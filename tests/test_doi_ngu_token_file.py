import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cong-cu'))


GIA = 'sk-ant-oat01-' + 'x' * 95  # 108 ký tự như token thật


def api():
    assert importlib.util.find_spec('doi_ngu_token'), 'Thiếu sổ tay token file'
    return importlib.import_module('doi_ngu_token')


def test_login_setup_token_an_stdin_khong_log(monkeypatch):
    m = api(); goi = []; log = []
    monkeypatch.setattr(m, 'can_tat', lambda c: None)
    monkeypatch.setattr(m.sys, 'stdin', SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(m.getpass, 'getpass', lambda prompt: GIA)
    class Gia:
        def tuong_tac(self, ten, argv):
            goi.append((ten, argv, {}))
        def goi(self, ten, argv, **kw):
            goi.append((ten, argv, kw))
            return SimpleNamespace(returncode=0, stdout='{"loggedIn":true}', stderr='')
        def ghi(self, *a): log.append(a)
    m.dang_nhap(Gia(), 1)
    assert goi[0][1][-1] == 'setup-token'
    ghi = next(x for x in goi if x[0] == 'ghi-token-khe')
    assert ghi[1][:5] == ['sudo', '-H', '-u', 'tram-khe1', m.PYTHON]
    assert ghi[2]['input'] == GIA and ghi[1][-1] == 'ghi'
    assert all(GIA not in str(x[1]) for x in goi)
    assert GIA not in str(log)
    assert goi[-1][1][-3:] == ['chay', 'auth', 'status']


@pytest.mark.parametrize('dan', [GIA[:80], 'oauth-gia-lap', GIA + ' x'])
def test_login_token_cut_hay_sai_dang_dung_truoc_khi_ghi(monkeypatch, dan):
    m = api(); goi = []
    monkeypatch.setattr(m, 'can_tat', lambda c: None)
    monkeypatch.setattr(m.sys, 'stdin', SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(m.getpass, 'getpass', lambda prompt: dan)
    c = SimpleNamespace(tuong_tac=lambda *a: None, goi=lambda ten, *a, **k: goi.append(ten))
    with pytest.raises(m.Dung, match='token-sai-dang') as e:
        m.dang_nhap(c, 1)
    assert goi == [] and dan not in str(e.value)


def test_login_khong_tty_khong_setup(monkeypatch):
    m = api(); monkeypatch.setattr(m, 'can_tat', lambda c: None)
    monkeypatch.setattr(m.sys, 'stdin', SimpleNamespace(isatty=lambda: False))
    with pytest.raises(m.Dung, match='Terminal'):
        m.dang_nhap(SimpleNamespace(), 1)


@pytest.mark.parametrize('ma, err, dat', [(1, 'Permission denied', True),
                                        (1, 'No such file or directory', False), (0, '', False), (127, '', False)])
def test_s6_chi_tu_choi_quyen_moi_dat(ma, err, dat):
    m = api(); da = []
    class Gia:
        def goi(self, ten, argv, **kw):
            da.append((ten, argv))
            return SimpleNamespace(returncode=ma if 'bi-chan' in ten else 0,
                                   stdout='', stderr=err)
    if dat:
        m.kiem_token_s6(Gia())
        am = [a for t, a in da if 'bi-chan' in t]
        assert len(am) == 6  # hai chiều chéo + hai quản lý→khe + hai khe→máy
        assert all('security' not in a and '-c' in a for a in am)
        assert all('.read(' not in a[a.index('-c') + 1] for a in am)
    else:
        with pytest.raises(m.Dung): m.kiem_token_s6(Gia())


def test_keychain_khong_con_la_buoc(monkeypatch):
    import doi_ngu_b as b
    monkeypatch.setattr(b.sys, 'argv', ['doi_ngu_b.py', 'keychain'])
    monkeypatch.setattr(b, 'Chay', lambda: pytest.fail('không được bắt đầu bước keychain'))
    assert b.main() == 2


def test_s6_tham_do_api_khong_preserve_env():
    # Máy B 21/10: s6 chạy dưới hungle; sudo của hungle không có SETENV → --preserve-env bị từ chối (rc 1).
    import doi_ngu_s6
    boc = doi_ngu_s6.boc_van_hanh("tram-khe1", {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
    argv = boc(["/usr/bin/curl", "-s", "http://127.0.0.1:7700"])
    assert argv[:5] == ["sudo", "-n", "-H", "-u", "tram-khe1"]
    assert not any(a.startswith("--preserve-env") for a in argv)
    assert argv[5:9] == ["/usr/bin/env", "-i", "PATH=/usr/bin:/bin", "LANG=C.UTF-8"]
    assert argv[-3:] == ["/usr/bin/curl", "-s", "http://127.0.0.1:7700"]


def test_s6_chay_tham_do_khong_tach_phien():
    # Máy B 21/10: khoi_chay đặt start_new_session → sudo -n mất vé tty của người vận hành → rc 1.
    import doi_ngu_s6
    goi = []
    def run(argv, **kw):
        goi.append(kw)
        return doi_ngu_s6.subprocess.CompletedProcess(argv, 0, "403", "")
    import unittest.mock as um
    with um.patch.object(doi_ngu_s6.subprocess, "run", run):
        kq = doi_ngu_s6.chay_van_hanh(["sudo", "-n", "x"], kill=None, capture_output=True, text=True,
                                     timeout=30, env={"PATH": "/usr/bin"})
    assert kq.stdout == "403" and "start_new_session" not in goi[0] and goi[0]["timeout"] == 30
