"""Exercise release failure/retry paths without network access or GitHub writes."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from theme_lib import check_tag


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        shutil.copyfile(ROOT / 'scripts/publish-release.py', self.root / 'scripts/publish-release.py')
        self.dist = self.root / 'dist'
        self.dist.mkdir()
        self.expected = {}
        for name, data in [('oqi-keycloak-21.1.jar', b'test-jar'), ('oqi-keycloak-21.1.zip', b'test-zip')]:
            (self.dist / name).write_bytes(data)
            self.expected[name] = hashlib.sha256(data).hexdigest()
        checksums = ''.join(value + '  ' + name + '\n' for name, value in self.expected.items()).encode()
        (self.dist / 'SHA256SUMS.txt').write_bytes(checksums)
        self.expected['SHA256SUMS.txt'] = hashlib.sha256(checksums).hexdigest()
        (self.dist / 'build-info.json').write_text(json.dumps({'version': '1.1.0', 'commit': 'a' * 40}))
        (self.dist / 'RELEASE_NOTES.md').write_text('Test release')
        self.env = {'RELEASE_TAG': 'v1.1.0', 'GH_REPO': 'example/theme', 'GITHUB_SHA': 'a' * 40}
        self.release = None
        self.writes = []
        self.remote_commit = 'a' * 40
        self.api_error = False
        self.fail_upload = False
        self.tamper_upload = False

    def assets(self):
        return [{'name': name, 'size': (self.dist / name).stat().st_size, 'state': 'uploaded', 'digest': 'sha256:' + digest} for name, digest in self.expected.items()]

    def mock_gh(self, argv, **kwargs):
        self.assertEqual(argv[0], 'gh')
        if argv[1] == 'api':
            if self.api_error:
                return subprocess.CompletedProcess(argv, 1, json.dumps({'status': '403'}), 'Forbidden')
            if '/git/ref/tags/' in argv[2]:
                body = {'object': {'type': 'commit', 'sha': self.remote_commit}}
            elif self.release is not None:
                body = self.release
            else:
                return subprocess.CompletedProcess(argv, 1, json.dumps({'status': '404'}), 'Not Found')
            return subprocess.CompletedProcess(argv, 0, json.dumps(body), '')
        action = argv[2]
        self.writes.append(action)
        if action == 'create':
            self.assertIn('--draft', argv)
            self.assertIn('--verify-tag', argv)
            self.release = {'draft': True, 'html_url': 'https://example.test/release', 'assets': []}
        elif action == 'upload':
            if self.fail_upload:
                raise subprocess.CalledProcessError(1, argv)
            self.assertTrue(self.release['draft'])
            self.release['assets'] = self.assets()
            if self.tamper_upload:
                self.release['assets'][0]['digest'] = 'sha256:' + '0' * 64
        elif action == 'edit':
            self.assertIn('--draft=false', argv)
            self.release['draft'] = False
        else:
            self.fail('Unexpected GitHub command')
        return subprocess.CompletedProcess(argv, 0)

    def execute(self, dry=False):
        argv = ['publish-release.py'] + (['--dry-run'] if dry else [])
        with patch.dict('os.environ', self.env, clear=True), patch.object(sys, 'argv', argv), patch('subprocess.run', side_effect=self.mock_gh), contextlib.redirect_stdout(io.StringIO()):
            try:
                runpy.run_path(str(self.root / 'scripts/publish-release.py'), run_name='__main__')
            except SystemExit as error:
                if error.code != 0:
                    raise

    def test_new_release_is_verified_before_publication(self):
        self.execute()
        self.assertEqual(self.writes, ['create', 'upload', 'edit'])
        self.assertFalse(self.release['draft'])

    def test_draft_can_resume_after_interruption(self):
        self.release = {'draft': True, 'html_url': 'https://example.test/release', 'assets': []}
        self.execute()
        self.assertEqual(self.writes, ['upload', 'edit'])

    def test_identical_published_release_is_not_modified(self):
        self.release = {'draft': False, 'html_url': 'https://example.test/release', 'assets': self.assets()}
        self.execute()
        self.assertEqual(self.writes, [])

    def test_different_published_assets_are_never_overwritten(self):
        self.release = {'draft': False, 'html_url': 'https://example.test/release', 'assets': []}
        with self.assertRaisesRegex(ValueError, 'asset failed'):
            self.execute()
        self.assertEqual(self.writes, [])

    def test_tag_mismatch_makes_no_github_writes(self):
        self.env['RELEASE_TAG'] = 'v9.9.9'
        with self.assertRaisesRegex(ValueError, 'must match'):
            self.execute()
        self.assertEqual(self.writes, [])

    def test_workflow_commit_mismatch_is_rejected(self):
        self.env['GITHUB_SHA'] = 'b' * 40
        with self.assertRaisesRegex(ValueError, 'workflow commit'):
            self.execute()
        self.assertEqual(self.writes, [])

    def test_moved_remote_tag_is_rejected(self):
        self.remote_commit = 'b' * 40
        with self.assertRaisesRegex(ValueError, 'Remote tag'):
            self.execute()
        self.assertEqual(self.writes, [])

    def test_corrupt_local_artifact_is_rejected(self):
        (self.dist / 'oqi-keycloak-21.1.jar').write_bytes(b'corrupted')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            self.execute()
        self.assertEqual(self.writes, [])

    def test_upload_failure_keeps_draft_unpublished(self):
        self.fail_upload = True
        with self.assertRaises(subprocess.CalledProcessError):
            self.execute()
        self.assertEqual(self.writes, ['create', 'upload'])
        self.assertTrue(self.release['draft'])

    def test_remote_digest_failure_keeps_draft_unpublished(self):
        self.tamper_upload = True
        with self.assertRaisesRegex(ValueError, 'asset failed'):
            self.execute()
        self.assertEqual(self.writes, ['create', 'upload'])
        self.assertTrue(self.release['draft'])

    def test_api_auth_failure_is_not_treated_as_missing_release(self):
        self.api_error = True
        with self.assertRaises(RuntimeError):
            self.execute()
        self.assertEqual(self.writes, [])

    def test_dry_run_never_calls_github(self):
        self.api_error = True
        self.execute(dry=True)
        self.assertEqual(self.writes, [])

    def test_prerelease_tag_is_exact(self):
        check_tag('v1.2.0-rc.1', '1.2.0-rc.1')
        with self.assertRaises(ValueError):
            check_tag('v1.2.0', '1.2.0-rc.1')


if __name__ == '__main__':
    unittest.main()
