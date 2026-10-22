import json
import subprocess
from datetime import datetime, timezone

from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.do_may import TAG_THO
from tram.tho.kiem_3b import bo_sung_3b
from tram.tho.kiem_may import DauDo, MucKiem, in_ket_qua, kiem_may
from tram.tho.principal import Principal

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


def _ch(tmp_path, api="https://may-b.tail1234.ts.net"):
    return CauHinhTho("C", api, (
        KheCauHinh("codex-1", "codex", None, tmp_path / "codex-1", "Codex 1", ("coder",)),
        KheCauHinh("claude-3", "claude", None, tmp_path / "claude-3", "Claude 3", ("qc",))))


def _dd(tmp_path, *, dang_nhap=0, tags=(TAG_THO,), goc="/opt/bin"):
    def chay(argv, **kw):
        if argv[1:] == ["login", "status"]:
            assert kw["env"]["CODEX_HOME"] == str(tmp_path / "codex-1")
            return subprocess.CompletedProcess(argv, dang_nhap, "", "")
        if argv[1:] == ["status", "--json"]:
            return subprocess.CompletedProcess(argv, 0, json.dumps({"Self": {"Tags": list(tags)}}), "")
        return subprocess.CompletedProcess(argv, 0, "x 1.0\n" if "--version" in argv else "", "")
    return DauDo(ping=lambda: {"may_id": "C", "khe": []}, du_an=lambda: [], which=lambda c: f"{goc}/{c}",
                 chay=chay, con_trong=lambda p: 50 * 1024 ** 3, thu_muc_kho=tmp_path / "kho")


def _hm(kid, thu_muc, *, bay_gio, principal, path, codex):
    return HanMuc(khe_id=kid, nguon="app-server", cua_so=[
        CuaSo(loai="5h", trang_thai="biet", phan_tram=62.0, doc_luc="2026-10-13T03:00:00Z")])


def _muc(ds):
    return {m.muc: (m.muc_do, m.chi_tiet) for m in ds}


def test_khe_codex_thay_muc_dang_nhap_them_han_muc_va_tag(tmp_path):
    goc = [MucKiem("C/codex-1 đăng nhập", "do", "chờ S2"), MucKiem("C/claude-3 đăng nhập", "do", "chờ S2")]
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), goc, doc_han_muc=_hm, bay_gio=LUC,
                    principal_cua_=lambda ch, k: Principal("user", "tram-k-c-codex-1"),
                    dang_nhap_=lambda *a, **kw: (True, "đã đăng nhập"))
    m = _muc(ds)
    assert m["C/codex-1 đăng nhập"][0] == "xanh" and m["C/claude-3 đăng nhập"] == ("do", "chờ S2")
    assert [x.muc for x in ds].count("C/codex-1 đăng nhập") == 1
    assert m["C/codex-1 hạn mức"] == ("xanh", "5h 62%") and m["tailscale tag"][0] == "xanh"
    assert "C/claude-3 hạn mức" not in m


def test_chua_dang_nhap_chua_doc_han_muc_chua_gan_tag(tmp_path):
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path, dang_nhap=1, tags=()), [],
                    doc_han_muc=lambda *a, **k: None, bay_gio=LUC)
    m = _muc(ds)
    assert m["C/codex-1 đăng nhập"][0] == "do" and m["C/codex-1 hạn mức"][0] == "vang"
    assert m["tailscale tag"][0] == "do" and in_ket_qua(ds)[1] == 1
    assert "tailscale tag" not in _muc(bo_sung_3b(_ch(tmp_path, "http://127.0.0.1:7700"), _dd(tmp_path), [],
                                                  doc_han_muc=_hm, bay_gio=LUC))


def test_kiem_may_goi_bo_sung_3b(tmp_path):
    m = _muc(kiem_may(_ch(tmp_path), _dd(tmp_path, goc=str(tmp_path / "khong-co"))))
    assert m["C/codex-1 đăng nhập"][0] == "do" and m["tailscale tag"][0] == "xanh"     # khe chưa principal: không dò
    assert m["C/codex-1 hạn mức"][0] == "vang"                      # không có `codex` thật → không đọc được


def test_uid_principal_chua_chung_minh_thi_vang_khong_hoi(tmp_path, monkeypatch):
    from dataclasses import replace
    from tram.kiem.danh_tinh import LoiDanhTinh
    ch = _ch(tmp_path)
    ch = replace(ch, khe=(replace(ch.khe[0], principal="user:quan-ly"),))       # cấu hình nhầm: principal = quản lý
    monkeypatch.setattr("tram.kiem.danh_tinh.xac_minh_uid", lambda *a: (_ for _ in ()).throw(LoiDanhTinh("x")))
    goi = []
    ds = bo_sung_3b(ch, _dd(tmp_path), [], doc_han_muc=lambda *a, **k: goi.append(k["principal"]), bay_gio=LUC)
    assert goi == [None] and _muc(ds)["C/codex-1 hạn mức"][0] == "vang"
