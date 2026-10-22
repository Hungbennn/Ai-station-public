import asyncio
from types import SimpleNamespace

import pytest
from fastapi import Depends, FastAPI, HTTPException
from starlette.datastructures import Headers

from asgi_gia import goi
from tram.api.bao_mat import CSP, host_hop_le, kiem_ghi, la_dai_ca, them_header_an_toan, yeu_cau_ghi
from tram.cau_hinh.tram import CauHinhTram

CH = CauHinhTram(dai_ca_logins=("dai-ca@example.com",), ten_may_b="may-b.tail.ts.net")
DU = {"tailscale-user-login": "dai-ca@example.com", "x-tram": "1", "origin": "https://may-b.tail.ts.net"}


def test_la_dai_ca():
    assert la_dai_ca(DU, CH)
    assert not la_dai_ca({}, CH)
    assert not la_dai_ca({**DU, "tailscale-user-login": "khac@x.y"}, CH)
    assert not la_dai_ca(DU, CauHinhTram())          # chưa cấu hình danh sách → không ai ghi được


def test_kiem_ghi_tung_dieu_kien():
    assert kiem_ghi(DU, CH) is None
    assert "Chỉ đọc" in kiem_ghi({k: v for k, v in DU.items() if k != "tailscale-user-login"}, CH)
    assert "X-Tram" in kiem_ghi({**DU, "x-tram": "0"}, CH)
    assert "Origin" in kiem_ghi({**DU, "origin": "https://evil.example"}, CH)
    assert "Origin" in kiem_ghi({k: v for k, v in DU.items() if k != "origin"}, CH)
    assert "ten_may_b" in kiem_ghi(DU, CauHinhTram(dai_ca_logins=("dai-ca@example.com",)))


def _app():
    app = FastAPI()
    app.state.pt = SimpleNamespace(cau_hinh=CH)

    @app.post("/api/chu/estop", dependencies=[Depends(yeu_cau_ghi)])
    @app.post("/ghi", dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        return {"ok": True}

    return app


def test_dependency_qua_asgi():
    hdr = {"Tailscale-User-Login": "dai-ca@example.com", "X-Tram": "1", "Origin": "https://may-b.tail.ts.net"}
    assert goi(_app(), "POST", "/api/chu/estop", json_body={}, headers=hdr).json() == {"ok": True}
    r = goi(_app(), "POST", "/ghi", json_body={}, headers=hdr)
    assert r.status == 403 and r.json()["detail"] == "Tuyến chưa được cấp quyền người"
    r = goi(_app(), "POST", "/api/chu/estop", json_body={}, headers={"X-Tram": "1"})
    assert r.status == 403 and r.json()["detail"] == "Danh tính không hợp lệ"


def test_hai_header_danh_tinh_bi_tu_choi():
    raw = [(b"tailscale-user-login", b"dai-ca@example.com"), (b"tailscale-user-login", b"khac@x.y"),
           (b"x-tram", b"1"), (b"origin", b"https://may-b.tail.ts.net")]
    req = SimpleNamespace(headers=Headers(raw=raw),
                          app=SimpleNamespace(state=SimpleNamespace(pt=SimpleNamespace(cau_hinh=CH))))
    with pytest.raises(HTTPException) as e:
        asyncio.run(yeu_cau_ghi(req))
    assert e.value.status_code == 403


def _app_doc():
    app = FastAPI()
    app.state.pt = SimpleNamespace(cau_hinh=CH)

    @app.get("/doc")
    def doc():
        return {"ok": True}

    them_header_an_toan(app, CH, cong=7700)
    return app


def test_header_an_toan_tren_moi_phan_hoi():
    assert "unsafe-eval" not in CSP and "unsafe-inline" not in CSP and "script-src 'self'" in CSP
    for duong, ma in (("/doc", 200), ("/khong-co", 404)):
        r = goi(_app_doc(), "GET", duong)
        assert r.status == ma and r.headers["content-security-policy"] == CSP
        assert r.headers["x-content-type-options"] == "nosniff" and r.headers["x-frame-options"] == "DENY"
        assert r.headers["referrer-policy"] == "no-referrer"


def test_host_ngoai_danh_sach_la_421():
    assert host_hop_le(CH, 7700) == {"127.0.0.1:7700", "localhost:7700", "may-b.tail.ts.net", "may-b.tail.ts.net:443"}
    assert host_hop_le(CauHinhTram(), 7701) == {"127.0.0.1:7701", "localhost:7701"}
    for host in ("127.0.0.1:7700", "localhost:7700", "MAY-B.tail.ts.net", "may-b.tail.ts.net:443"):
        assert goi(_app_doc(), "GET", "/doc", headers={"Host": host}).status == 200, host
    for host in ("evil.example", "evil.example:7700", "127.0.0.1:8080", ""):
        r = goi(_app_doc(), "GET", "/doc", headers={"Host": host})
        assert r.status == 421 and "content-security-policy" in r.headers, host


def test_loi_bat_ngo_500_van_co_header_an_toan():
    app = _app_doc()

    @app.get("/no")
    def no():
        raise RuntimeError("bí mật trong traceback")

    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "GET", "scheme": "http",
             "path": "/no", "raw_path": b"/no", "query_string": b"", "root_path": "",
             "headers": [(b"host", b"127.0.0.1:7700")], "client": ("127.0.0.1", 1), "server": ("127.0.0.1", 7700)}
    gui: list[dict] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(m):
        gui.append(m)

    with pytest.raises(RuntimeError):            # ném lại để uvicorn ghi log
        asyncio.run(app(scope, receive, send))
    dau = [m for m in gui if m["type"] == "http.response.start"]
    assert len(dau) == 1 and dau[0]["status"] == 500
    h = {k.decode(): v.decode() for k, v in dau[0]["headers"]}
    assert h["content-security-policy"] == CSP and h["x-content-type-options"] == "nosniff"
    assert h["x-frame-options"] == "DENY"
    than = b"".join(m.get("body", b"") for m in gui if m["type"] == "http.response.body").decode()
    assert "bí mật" not in than and "Traceback" not in than and "Lỗi máy chủ" in than
