import io
import tarfile
import pytest
from tram.quan_kiem.nhan import giai_nen


def tar(ten, kind=tarfile.REGTYPE, link=''):
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w') as f:
        t = tarfile.TarInfo(ten)
        t.type, t.linkname = kind, link
        t.size = 1 if kind == tarfile.REGTYPE else 0
        f.addfile(t, io.BytesIO(b'x') if t.size else None)
    return b.getvalue()


def test_nhan_file_binh_thuong(tmp_path):
    giai_nen(io.BytesIO(tar('a')), tmp_path)
    assert (tmp_path / 'a').read_bytes() == b'x'


@pytest.mark.parametrize('ten,kind,link', [('../a', tarfile.REGTYPE, ''),
    ('/tmp/a', tarfile.REGTYPE, ''), ('.git/config', tarfile.REGTYPE, ''),
    ('a', tarfile.SYMTYPE, '/tmp'), ('a', tarfile.LNKTYPE, '../x'), ('dev', tarfile.CHRTYPE, '')])
def test_nguon_khong_thoat_cay(tmp_path, ten, kind, link):
    with pytest.raises(ValueError):
        giai_nen(io.BytesIO(tar(ten, kind, link)), tmp_path)
    assert list(tmp_path.iterdir()) == []
