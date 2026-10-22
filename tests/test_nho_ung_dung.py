import hashlib

from asgi_gia import goi
from tram.nho.danh_tinh import DanhTinh
from tram.nho.ung_dung import HOST_NOI_BO, KHOA_DANH_TINH, CauHinhMcp, UngDungNho, tao_cau_hinh_mcp_that

MA = "Abc_def-123456789012ab"
GID = "g-20261013-0042"
PHIEU = {"du_an": "hr-codex", "vai": "coder", "ma_giao": MA, "con_hieu_luc": True}
H_PHIEU = {"X-Tram-Giao-Id": GID, "X-Tram-Ma-Giao": MA}


class AppGhi:
    """ASGI giả (CHỈ DÙNG TRONG TEST): ghi lại scope, trả 200 {"app": ten}."""

    def __init__(self, ten):
        self.ten, self.scope = ten, []

    async def __call__(self, scope, receive, send):
        self.scope.append(scope)
        await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"application/json")]})
        await send({"type": "http.response.body", "body": f'{{"app": "{self.ten}"}}'.encode()})


def tao(tra=lambda g: PHIEU if g == GID else None):
    http, mcp = AppGhi("http"), AppGhi("mcp")
    cfg = CauHinhMcp(tra, lambda: hashlib.sha256(b"m" * 40).hexdigest(), lambda t: t == "hr-codex",
                     host=HOST_NOI_BO | {"127.0.0.1:7700"})          # asgi_gia gửi Host của tram-api
    return UngDungNho(http, mcp, cfg), http, mcp


def test_mcp_khong_bang_chung_401_khong_toi_sdk(capsys):
    app, http, mcp = tao()
    for h in ({}, {"Authorization": "Bearer tok-nho"}, {"Tailscale-User-Login": "dai-ca@example.com"},
              {"X-Tram-Giao-Id": GID, "X-Tram-Ma-Giao": "Zbc_def-123456789012ab"}):
        r = goi(app, "POST", "/mcp", json_body={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, headers=h)
        assert r.status == 401 and "loi" in r.json() and r.headers["cache-control"] == "no-store"
    assert mcp.scope == http.scope == [] and MA not in capsys.readouterr().err


def test_mcp_hop_le_mang_danh_tinh_trong_state():
    app, http, mcp = tao()
    r = goi(app, "POST", "/mcp", json_body={}, headers=H_PHIEU)
    assert r.json() == {"app": "mcp"} and http.scope == []
    dt = mcp.scope[0]["state"][KHOA_DANH_TINH]
    assert isinstance(dt, DanhTinh) and dt.vung_cap == ("/du-an/hr-codex", "/vai/coder", "/chung")
    r = goi(app, "POST", "/mcp", json_body={}, headers={"Authorization": "Bearer " + "m" * 40,
                                                        "X-Tram-Du-An": "hr-codex"})
    assert r.status == 200 and not mcp.scope[1]["state"][KHOA_DANH_TINH].duoc_ghi


def test_khong_tra_duoc_phieu_503_va_duong_khac_khong_qua_cong():
    def sap(g):
        raise OSError("tram-api tắt")
    app, http, mcp = tao(tra=sap)
    assert goi(app, "POST", "/mcp", json_body={}, headers=H_PHIEU).status == 503 and mcp.scope == []
    for duong in ("/nho-lai", "/xoa", "/mcp/", "/khac"):
        assert goi(app, "POST", duong, json_body={}).json() == {"app": "http"}
    assert len(http.scope) == 4 and mcp.scope == []


def test_cau_hinh_that_khong_doc_keychain_luc_tao(monkeypatch):
    import subprocess
    import tram.cau_hinh.du_an as du_an
    import tram.nho.ma_dai_ca as ma_dai_ca
    # Fixture tự chứa: không phụ thuộc du-an/hr-codex.yaml hay ~/.tram của người chạy.
    monkeypatch.setattr(du_an, "liet_ke_du_an", lambda: ["du-an-thu", "_tram"])
    monkeypatch.setattr(ma_dai_ca, "doc_bam", lambda: None)
    def cam_goi_lenh(*args, **kwargs):
        raise AssertionError("Khởi tạo/các callback đọc cấu hình không được gọi subprocess/Keychain")
    monkeypatch.setattr(subprocess, "run", cam_goi_lenh)
    cfg = tao_cau_hinh_mcp_that()
    assert cfg.co_du_an("du-an-thu")
    assert not cfg.co_du_an("khong-co") and not cfg.co_du_an("_tram")
    assert cfg.bam_ma_dai_ca() is None
