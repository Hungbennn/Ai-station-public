"""CLI máy A gọi B (plan 4d 4D-3b) qua HTTP giả nối vào tram-api thật trong bộ nhớ: xem → `tạo` đúng bản đã xem →
gửi lại không tạo trùng; sửa sau khi tạo là xung đột; mất kết nối/5xx là CHƯA RÕ, không đổi mã. Không mạng thật."""
import http.client
import json
import urllib.error
import urllib.request

import pytest
from phong_van_gia import GOC, MoTram, chay, khach, ma_xem, nhap, nhap_day_du
from yeu_cau_gia import BI_MAT


def test_chi_gui_dieu_kien_csrf_khong_gui_danh_tinh(tmp_path, capsys):
    mo, p = MoTram(tmp_path), nhap_day_du(tmp_path)
    ma, out = chay(capsys, mo, "xem", str(p))
    assert ma == 0 and "kho trên B: /kho/b/hr-codex" in out and "HỢP LỆ" in out and "không có biên nhận" in out
    ((req, timeout),) = mo.goi
    assert (req.full_url, req.get_method(), timeout) == (GOC + "/api/feature/yeu-cau/xem", "POST", 20)
    assert dict(req.header_items()) == {"Content-type": "application/json", "X-tram": "1", "Origin": GOC}
    assert mo.bd.so_lan_tao() == 0


def test_xem_roi_tao_dung_ban_da_xem_gui_lai_khong_tao_trung(tmp_path, capsys):
    mo, p = MoTram(tmp_path), nhap_day_du(tmp_path)
    dau = ma_xem(chay(capsys, mo, "xem", str(p))[1])
    ma, out = chay(capsys, mo, "gui", str(p), "--dau-xem", dau)
    assert ma == 0 and "ĐÃ TẠO · feature hr-f1 · nhãn can-spec" in out and mo.goi[-1][1] == 420
    ma, out = chay(capsys, mo, "gui", str(p), "--dau-xem", dau)
    assert ma == 0 and "ĐÃ CÓ, không tạo lại · feature hr-f1" in out and mo.bd.so_lan_tao() == 1
    assert "đã gửi trước: da_tao hr-f1" in chay(capsys, mo, "xem", str(p))[1]


def test_sua_sau_khi_xem_phai_xem_lai(tmp_path, capsys):
    mo, p = MoTram(tmp_path), nhap_day_du(tmp_path)
    dau = ma_xem(chay(capsys, mo, "xem", str(p))[1])
    d = json.loads(p.read_text(encoding="utf-8"))
    p.write_text(json.dumps({**d, "uu_tien": 1}, ensure_ascii=False), encoding="utf-8")
    ma, out = chay(capsys, mo, "gui", str(p), "--dau-xem", dau)
    assert ma == 2 and "NỘI DUNG ĐÃ ĐỔI" in out and mo.bd.so_lan_tao() == 0


def test_sua_sau_khi_tao_la_xung_dot_yeu_cau_moi_phai_chon_ro(tmp_path, capsys):
    mo, p = MoTram(tmp_path), nhap_day_du(tmp_path)
    chay(capsys, mo, "gui", str(p), "--dau-xem", ma_xem(chay(capsys, mo, "xem", str(p))[1]))
    d = json.loads(p.read_text(encoding="utf-8"))
    p.write_text(json.dumps({**d, "tieu_de": "Tiêu đề khác"}, ensure_ascii=False), encoding="utf-8")
    out = chay(capsys, mo, "xem", str(p))[1]
    assert "NỘI DUNG KHÁC lần gửi trước" in out
    ma, out = chay(capsys, mo, "gui", str(p), "--dau-xem", ma_xem(out))
    assert ma == 2 and "XUNG ĐỘT" in out and mo.bd.so_lan_tao() == 1
    ma, out = chay(capsys, mo, "moi", "--tu", str(p), "--thu-muc", str(tmp_path / "nhap"))
    moi = out.split("NHÁP MỚI ")[1].strip()
    assert ma == 0 and nhap.doc(moi)["ma_yeu_cau"] != d["ma_yeu_cau"]
    ma, out = chay(capsys, mo, "gui", moi, "--dau-xem", ma_xem(chay(capsys, mo, "xem", moi)[1]))
    assert ma == 0 and "ĐÃ TẠO · feature hr-f2" in out and mo.bd.so_lan_tao() == 2


@pytest.mark.parametrize("hong", [OSError("ssl " + BI_MAT), TimeoutError(BI_MAT), http.client.IncompleteRead(b"x"),
                                  urllib.error.HTTPError(GOC, 500, BI_MAT, {}, None), RuntimeError(BI_MAT)])
def test_mat_ket_noi_hay_5xx_khi_gui_la_chua_ro_khong_doi_ma(tmp_path, capsys, hong):
    p = nhap_day_du(tmp_path)
    truoc = p.read_text(encoding="utf-8")

    def mo(req, timeout):
        raise hong
    ma, out = chay(capsys, mo, "gui", str(p), "--dau-xem", "0" * 16)
    assert ma == 3 and "CHƯA RÕ" in out and "không đổi mã" in out and BI_MAT not in out
    assert p.read_text(encoding="utf-8") == truoc


def test_khong_ro_dang_xu_ly_tra_ma_3_va_khong_tao_lai(tmp_path, capsys):
    mo, p = MoTram(tmp_path, su_co=("truoc_ghi", "loi")), nhap_day_du(tmp_path)
    dau = ma_xem(chay(capsys, mo, "xem", str(p))[1])
    for _ in range(3):
        ma, out = chay(capsys, mo, "gui", str(p), "--dau-xem", dau)
        assert ma == 3 and "CHƯA RÕ" in out
    assert mo.bd.so_lan_tao() == 1


def test_403_404_422_la_tu_choi_chu_co_dinh(tmp_path, capsys):
    p = nhap_day_du(tmp_path)
    ma, out = chay(capsys, MoTram(tmp_path / "a", login=None), "xem", str(p))
    assert ma == 2 and "403" in out and "không thử đường khác" in out
    mo = MoTram(tmp_path / "b", bat_ghi=False)
    ma, out = chay(capsys, mo, "xem", str(p))
    assert ma == 2 and "B CHƯA BẬT GHI" in out and "mã xem" not in out
    ma, out = chay(capsys, mo, "gui", str(p), "--dau-xem", "0" * 16)
    assert ma == 2 and "422" in out and "chưa bật ghi" in out


def test_dia_chi_tram_khong_proxy_khong_chuyen_huong(monkeypatch):
    assert khach.goc_tram(GOC + "/") == GOC and khach.goc_tram("https://may-b:8443") == "https://may-b:8443"
    assert khach.goc_tram("https://May-B.Tail.TS.net:443") == "https://may-b.tail.ts.net"     # Origin B so nguyên chuỗi
    for sai in ("http://may-b", GOC + "/api", "https://u@may-b", GOC + "?x=1", "", "may-b", None, "https://b:x"):
        assert khach.goc_tram(sai) is None
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example:3128")
    assert not any(isinstance(x, urllib.request.ProxyHandler) and x.proxies
                   for x in khach.mo_mac_dinh().__self__.handlers)
    assert khach.KhongChuyenHuong().redirect_request(None, None, 302, "x", {}, "https://khac/") is None
    for host in ("https://máy-b.ts.net", "https://[::1]", "https://may-b.ts.net."):
        assert khach.goc_tram(host) is None

    def dut(req, timeout):
        raise http.client.IncompleteRead(b"x")
    with pytest.raises(khach.MatKetNoi):
        khach.goi(GOC, "/x", {}, dut)
