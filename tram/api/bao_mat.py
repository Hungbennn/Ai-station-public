"""Danh tính Tailscale + chống CSRF cho API ghi; header an toàn + kiểm Host cho mọi phản hồi (spec 2 §4 mục 2, 3, 6).

Lát 2a tin header `Tailscale-User-Login` do `tailscale serve` gắn. Header này giả được bởi mọi tiến trình
cục bộ gọi thẳng 127.0.0.1 (spec §4 mục 2b) — chấp nhận ở 2a vì chưa có thợ chạy trên B; phải thay trước 3a.
Hành vi header thật kiểm ở Task 26 (chờ #5).
"""
from collections.abc import Mapping

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from tram.api.kenh_ghi import kenh_hop_le
from tram.cau_hinh.tram import CauHinhTram

HEADER_DANH_TINH = "tailscale-user-login"
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
       "font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
HEADER_AN_TOAN = [(b"content-security-policy", CSP.encode()), (b"x-content-type-options", b"nosniff"),
                  (b"referrer-policy", b"no-referrer"), (b"x-frame-options", b"DENY")]


def la_dai_ca(headers: Mapping[str, str], ch: CauHinhTram) -> bool:
    login = (headers.get(HEADER_DANH_TINH) or "").strip()
    return bool(login) and login in ch.dai_ca_logins


def kiem_ghi(headers: Mapping[str, str], ch: CauHinhTram) -> str | None:
    if not la_dai_ca(headers, ch):
        return "Chỉ đọc: yêu cầu không mang danh tính Đại ca (Tailscale-User-Login)"
    if headers.get("x-tram") != "1":
        return "Thiếu header X-Tram: 1"
    if not ch.ten_may_b:
        return "Chưa cấu hình ten_may_b trong ~/.tram/cau-hinh.yaml — từ chối mọi thao tác ghi"
    if headers.get("origin") != f"https://{ch.ten_may_b}":
        return "Origin không khớp máy B"
    return None


def _header(request) -> dict[str, str]:
    return {k.lower(): v for k, v in request.headers.items()}


def yeu_cau_danh_tinh(request: Request) -> None:
    if not kenh_hop_le(request):
        raise HTTPException(status_code=403, detail="API ghi chỉ nhận qua kênh đã xác thực (cach_ly.kenh_ghi)")
    if len(request.headers.getlist(HEADER_DANH_TINH)) > 1:
        raise HTTPException(status_code=403, detail="Nhiều header danh tính — từ chối")
    loi = kiem_ghi(_header(request), request.app.state.pt.cau_hinh)
    if loi:
        raise HTTPException(status_code=403, detail=loi)


async def yeu_cau_ghi(request: Request) -> None:
    from tram.api.passkey_phu_thuoc import can_ghi, rang_yeu_cau
    from starlette.concurrency import run_in_threadpool
    await run_in_threadpool(can_ghi, request)
    await rang_yeu_cau(request)


def la_dai_ca_yeu_cau(request: Request) -> bool:
    return (kenh_hop_le(request) and len(request.headers.getlist(HEADER_DANH_TINH)) == 1
            and la_dai_ca(_header(request), request.app.state.pt.cau_hinh))


def host_hop_le(ch: CauHinhTram, cong: int) -> frozenset[str]:
    """Host trình duyệt được dùng: localhost (cổng tram-api) và tên máy B qua `tailscale serve` (Task 26 bước 7.4)."""
    ds = {f"127.0.0.1:{cong}", f"localhost:{cong}"}
    if ch.ten_may_b:
        ds |= {ch.ten_may_b.lower(), f"{ch.ten_may_b.lower()}:443"}
    return frozenset(ds)


class GiuaAnToan:
    """ASGI thuần: Host lạ → 421 (chống DNS rebinding đọc API); mọi phản hồi mang CSP chặt + header an toàn."""

    def __init__(self, app, *, host: frozenset[str]):
        self.app, self.host = app, host

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        da_gui = False

        async def gui(m):
            nonlocal da_gui
            if m["type"] == "http.response.start":
                hs = [*m.get("headers", []), *HEADER_AN_TOAN]
                if scope["path"].startswith("/api/passkey/") or scope["path"] == "/":
                    hs = [(k, v) for k, v in hs if k.lower() != b"cache-control"]
                    hs.append((b"cache-control", b"no-store"))
                da_gui, m = True, {**m, "headers": hs}
            await send(m)

        host = dict(scope["headers"]).get(b"host", b"").decode("latin-1").lower()
        if host not in self.host:
            return await JSONResponse({"loi": "Host không hợp lệ"}, status_code=421)(scope, receive, gui)
        try:
            await self.app(scope, receive, gui)
        except Exception:
            # ServerErrorMiddleware (ngoài cùng) gửi 500 trần không header; tự gửi trước để có CSP.
            # Ném lại vẫn đúng: nó thấy phản hồi đã bắt đầu nên không gửi lần hai, chỉ ném tiếp cho uvicorn ghi log.
            if not da_gui:
                await JSONResponse({"loi": "Lỗi máy chủ"}, status_code=500)(scope, receive, gui)
            raise


def them_header_an_toan(app: FastAPI, ch: CauHinhTram, *, cong: int) -> None:
    app.add_middleware(GiuaAnToan, host=host_hop_le(ch, cong))
