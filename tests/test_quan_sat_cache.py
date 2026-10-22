"""B5 19/10: stderr thật; metadata giả, không đọc /Library/Caches thật."""
import stat
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.quan_sat_kiem import tep_ngoai

LOI_THAT = (
    'find: /Library/Caches/com.apple.amsengagementd.classicdatavault: Operation not permitted\n'
    'find: /Library/Caches/com.apple.aneuserd: Operation not permitted\n'
    'find: /Library/Caches/com.apple.aned: Operation not permitted\n'
)


def gia(monkeypatch, *, mode=stat.S_IFDIR | 0o755, uid=0, mat=False):
    doc, cu = [], Path.lstat
    def lstat(p, *a, **kw):
        if str(p).startswith('/Library/Caches/'):
            doc.append(str(p))
            if mat:
                raise PermissionError('khong-doc-duoc')
            return SimpleNamespace(st_mode=mode, st_uid=uid)
        return cu(p, *a, **kw)
    monkeypatch.setattr(Path, 'lstat', lstat)
    return doc


def quet(stderr=LOI_THAT, ma=1, stdout=''):
    tep_ngoai('tram-kiem', Path('/Users/Shared/tram-kiem'),
              chay=lambda a, **kw: subprocess.CompletedProcess(a, ma, stdout, stderr))


def test_ba_thu_muc_apple_bi_khoa_thuc_te_duoc_bo_qua(monkeypatch):
    doc = gia(monkeypatch)
    quet()
    assert doc == [dong[6:-25] for dong in LOI_THAT.splitlines()]


@pytest.mark.parametrize('loi', [
    LOI_THAT.replace('/Library/Caches/', '/Users/Shared/'),
    LOI_THAT.replace('com.apple.aned', 'ben.aned'),
    LOI_THAT.replace('com.apple.aned', 'com.apple.aned/con'),
    LOI_THAT.replace('com.apple.aned', 'com.apple.aned/../khac'),
    LOI_THAT.replace('Operation not permitted', 'Permission denied'),
    LOI_THAT + 'find: loi khac\n', LOI_THAT + '\n', '',
])
def test_stderr_khac_van_dong(monkeypatch, loi):
    gia(monkeypatch)
    with pytest.raises(LoiBanChep):
        quet(loi)


@pytest.mark.parametrize('doi', [dict(mode=stat.S_IFDIR | 0o775), dict(mode=stat.S_IFDIR | 0o757),
    dict(mode=stat.S_IFLNK | 0o755), dict(mode=stat.S_IFREG | 0o644), dict(uid=503), dict(mat=True)])
def test_metadata_khong_chung_minh_duoc_thi_dong(monkeypatch, doi):
    gia(monkeypatch, **doi)
    with pytest.raises(LoiBanChep):
        quet()


@pytest.mark.parametrize('ma,stdout', [(2, ''), (-9, ''), (0, ''), (1, '\n'), (1, 'la'),
                                       (1, '/Users/Shared/sot\n')])
def test_ma_loi_va_stdout_khong_duoc_bo_qua(monkeypatch, ma, stdout):
    gia(monkeypatch)
    with pytest.raises(LoiBanChep):
        quet(ma=ma, stdout=stdout)


@pytest.mark.parametrize('ma_errno,dat', [('EPERM', True), ('EACCES', False)])
def test_data_vault_lstat_eperm_that(monkeypatch, ma_errno, dat):
    """Đo 20/10 dưới 501 và Uq: lstat 3 thư mục này trả EPERM (data vault SIP); ACL chặn thì ra EACCES — không nhận."""
    import errno
    cu = Path.lstat
    def lstat(p, *a, **kw):
        if str(p).startswith('/Library/Caches/'):
            e = getattr(errno, ma_errno)
            raise PermissionError(e, 'Operation not permitted')
        return cu(p, *a, **kw)
    monkeypatch.setattr(Path, 'lstat', lstat)
    if dat:
        quet()
    else:
        with pytest.raises(LoiBanChep):
            quet()
