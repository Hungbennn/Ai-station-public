"""bs-2bd.1.5: memory 7710 kiểm Host TRƯỚC mọi thứ (chống DNS rebinding) và bật lại lớp kiểm Host/Origin của SDK MCP.
Không mở cổng thật: ASGI trong bộ nhớ."""
import pytest

from asgi_gia import goi
from mcp_gia import goi_mcp, rpc
from test_nho_mcp import H_PHIEU, mt, post  # noqa: F401 — fixture `mt` dùng lại
from test_nho_ung_dung import AppGhi
from tram.nho.ung_dung import HOST_NOI_BO, CauHinhMcp, UngDungNho, tao_cau_hinh_mcp_that


def _app():
    tra = []
    http, mcp = AppGhi("http"), AppGhi("mcp")
    cfg = CauHinhMcp(lambda g: tra.append(g), lambda: None, lambda t: True)
    return UngDungNho(http, mcp, cfg), http, mcp, tra


@pytest.mark.parametrize("host", ["attacker.example:7710", "127.0.0.1:7700", "127.0.0.1", "", "LOCALHOST:7711"])
@pytest.mark.parametrize("duong", ["/mcp", "/nho-lai", "/xoa"])
def test_host_la_421_khong_toi_app_khong_xac_thuc(host, duong):
    app, http, mcp, tra = _app()
    r = goi(app, "POST", duong, json_body={}, headers={"Host": host, **H_PHIEU})
    assert r.status == 421 and r.json() == {"loi": "Host không hợp lệ"}
    assert http.scope == mcp.scope == [] and tra == []


@pytest.mark.parametrize("host", sorted(HOST_NOI_BO))
def test_host_noi_bo_qua_cong(host):
    app, http, _, _ = _app()
    assert goi(app, "POST", "/nho-lai", json_body={}, headers={"Host": host}).json() == {"app": "http"}
    assert HOST_NOI_BO == {"127.0.0.1:7710", "localhost:7710"}


def test_cau_hinh_that_them_ten_may_b_cau_hinh_hong_chi_localhost(tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("ten_may_b: may-b.duoi-duoi.ts.net\n", encoding="utf-8")
    assert tao_cau_hinh_mcp_that().host == HOST_NOI_BO | {"may-b.duoi-duoi.ts.net", "may-b.duoi-duoi.ts.net:443"}
    (tram_home_tam / "cau-hinh.yaml").write_text("ten_may_b: 'co dau cach'\n", encoding="utf-8")
    assert tao_cau_hinh_mcp_that().host == HOST_NOI_BO


def test_sdk_bat_lai_kiem_origin(mt):
    app, _ = mt
    ok, la = goi_mcp(app, post(rpc("tools/list"), H_PHIEU),
                     post(rpc("tools/list", id=2), {**H_PHIEU, "Origin": "http://attacker.example"}))
    assert ok.status == 200 and la.status == 403
