"""Build the theme JAR using only the Python standard library."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
root = Path(__file__).resolve().parent
out = root / 'providers' / 'oqi-keycloak-21.1.jar'
out.parent.mkdir(exist_ok=True)
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for dirname, prefix in [('META-INF', 'META-INF'), ('themes', 'theme')]:
        source = root / dirname
        archive.write(source, prefix + '/')
        for path in sorted(source.rglob('*')):
            name = prefix + '/' + path.relative_to(source).as_posix()
            archive.write(path, name + ('/' if path.is_dir() else ''))
with ZipFile(out) as archive:
    assert 'theme/oqi/login/resources/' in archive.namelist()
    data = json.loads(archive.read('META-INF/keycloak-themes.json'))
    assert data == {'themes': [{'name': 'oqi', 'types': ['login']}]}
print(out)
