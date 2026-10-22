"""Envelope lỗi không phản chiếu input; chỉ áp cho hai tuyến 4d."""
import pytest
from api_gia import DAI_CA
from api_yeu_cau_gia import TAO, XEM, dau, mo_app, than
from asgi_gia import goi

BI_MAT = "BI_MAT_DOT7"


@pytest.mark.parametrize("duong", [XEM, TAO])
@pytest.mark.parametrize("sua", [
    {"phieu": BI_MAT}, {"extra": BI_MAT}, {"ma_yeu_cau": BI_MAT},
])
def test_loi_envelope_khong_echo_input(tmp_path, capsys, caplog, duong, sua):
    app, pt, bd, mo = mo_app(tmp_path)
    mo_bd, tao_bd = [], pt.tao_bd_yeu_cau

    def dem(ten):
        mo_bd.append(ten)
        return tao_bd(ten)

    pt.tao_bd_yeu_cau = dem
    body = {**than(), **({"dau_xem": dau()} if duong == TAO else {}), **sua}
    r = goi(app, "POST", duong, json_body=body, headers=DAI_CA)
    assert r.status == 422
    assert BI_MAT not in r.body.decode()
    assert r.json() == {"trang_thai": "khong_hop_le", "loi": ["Thân yêu cầu không hợp lệ"]}
    out = capsys.readouterr()
    assert BI_MAT not in out.out + out.err + caplog.text
    assert mo == mo_bd == []
    assert bd.so_lan_doc() == bd.so_lan_tao() == 0
    assert not (tmp_path / "so.db").exists()


@pytest.mark.parametrize("duong", [XEM, TAO])
@pytest.mark.parametrize("headers", [{}, {**DAI_CA, "Tailscale-User-Login": "ke-la@example.com"}])
def test_envelope_sai_khong_bo_qua_danh_tinh(tmp_path, duong, headers):
    app, _, bd, mo = mo_app(tmp_path)
    body = {**than(), **({"dau_xem": dau()} if duong == TAO else {}), "phieu": BI_MAT}
    r = goi(app, "POST", duong, json_body=body, headers=headers)
    assert r.status == 403 and BI_MAT not in r.body.decode()
    assert mo == [] and bd.so_lan_doc() == bd.so_lan_tao() == 0


def test_handler_mac_dinh_ngoai_4d_khong_doi(tmp_path):
    app, _, _, _ = mo_app(tmp_path)

    @app.get("/kiem-envelope-test")
    def doc(so: int):
        return {"so": so}

    r = goi(app, "GET", "/kiem-envelope-test?so=sai")
    assert r.status == 422
    assert "detail" in r.json() and "trang_thai" not in r.json()
