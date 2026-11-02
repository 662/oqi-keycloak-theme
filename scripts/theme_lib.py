"""Shared, dependency-free helpers for theme packaging."""
from pathlib import Path
import re
from zipfile import ZipInfo, ZIP_DEFLATED

VERSION_RE = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?")


def version(root):
    text = (root / 'META-INF/MANIFEST.MF').read_text(encoding='utf-8')
    found = re.findall(r'^Implementation-Version: (.+)$', text, re.MULTILINE)
    if len(found) != 1 or not VERSION_RE.fullmatch(found[0]):
        raise ValueError('Manifest must contain exactly one valid release version')
    return found[0]


def check_tag(tag, expected):
    if tag != 'v' + expected:
        raise ValueError(f'Tag {tag!r} must match manifest version v{expected}')


def write_entry(archive, name, data=b'', directory=False):
    """Fixed timestamps and permissions produce reproducible ZIP/JAR bytes."""
    if name.startswith('/') or '..' in Path(name).parts:
        raise ValueError('Unsafe archive path: ' + name)
    if directory and not name.endswith('/'):
        name += '/'
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = (0o40755 if directory else 0o100644) << 16
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, data)


def write_tree(archive, source, prefix):
    write_entry(archive, prefix, directory=True)
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlinks are not supported in theme sources: ' + str(path))
        name = prefix + '/' + path.relative_to(source).as_posix()
        write_entry(archive, name, b'' if path.is_dir() else path.read_bytes(), path.is_dir())
