"""Kênh nhận API ghi của dashboard (spec 2 §4 mục 2b, spec 3 §7.3 mục 4, H9). CƠ CHẾ CHƯA CHỐT — chờ spike S6 + N2:
`cach_ly.kenh_ghi = header` (mặc định, lát 2a) giữ hành vi cũ; `unix-socket` → `tram api` nghe THÊM một Unix socket
trong thư mục 0700 của tài khoản trạm (`tailscale serve` trỏ vào đó — N2 kiểm Tailscale có hỗ trợ không), và API ghi
CHỈ nhận yêu cầu đến qua socket đó: header danh tính gửi thẳng TCP 127.0.0.1 (principal thực thi, `tram-kiem`, tiến
trình quản lý thợ) bị 403 dù giả đúng header. Đánh dấu kênh nằm trong `scope` ASGI — client không giả được."""
import asyncio
import threading
from pathlib import Path

from fastapi import Request

KHOA_SCOPE = "tram.kenh"


class KenhUnix:
    """Bọc app cho listener Unix socket: gắn `scope["tram.kenh"] = "unix"`."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            scope = {**scope, KHOA_SCOPE: "unix"}
        await self.app(scope, receive, send)


def kenh_hop_le(request: Request) -> bool:
    return getattr(request.app.state, "kenh_ghi", "header") == "header" or request.scope.get(KHOA_SCOPE) == "unix"


def _server(cfg):
    import uvicorn

    class Server(uvicorn.Server):
        def capture_signals(self):                     # tín hiệu do server TCP giữ; server này dừng theo nó
            from contextlib import nullcontext
            return nullcontext()
    return Server(cfg)


def chay_hai_cong(app, *, host: str, cong: int, socket: Path, dung: threading.Event | None = None) -> None:
    """TCP `host:cong` (đọc + `/api/tho/*`) và Unix socket (dashboard qua `tailscale serve`) trên CÙNG app."""
    import uvicorn
    socket.parent.mkdir(parents=True, exist_ok=True)
    socket.parent.chmod(0o700)
    socket.unlink(missing_ok=True)
    app.state.kenh_ghi = "unix-socket"
    tcp = uvicorn.Server(uvicorn.Config(app, host=host, port=cong, log_level="info", server_header=False))
    uds = _server(uvicorn.Config(KenhUnix(app), uds=str(socket), log_level="info", server_header=False,
                                 lifespan="off"))

    async def chay():
        viec = [asyncio.create_task(tcp.serve()), asyncio.create_task(uds.serve())]
        while not (tcp.should_exit or uds.should_exit or (dung and dung.is_set()) or any(v.done() for v in viec)):
            await asyncio.sleep(0.1)
        tcp.should_exit = uds.should_exit = True
        await asyncio.gather(*viec, return_exceptions=True)
    asyncio.run(chay())


def chay_api(app, *, host: str, cong: int) -> None:
    """`tram api`: theo `cach_ly.kenh_ghi` của `~/.tram/cau-hinh.yaml`."""
    import uvicorn

    from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
    cl = nap_cau_hinh_cach_ly()
    if cl.kenh_ghi == "header":
        uvicorn.run(app, host=host, port=cong, log_level="info", server_header=False)
        return
    chay_hai_cong(app, host=host, cong=cong, socket=cl.duong_socket)
