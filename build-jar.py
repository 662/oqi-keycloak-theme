"""Build a reproducible theme JAR using only the Python standard library."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
from scripts.theme_lib import write_tree

root = Path(__file__).resolve().parent
out = root / 'providers' / 'oqi-keycloak-21.1.jar'
out.parent.mkdir(exist_ok=True)
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for dirname, prefix in [('META-INF', 'META-INF'), ('themes', 'theme')]:
        write_tree(archive, root / dirname, prefix)
with ZipFile(out) as archive:
    assert 'theme/oqi/login/resources/' in archive.namelist()
    data = json.loads(archive.read('META-INF/keycloak-themes.json'))
    assert data == {'themes': [{'name': 'oqi', 'types': ['login']}]}
    assert archive.testzip() is None
print(out)
