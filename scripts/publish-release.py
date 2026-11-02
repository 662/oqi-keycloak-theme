"""Publish only verified tag builds; never overwrite an already published release."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
from urllib.parse import quote
from theme_lib import check_tag

parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true', help='Validate artifacts without calling GitHub')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
dist = root / 'dist'
info = json.loads((dist / 'build-info.json').read_text())
tag = os.environ.get('RELEASE_TAG', 'v' + info['version'] if args.dry_run else '')
check_tag(tag, info['version'])
if not re.fullmatch(r'[0-9a-f]{40}', info['commit']):
    raise ValueError('Build provenance must contain a full Git commit SHA')
if os.environ.get('GITHUB_SHA', info['commit']) != info['commit']:
    raise ValueError('Build artifacts do not match this workflow commit')
expected = {}
for line in (dist / 'SHA256SUMS.txt').read_text().splitlines():
    digest, name = line.split('  ', 1)
    if name not in ['oqi-keycloak-21.1.jar', 'oqi-keycloak-21.1.zip'] or name in expected:
        raise ValueError('Unexpected or duplicate checksum entry')
    file = dist / name
    if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise ValueError('Artifact checksum mismatch: ' + name)
    expected[name] = digest
if set(expected) != {'oqi-keycloak-21.1.jar', 'oqi-keycloak-21.1.zip'}:
    raise ValueError('Both ZIP and JAR must be present')
expected['SHA256SUMS.txt'] = hashlib.sha256((dist / 'SHA256SUMS.txt').read_bytes()).hexdigest()
if args.dry_run:
    print(f'Dry run passed for {tag}: provenance and three release assets verified. No GitHub writes.')
    raise SystemExit(0)

repo = os.environ['GH_REPO']
if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
    raise ValueError('Invalid GitHub repository')


def api(path, missing_ok=False):
    result = subprocess.run(['gh', 'api', path], text=True, capture_output=True)
    if result.returncode:
        try:
            missing = json.loads(result.stdout).get('status') == '404'
        except (ValueError, AttributeError):
            missing = False
        if missing_ok and missing:
            return None
        raise RuntimeError('GitHub API request failed: ' + result.stderr.strip())
    return json.loads(result.stdout)


def gh(*arguments):
    subprocess.run(['gh', *arguments], cwd=root, check=True)


def verify_assets(release):
    assets = {item['name']: item for item in release['assets']}
    for name, digest in expected.items():
        asset = assets.get(name)
        if not asset or asset['state'] != 'uploaded' or asset['size'] != (dist / name).stat().st_size or asset.get('digest') != 'sha256:' + digest:
            raise ValueError('GitHub asset failed verification: ' + name)


ref = api('repos/' + repo + '/git/ref/tags/' + quote(tag, safe=''))['object']
while ref['type'] == 'tag':
    ref = api('repos/' + repo + '/git/tags/' + ref['sha'])['object']
if ref['type'] != 'commit' or ref['sha'] != info['commit']:
    raise ValueError('Remote tag does not match the built commit')
release_path = 'repos/' + repo + '/releases/tags/' + quote(tag, safe='')
release = api(release_path, missing_ok=True)
if release and not release['draft']:
    verify_assets(release)
    print('Release already published with identical assets; leaving it unchanged: ' + release['html_url'])
    raise SystemExit(0)
if not release:
    arguments = ['release', 'create', tag, '--repo', repo, '--verify-tag', '--draft', '--title', 'OQI.ME ' + tag, '--notes-file', str(dist / 'RELEASE_NOTES.md')]
    if '-' in info['version']:
        arguments.append('--prerelease')
    gh(*arguments)
# Drafts can be resumed after interrupted uploads. Published releases are never clobbered.
gh('release', 'upload', tag, *[str(dist / name) for name in expected], '--repo', repo, '--clobber')
verify_assets(api(release_path))
gh('release', 'edit', tag, '--repo', repo, '--draft=false')
print('Published verified release: ' + api(release_path)['html_url'])
