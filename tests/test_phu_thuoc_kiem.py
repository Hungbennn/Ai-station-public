"""Bundle không được thành đường đưa mã dự án/chạy cài gói dưới Uq/root."""
import copy
import io
import json
import tarfile

import pytest

from tram.kiem.deps_manifest import (KHOA_NGUON, bam, kiem_manifest, ma_bundle, nen_tang)
from tram.kiem.deps_tar import giai_nen


def archive(entries):
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w') as t:
        for name, kind, value in entries:
            m = tarfile.TarInfo(name)
            m.mode = 0o755 if kind == 'dir' else 0o644
            if kind == 'link':
                m.type, m.linkname = tarfile.SYMTYPE, value
            elif kind == 'hard':
                m.type, m.linkname = tarfile.LNKTYPE, value
            elif kind == 'dir':
                m.type = tarfile.DIRTYPE
            else:
                m.size = len(value)
            t.addfile(m, io.BytesIO(value) if kind == 'file' else None)
    return b.getvalue()


def mau():
    from tram.kiem.toolchain import PYTHON
    return {'v': 1, 'du_an': 'ben-station', 'commit': 'a' * 40,
            'nguon': {k: bam(k.encode()) for k in KHOA_NGUON},
            'runtime': nen_tang() | {'python': PYTHON, 'build': '20261009', 'version': '3.12.15'},
            'cong_cu': {'uv': '0.13.0', 'node': '26.5.0', 'npm': '11.15.0'},
            'python_groups': ['dev'],
            'npm_flags': ['--ignore-scripts', '--include=dev', '--no-audit', '--no-fund'],
            'artifacts': {k: {'sha256': 'b' * 64, 'size': 10240, 'bytes': 1, 'entries': 1}
                          for k in ('python-site.tar', 'node-modules.tar')}}


def test_manifest_khoa_du_bon_tep_va_fingerprint():
    m = mau()
    assert kiem_manifest(m) == m
    other = copy.deepcopy(m)
    other['nguon']['pyproject.toml'] = 'f' * 64
    assert ma_bundle(m) != ma_bundle(other)
    assert ma_bundle(json.loads(json.dumps(m, sort_keys=True))) == ma_bundle(m)


def test_manifest_khong_khoa_trung():
    from tram.kiem.deps_manifest import doc_manifest
    with pytest.raises(ValueError):
        doc_manifest(b'{"v":1,"v":1}')


@pytest.mark.parametrize('doi', [lambda m: m.update(v=2), lambda m: m.update(extra=1),
    lambda m: m['nguon'].pop('uv.lock'), lambda m: m['runtime'].update(python='/tmp/python'),
    lambda m: m['artifacts']['python-site.tar'].update(bytes=1024**3 + 1),
    lambda m: m['artifacts']['node-modules.tar'].update(entries=100001),
    lambda m: m['artifacts']['python-site.tar'].update(size=True),
    lambda m: m['artifacts']['python-site.tar'].update(sha256='../x')])
def test_manifest_sai_dong_cong(doi):
    m = mau()
    doi(m)
    with pytest.raises(ValueError):
        kiem_manifest(m)


def test_npm_link_cham_cham_noi_bo_va_hai_luot_rieng(tmp_path):
    data = archive([('vite', 'dir', ''), ('vite/bin.js', 'file', b'x'),
                    ('.bin', 'dir', ''), ('.bin/vite', 'link', '../vite/bin.js')])
    for n in ('mot', 'hai'):
        root = tmp_path / n
        root.mkdir()
        assert giai_nen(io.BytesIO(data), root, 1, 4) == (1, 4)
        assert (root / '.bin/vite').read_bytes() == b'x'
        if n == 'mot':
            (root / 'vite/bin.js').write_bytes(b'changed')
    assert (tmp_path / 'hai/vite/bin.js').read_bytes() == b'x'


@pytest.mark.parametrize('entries', [
    [('../x', 'file', b'x')], [('/x', 'file', b'x')], [('x', 'hard', 'y')],
    [('x', 'link', '/tmp/x')], [('x', 'link', '../x')],
    [('x', 'file', b'x'), ('x', 'file', b'x')],
    [('x', 'link', 'y'), ('x/a', 'file', b'x')],
    [('x', 'link', 'y'), ('y', 'link', 'x')],
])
def test_artifact_tu_choi_link_thoat_va_ghi_de(tmp_path, entries):
    with pytest.raises(ValueError):
        giai_nen(io.BytesIO(archive(entries)), tmp_path, 100, 20)
    assert not (tmp_path.parent / 'x').exists()


@pytest.mark.parametrize('size,count', [(0, 1), (1, 0), (2, 1), (1, 2)])
def test_artifact_gioi_han_va_doi_chieu_so_do(tmp_path, size, count):
    with pytest.raises(ValueError):
        giai_nen(io.BytesIO(archive([('x', 'file', b'x')])), tmp_path, size, count)
