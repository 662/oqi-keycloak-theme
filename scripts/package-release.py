"""Build verified, reproducible install archives from the checked-out Git source."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import os
import shutil
import subprocess
import sys
from theme_lib import version, check_tag, write_entry

root = Path(__file__).resolve().parents[1]
release_version = version(root)
tag = os.environ.get('RELEASE_TAG', '')
if tag:
    check_tag(tag, release_version)
dist = root / 'dist'
dist.mkdir(exist_ok=True)
source_jar = root / 'providers/oqi-keycloak-21.1.jar'
build_command = [sys.executable, str(root / 'build-jar.py')]
subprocess.run(build_command, cwd=root, check=True)
first = source_jar.read_bytes()
subprocess.run(build_command, cwd=root, check=True)
if first != source_jar.read_bytes():
    raise ValueError('Building the same sources twice did not produce identical JARs')
with ZipFile(source_jar) as archive:
    if archive.testzip() is not None:
        raise ValueError('Corrupt JAR')
    if 'theme/oqi/login/resources/' not in archive.namelist():
        raise ValueError('JAR is missing explicit class-loader resource directories')
    for file in (root / 'themes/oqi').rglob('*'):
        if file.is_file() and archive.read('theme/oqi/' + file.relative_to(root / 'themes/oqi').as_posix()) != file.read_bytes():
            raise ValueError('JAR/source mismatch: ' + str(file))

tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
tracked = sorted(name for name in tracked if name)
jar = dist / source_jar.name
shutil.copyfile(source_jar, jar)
prefix = f'oqi-keycloak-theme-v{release_version}/'
zip_path = dist / 'oqi-keycloak-21.1.zip'
with ZipFile(zip_path, 'w', ZIP_DEFLATED) as archive:
    write_entry(archive, prefix, directory=True)
    for name in tracked:
        if name.startswith(('.git/', 'dist/', 'providers/')) or name.endswith(('.jar', '.zip', '.class', '.pyc')) or Path(name).name.startswith('.env'):
            raise ValueError('Unexpected generated/private file tracked by Git: ' + name)
        file = root / name
        if file.is_symlink():
            raise ValueError('Release source contains a symlink: ' + name)
        write_entry(archive, prefix + name, file.read_bytes())
    write_entry(archive, prefix + 'providers/' + jar.name, jar.read_bytes())
with ZipFile(zip_path) as archive:
    if archive.testzip() is not None:
        raise ValueError('Corrupt ZIP')
checksums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [jar, zip_path]}
(dist / 'SHA256SUMS.txt').write_text(''.join(value + '  ' + name + '\n' for name, value in sorted(checksums.items())))
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
(dist / 'build-info.json').write_text(json.dumps({'version': release_version, 'commit': commit}, indent=2) + '\n')
changelog = (root / 'CHANGELOG.md').read_text()
notes = changelog.split('\n## ' + release_version + '\n', 1)[1].split('\n## ', 1)[0].strip()
(dist / 'RELEASE_NOTES.md').write_text(notes + '\n\nKeycloak 21.1.x theme; runtime validation baseline: 21.1.2. See README and VALIDATION.md for installation and compatibility scope.\n')
print(f'Built ZIP/JAR, SHA256 checksums and provenance for v{release_version} at {commit}.')
