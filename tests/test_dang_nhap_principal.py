"""bs-863.17: trạng thái đăng nhập CLI dò DƯỚI principal của khe — argv qua `boc`, `kill` của principal, env dựng mới
chỉ PATH/LANG/<thư mục cấu hình> (không HOME/token của quản lý); chưa có principal hay UID chưa chứng minh → không spawn
lệnh đăng nhập nào. Lỗi hạ tầng không thành "đã đăng nhập". Không sudo/CLI thật: chạy và xác minh UID đều GIẢ."""
import subprocess
from datetime import datetime, timezone

import pytest

from test_kiem_3b import _ch, _dd, _hm
from test_kiem_cong import cau_hinh
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.do_may import dang_nhap_codex, do_cli
from tram.tho.kiem_3b import bo_sung_3b
from tram.tho.kiem_cong import dang_nhap
from tram.tho.principal import Principal

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
PR = Principal("user", "tram-k-c-codex-1")


def chay_gia(goi, ket=0):
    def chay(argv, **kw):
        goi.append((argv, kw))
        if isinstance(ket, BaseException):
            raise ket
        return subprocess.CompletedProcess(argv, ket, '{"loggedIn":true}\n' if "auth" in argv else "Logged in as ai@x\n", "")
    return chay


def test_do_cli_chi_doc_phien_ban_khong_do_dang_nhap_duoi_quan_ly(tmp_path):
    goi = []
    kq = do_cli("codex", tmp_path, which=lambda c: "/opt/bin/codex", chay=chay_gia(goi))
    assert [a for a, _ in goi] == [["/opt/bin/codex", "--version"]] and kq.dang_nhap is None
    assert "principal" in kq.chi_tiet


def test_dang_nhap_codex_duoi_principal_env_moi_kill_cua_principal(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", "/Users/quan-ly")
    monkeypatch.setenv("TRAM_THO_TOKEN", "BI-MAT")
    goi = []
    assert dang_nhap_codex(PR, "/opt/bin/codex", tmp_path / "k1", path="/x/bin", chay=chay_gia(goi))[0] is True
    argv, kw = goi[0]
    assert argv == PR.boc(["/opt/bin/codex", "login", "status"]) and kw["kill"] == PR.kill_nhom
    assert kw["env"] == {"PATH": "/x/bin", "LANG": "C.UTF-8", "CODEX_HOME": str(tmp_path / "k1")}
    assert kw["timeout"] == 20
    co, ct = dang_nhap_codex(PR, "codex", tmp_path, path="/x", chay=chay_gia([], 1))
    assert co is False and "ai@x" not in ct


def test_dang_nhap_codex_loi_ha_tang_khong_ket_luan_thu_hoi_loi_thi_noi_len(tmp_path):
    for loi in (subprocess.TimeoutExpired("x", 20), OSError("spawn")):
        co, ct = dang_nhap_codex(PR, "codex", tmp_path, path="/x", chay=chay_gia([], loi))
        assert co is None and "không kết luận" in ct
    with pytest.raises(LoiThuHoi):                      # A05: người gọi phải biết để thôi mọi thăm dò dưới principal
        dang_nhap_codex(PR, "codex", tmp_path, path="/x", chay=chay_gia([], LoiThuHoi("x")))


def test_tho_kiem_dang_nhap_thu_hoi_loi_thi_khong_do_han_muc(tmp_path):
    hm = []

    def dn(*a, **kw):
        raise LoiThuHoi("không xác nhận thu hồi `codex login status`")
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=lambda *a, **k: hm.append(1), bay_gio=LUC,
                    principal_cua_=lambda ch, k: PR, dang_nhap_=dn)
    m = {x.muc: x for x in ds}
    assert hm == [] and m["C/codex-1 hạn mức"].muc_do == "do" and m["C/codex-1 đăng nhập"].muc_do == "do"
    assert "thu hồi" in m["C/codex-1 đăng nhập"].chi_tiet


def test_tho_kiem_khong_principal_thi_khong_spawn_dang_nhap(tmp_path):
    goi, hm = [], []
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=lambda *a, **k: hm.append(k["principal"]),
                    bay_gio=LUC, principal_cua_=lambda ch, k: None,
                    dang_nhap_=lambda *a, **k: goi.append(a) or (True, "x"))
    m = {x.muc: x for x in ds}
    assert goi == [] and hm == [None] and m["C/codex-1 đăng nhập"].muc_do == "do"
    assert "principal" in m["C/codex-1 đăng nhập"].chi_tiet


def test_tho_kiem_mot_lan_xac_minh_uid_cho_ca_dang_nhap_va_han_muc(tmp_path):
    goi, xm = [], []

    def dn(pr, codex, thu_muc, *, path):
        goi.append((pr, codex, thu_muc, path))
        return True, "ok"
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=_hm, bay_gio=LUC,
                    principal_cua_=lambda ch, k: xm.append(k.ten) or PR, dang_nhap_=dn)
    assert xm == ["codex-1"] and goi == [(PR, "/opt/bin/codex", tmp_path / "codex-1", _ch(tmp_path).chay.path_cli)]
    assert {x.muc: x.muc_do for x in ds}["C/codex-1 đăng nhập"] == "xanh"


def test_tho_kiem_thu_hoi_loi_khi_xac_minh_uid_thi_do(tmp_path):
    def loi(ch, k):
        raise LoiThuHoi("x")
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=_hm, bay_gio=LUC, principal_cua_=loi,
                    dang_nhap_=lambda *a, **k: 1 / 0)
    assert {x.muc: x.muc_do for x in ds}["C/codex-1 hạn mức"] == "do"


def test_claude_auth_status_uid_truoc_qua_p1(tmp_path):
    ch, goi = cau_hinh(tmp_path), []
    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay_gia(goi),
                     xac_minh=lambda *a: (_ for _ in ()).throw(LoiDanhTinh("x")))[0] == "do" and goi == []
    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay_gia(goi), xac_minh=lambda *a: 600)[0] \
        == "xanh"
    assert goi[0][1]["kill"].__self__.user == "tram-k-1" and goi[0][1]["timeout"] == 30
    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay_gia([], LoiThuHoi("x")),
                     xac_minh=lambda *a: 600)[0] == "do"
