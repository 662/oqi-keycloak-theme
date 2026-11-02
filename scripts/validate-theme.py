"""Validate contracts between the theme registry, templates, messages and assets."""
from pathlib import Path
import json
import re
from theme_lib import version

root = Path(__file__).resolve().parents[1]
theme = root / 'themes/oqi/login'
registry = json.loads((root / 'META-INF/keycloak-themes.json').read_text())
if registry != {'themes': [{'name': 'oqi', 'types': ['login']}]}:
    raise ValueError('Unexpected theme registration')


def properties(path):
    result = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith(('#', '!')):
            continue
        key, sep, value = line.partition('=')
        if not sep or key in result:
            raise ValueError('Malformed or duplicate key in ' + str(path) + ': ' + key)
        result[key] = value
    return result


props = properties(theme / 'theme.properties')
if props.get('parent') != 'keycloak' or props.get('import') != 'common/keycloak':
    raise ValueError('The native Keycloak inheritance contract changed')
for key in ['styles', 'scripts']:
    for resource in props[key].split():
        if not (theme / 'resources' / resource).is_file():
            raise ValueError('Missing resource: ' + resource)

templates = list(theme.glob('*.ftl'))
text = '\n'.join(p.read_text(encoding='utf-8') for p in templates)
custom_keys = set(re.findall(r'''msg\(['"](oqi\w+)['"]''', text))
for file in sorted((theme / 'messages').glob('*.properties')):
    if not file.read_text(encoding='utf-8').startswith('# encoding: UTF-8'):
        raise ValueError('Missing UTF-8 header: ' + file.name)
    values = properties(file)
    if missing := custom_keys - values.keys():
        raise ValueError(file.name + ': missing keys ' + str(sorted(missing)))
    # Brand messages must have matching runtime placeholders across languages.
    if file.name == 'messages_en.properties':
        english = values
for file in (theme / 'messages').glob('*.properties'):
    values = properties(file)
    for key in custom_keys:
        if set(re.findall(r'\{\d+\}', english[key])) != set(re.findall(r'\{\d+\}', values[key])):
            raise ValueError('Translation placeholder mismatch: ' + key)
for resource in re.findall(r'\$\{url.resourcesPath\}/([^"\s$<>]+)', text):
    if not (theme / 'resources' / resource).is_file():
        raise ValueError('Missing template image/resource: ' + resource)
for css in (theme / 'resources/css').glob('*.css'):
    for resource in re.findall(r'''url\(['"]?(\.\./[^)'"\s]+)''', css.read_text()):
        if not (css.parent / resource).is_file():
            raise ValueError('Missing CSS image/resource: ' + resource)
for name in ['login.ftl', 'login-username.ftl', 'login-password.ftl']:
    content = (theme / name).read_text()
    if 'action="${url.loginAction}"' not in content or 'method="post"' not in content:
        raise ValueError('Native login POST contract missing: ' + name)
release_version = version(root)
if '\n## ' + release_version + '\n' not in (root / 'CHANGELOG.md').read_text():
    raise ValueError('Add a changelog entry for ' + release_version)
print(f'Validated {len(templates)} templates, bilingual messages, resource references and version {release_version}.')
