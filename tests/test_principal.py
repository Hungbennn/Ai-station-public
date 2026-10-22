"""Principal thực thi (spec 3 §7.3) — chỉ kiểm argv/hồ sơ sinh ra; test KHÔNG chạy sudo, sandbox-exec hay tạo user."""
import signal
from pathlib import Path

import pytest

from tram.tho.principal import BIEN_GIU, ChuaCoPrincipal, Principal, doc_principal
from tram.tho.sandbox import ghi_ho_so, ho_so_sandbox


def test_user_moi_khe_boc_qua_sudo_khong_hoi_mat_khau():
    p = doc_principal("user:tram-k-b-claude-1")
    a = p.boc(["claude", "-p"])
    assert a[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-b-claude-1"] and a[-3:] == ["--", "claude", "-p"]
    giu = a[5].removeprefix("--preserve-env=").split(",")
    assert set(giu) == set(BIEN_GIU) and "TRAM_THO_TOKEN" not in giu and all("=" not in x for x in giu)


def test_sandbox_can_ho_so_cua_lan_chay(tmp_path):
    p = doc_principal("sandbox:tram-thuc-thi")
    with pytest.raises(ChuaCoPrincipal):
        p.boc(["claude"])
    a = p.voi_ho_so(tmp_path / "hs.sb").boc(["claude"])
    assert a[a.index("--") + 1:] == ["/usr/bin/sandbox-exec", "-f", str(tmp_path / "hs.sb"), "claude"]


@pytest.mark.parametrize("chuoi", [None, "", "tram-k", "root:x", "user:", "user:Tram", "user:a b", "user:../x"])
def test_principal_sai_dang(chuoi):
    with pytest.raises(ChuaCoPrincipal):
        doc_principal(chuoi)


def test_ho_so_sandbox_cam_truoc_mo_sau(tmp_path):
    s = ho_so_sandbox(cam=[Path("/Users/tram/.tram")], cam_ghi=[Path("/Users/tram-tho/tram/worktrees")],
                      cho_ghi=[Path("/Users/tram-tho/tram/worktrees/hr/hr-1")], cong_cam=[7700, 3306])
    dong = s.splitlines()
    assert dong[:2] == ["(version 1)", "(allow default)"]
    assert dong.index('(deny file-write* (subpath "/Users/tram-tho/tram/worktrees"))') < dong.index(
        '(allow file-read* file-write* (subpath "/Users/tram-tho/tram/worktrees/hr/hr-1"))')
    assert '(deny network-outbound (remote tcp "*:7700"))' in dong and "com.apple.SecurityServer" in s
    p = ghi_ho_so(tmp_path / "x" / "hs.sb", s)
    assert p.read_text() == s and oct(p.stat().st_mode)[-3:] == "644"


@pytest.mark.parametrize("cam, cong", [([Path('/a"b')], []), ([Path("tuong-doi")], []), ([], [0]), ([], [70000])])
def test_ho_so_tu_choi_dau_vao_nguy_hiem(cam, cong):
    with pytest.raises(ValueError):
        ho_so_sandbox(cam=cam, cam_ghi=[], cho_ghi=[], cong_cam=cong)


def test_principal_kill_nhom_chay_kill_duoi_quyen_principal(monkeypatch):
    goi = []
    monkeypatch.setattr("tram.tho.principal.chay_ngan", lambda argv, **kw: goi.append((argv, kw)))
    doc_principal("user:tram-k-b-claude-1").kill_nhom(4321, signal.SIGTERM)
    assert goi == [(["/usr/bin/sudo", "-n", "-u", "tram-k-b-claude-1", "/bin/kill", "-s", "TERM", "--", "-4321"],
                    {"timeout": 5})]


def test_lenh_kiem_kill_qua_ham_cua_principal(tmp_path):
    import os
    import sys

    from tram.kiem.chay_lenh import chay_mot_lenh
    da = []

    def kill(pgid, sig):
        da.append(sig)
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            pass
    ma = "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)"
    kq = chay_mot_lenh("ngu", [sys.executable, "-c", ma], cwd=tmp_path,
                       env=dict(os.environ), log=tmp_path / "l.log", thoi_gian_cho=0.3, boc=lambda a: a, cho_kill=1,
                       kill=kill)
    assert kq.het_gio and kq.ket_qua == "fail" and da[:2] == [signal.SIGTERM, signal.SIGKILL]
