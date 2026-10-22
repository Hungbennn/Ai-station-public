"""Mọi đường từ chối của API tạo feature (plan 4d 4D-2) — gián điệp chứng minh KHÔNG mở sổ, KHÔNG đọc/gọi `bd`:
thiếu/giả/trùng danh tính, sai kênh/X-Tram/Origin/Host, dự án lạ, chưa bật ghi, thân sai hoặc đòi đổi nhãn/kho/actor."""
import pytest
from api_yeu_cau_gia import MAY_B, TAO, XEM, dau, goi_tho, mo_app, than

from api_gia import LOGIN

DUNG = [("Tailscale-User-Login", LOGIN), ("X-Tram", "1"), ("Origin", f"https://{MAY_B}")]


def bo(ten):
    return [h for h in DUNG if h[0] != ten]


def kiem_khong_dong_vao(bd, mo):
    assert mo == [] and bd.so_lan_doc() == 0 and bd.so_lan_tao() == 0


@pytest.mark.parametrize("duong", [TAO, XEM])
@pytest.mark.parametrize("headers, ma", [
    (bo("Tailscale-User-Login"), 403),
    ([("Tailscale-User-Login", "ke-la@example.com"), *bo("Tailscale-User-Login")], 403),
    ([("Tailscale-User-Login", " "), *bo("Tailscale-User-Login")], 403),
    ([*DUNG, ("Tailscale-User-Login", LOGIN)], 403),                          # hai header danh tính
    (bo("X-Tram"), 403),
    ([("X-Tram", "0"), *bo("X-Tram")], 403),
    (bo("Origin"), 403),
    ([("Origin", f"http://{MAY_B}"), *bo("Origin")], 403),
    ([("Origin", "https://ke-la.example"), *bo("Origin")], 403),
])
def test_sai_danh_tinh_hay_chong_csrf_thi_403(tmp_path, duong, headers, ma):
    app, _, bd, mo = mo_app(tmp_path)
    assert goi_tho(app, duong, {**than(), "dau_xem": dau()}, headers) == ma
    kiem_khong_dong_vao(bd, mo)


@pytest.mark.parametrize("duong", [TAO, XEM])
def test_than_sai_ma_khong_danh_tinh_van_403_truoc(tmp_path, duong):
    app, _, bd, mo = mo_app(tmp_path)
    assert goi_tho(app, duong, {"nhan": ["cot:ai-lam"], "repo": "/"}, bo("Tailscale-User-Login")) == 403
    kiem_khong_dong_vao(bd, mo)


def test_chua_cau_hinh_may_b_kenh_unix_va_host_la(tmp_path):
    app, pt, bd, mo = mo_app(tmp_path)
    thanyc = {**than(), "dau_xem": dau()}
    assert goi_tho(app, TAO, thanyc, DUNG, host="ke-la.example") == 421
    pt.cau_hinh = type(pt.cau_hinh)(dai_ca_logins=(LOGIN,), ten_may_b=None)
    assert goi_tho(app, TAO, thanyc, DUNG) == 403
    kiem_khong_dong_vao(bd, mo)


@pytest.mark.parametrize("duong", [TAO, XEM])
def test_du_an_la_404(tmp_path, duong):
    app, _, bd, mo = mo_app(tmp_path)
    p = {**than()["phieu"], "du_an": "erp"}
    them = {"dau_xem": dau(du_an="erp", phieu=p)} if duong == TAO else {}
    assert goi_tho(app, duong, {**than(du_an="erp", phieu=p), **them}, DUNG) == 404
    kiem_khong_dong_vao(bd, mo)


def _loi_yaml(ten):
    raise ValueError("bat_ghi phải là true hoặc false")


@pytest.mark.parametrize("bat_ghi", [False, _loi_yaml, lambda ten: "true", lambda ten: None])
def test_chua_bat_ghi_hay_khoa_loi_thi_422_khong_tao(tmp_path, bat_ghi):
    app, _, bd, mo = mo_app(tmp_path, bat_ghi=bat_ghi)
    assert goi_tho(app, TAO, {**than(), "dau_xem": dau()}, DUNG) == 422
    kiem_khong_dong_vao(bd, mo)


@pytest.mark.parametrize("sua", [
    {"nhan": ["cot:ai-lam"]}, {"repo": "/tmp/kho-khac"}, {"kho": "/tmp"}, {"actor": "tram/giao-viec"},
    {"nguoi_gui": "ke-la@example.com"}, {"ma_yeu_cau": "yc-" + "0" * 31}, {"ma_yeu_cau": "YC-" + "0" * 32},
    {"ma_yeu_cau": "pyc-0123456789abcdef"}, {"tieu_de": "--label cot:ai-lam"}, {"tieu_de": "Dòng 1\nDòng 2"},
    {"tieu_de": " có khoảng trắng"}, {"tieu_de": "x" * 201}, {"uu_tien": "2"}, {"uu_tien": True}, {"uu_tien": 5},
    {"phieu": []}, {"dau_xem": "ABC"},
])
def test_than_sai_hay_doi_nhan_kho_actor_thi_422(tmp_path, sua):
    app, _, bd, mo = mo_app(tmp_path)
    assert goi_tho(app, TAO, {**than(), "dau_xem": dau(), **sua}, DUNG) == 422
    kiem_khong_dong_vao(bd, mo)


def test_d147_xem_tren_tcp_khong_phu_thuoc_socket(tmp_path):
    app, _, bd, _ = mo_app(tmp_path)
    app.state.kenh_ghi = 'unix-socket'
    assert goi_tho(app, XEM, than(), DUNG) == 200
    assert bd.so_lan_tao() == 0
