"""Tiến trình con mo/don/luot để lại một dòng lý do trong daemon.log (B5 20/10: stderr con là DEVNULL)."""
import os
import sys

import pytest

from tram.quan_kiem import chay


def test_con_mo_ghi_ly_do_roi_van_nem(tmp_path, monkeypatch):
    monkeypatch.setattr(chay, 'nap', lambda: {'uid_quan': os.getuid(), 'home': str(tmp_path)})
    monkeypatch.setattr(sys, 'argv', ['chay.py', 'mo', '0' * 32])
    import tram.quan_kiem.cong as cong

    def hong(c, mode, id_):
        raise OSError('không dọn được DARWIN_USER_DIR ' + 'x' * 400)
    monkeypatch.setattr(cong, 'phuc_hoi', hong)
    with pytest.raises(OSError):
        chay.main()
    dong = (tmp_path / 'daemon.log').read_text().splitlines()
    assert len(dong) == 1 and dong[0].startswith('con mo: OSError: không dọn được DARWIN_USER_DIR')
    assert len(dong[0]) < 340


def test_lenh_con_loi_ghi_lenh_that_va_stderr(tmp_path, monkeypatch):
    import subprocess
    monkeypatch.setattr(chay, 'nap', lambda: {'uid_quan': os.getuid(), 'home': str(tmp_path)})
    monkeypatch.setattr(sys, 'argv', ['chay.py', 'mo', '0' * 32])
    import tram.quan_kiem.cong as cong
    cmd = ['/usr/bin/sudo', '-n', '-u', 'tram-kiem', '/usr/bin/sandbox-exec', '-f', 'x.sb', '/usr/bin/env',
           'HOME=/n', 'PATH=/p', '/bin/mkdir', '/Users/Shared/tram-kiem/luot-1']

    def hong(c, mode, id_):
        raise subprocess.CalledProcessError(1, cmd, b'', b'mkdir: Operation not permitted\n')
    monkeypatch.setattr(cong, 'phuc_hoi', hong)
    with pytest.raises(subprocess.CalledProcessError):
        chay.main()
    d = (tmp_path / 'daemon.log').read_text()
    assert '| lenh: /bin/mkdir /Users/Shared/tram-kiem/luot-1 |' in d and 'Operation not permitted' in d
    assert 'HOME=' not in d


def test_argv_tu_chay_gioi_han_duoc_dung(tmp_path, monkeypatch):
    import subprocess
    monkeypatch.setattr(chay, 'nap', lambda: {'uid_quan': os.getuid(), 'home': str(tmp_path)})
    monkeypatch.setattr(sys, 'argv', ['chay.py', 'mo', '0' * 32])
    import tram.quan_kiem.cong as cong

    def hong(c, mode, id_):
        e = subprocess.CalledProcessError(1, ['sudo'], b'', b'git: loi that\n')
        e.argv = ['sudo', '-n', '/usr/bin/env', 'HOME=/n', '/usr/bin/git', 'init']
        raise e
    monkeypatch.setattr(cong, 'phuc_hoi', hong)
    with pytest.raises(subprocess.CalledProcessError):
        chay.main()
    d = (tmp_path / 'daemon.log').read_text()
    assert '| lenh: /usr/bin/git init |' in d and 'git: loi that' in d and 'HOME=' not in d
