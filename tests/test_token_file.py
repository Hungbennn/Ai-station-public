import os
import stat
from pathlib import Path

import pytest


def api():
    import importlib.util
    assert importlib.util.find_spec('tram.tho.tep_token'), 'Thiếu kho token file an toàn'
    from tram.tho import tep_token
    return tep_token


def test_ghi_nguyen_tu_quyen_va_doc(tmp_path, monkeypatch):
    m = api()
    p = tmp_path / 'kin' / 'token'
    m.ghi(p, 'gia-lap-cu')
    inode = p.stat().st_ino
    cu = os.replace
    def replace(src, dst, **kw):
        s = os.stat(src, dir_fd=kw['src_dir_fd'], follow_symlinks=False)
        assert stat.S_IMODE(s.st_mode) == 0o600
        assert p.read_text() == 'gia-lap-cu'
        return cu(src, dst, **kw)
    monkeypatch.setattr(os, 'replace', replace)
    m.ghi(p, 'gia-lap-moi')
    assert m.doc(p) == 'gia-lap-moi' and p.stat().st_ino != inode
    assert p.stat().st_uid == os.geteuid()
    assert stat.S_IMODE(p.stat().st_mode) == 0o600
    assert stat.S_IMODE(p.parent.stat().st_mode) == 0o700
    assert list(p.parent.iterdir()) == [p]


@pytest.mark.parametrize('loi', ['symlink-file', 'symlink-cha', 'mode-file', 'mode-cha', 'hardlink', 'fifo', 'uid'])
def test_tu_choi_kho_khong_kin(tmp_path, monkeypatch, loi):
    m = api()
    p = tmp_path / 'kin' / 'token'
    m.ghi(p, 'gia-lap')
    if loi == 'symlink-file':
        p.rename(p.with_name('that')); p.symlink_to('that')
    elif loi == 'symlink-cha':
        p.parent.rename(tmp_path / 'that'); p.parent.symlink_to('that')
    elif loi == 'mode-file':
        p.chmod(0o644)
    elif loi == 'mode-cha':
        p.parent.chmod(0o755)
    elif loi == 'hardlink':
        os.link(p, p.with_name('khac'))
    elif loi == 'fifo':
        p.unlink(); os.mkfifo(p, 0o600)
    else:
        monkeypatch.setattr(os, 'geteuid', lambda: -1)
    with pytest.raises((OSError, ValueError)):
        m.doc(p)
    with pytest.raises((OSError, ValueError)):
        m.ghi(p, 'gia-lap-moi')


def test_loi_rename_giu_token_cu_va_don_tmp(tmp_path, monkeypatch):
    m = api(); p = tmp_path / 'kin/token'
    m.ghi(p, 'gia-lap-cu')
    def hong(*a, **kw):
        raise OSError('gia-lap')
    monkeypatch.setattr(os, 'replace', hong)
    with pytest.raises(OSError):
        m.ghi(p, 'gia-lap-moi')
    assert m.doc(p) == 'gia-lap-cu' and list(p.parent.iterdir()) == [p]


@pytest.mark.parametrize('token', ['', 'x\ny', 'x y', 'x' * 4097])
def test_khong_ghi_gia_tri_sai(tmp_path, token):
    m = api()
    with pytest.raises(ValueError):
        m.ghi(tmp_path / 'kin/token', token)
    assert not (tmp_path / 'kin').exists()
