"""Gọi memory service qua MCP trong bộ nhớ (CHỈ DÙNG TRONG TEST): chạy lifespan (bộ quản lý phiên của SDK), rồi các
yêu cầu HTTP trong CÙNG một vòng sự kiện, rồi dừng. Phần tử là hàm (không phải bộ yêu cầu) thì gọi giữa các yêu cầu."""
import asyncio
import json

from asgi_gia import PhanHoi

ACCEPT = "application/json, text/event-stream"


def rpc(phuong_thuc: str, tham_so: dict | None = None, id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": id, "method": phuong_thuc, "params": tham_so or {}}


def goi_cong_cu(ten: str, doi_so: dict, id: int = 1) -> dict:
    return rpc("tools/call", {"name": ten, "arguments": doi_so}, id)


async def _http(app, method: str, path: str, than, headers: dict) -> PhanHoi:
    body = b"" if than is None else json.dumps(than, ensure_ascii=False).encode()
    hdr = {"host": "127.0.0.1:7710", "accept": ACCEPT, "content-type": "application/json",
           **{k.lower(): v for k, v in headers.items()}}
    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method, "scheme": "http",
             "path": path, "raw_path": path.encode(), "query_string": b"", "root_path": "",
             "headers": [(k.encode("latin-1"), v.encode("latin-1")) for k, v in hdr.items()],
             "client": ("127.0.0.1", 50000), "server": ("127.0.0.1", 7710), "state": {}}
    nhan, gui, xong = [{"type": "http.request", "body": body, "more_body": False}], [], asyncio.Event()

    async def receive():
        if nhan:
            return nhan.pop(0)
        await xong.wait()                                   # chỉ "ngắt kết nối" sau khi đã trả lời xong
        return {"type": "http.disconnect"}

    async def send(m):
        gui.append(m)

    await asyncio.wait_for(app(scope, receive, send), 20)
    xong.set()
    dau = next(m for m in gui if m["type"] == "http.response.start")
    return PhanHoi(dau["status"], {k.decode(): v.decode() for k, v in dau["headers"]},
                   b"".join(m.get("body", b"") for m in gui if m["type"] == "http.response.body"))


async def _phien(app, viec) -> list[PhanHoi]:
    vao, ra = asyncio.Queue(), asyncio.Queue()
    chay = asyncio.create_task(app({"type": "lifespan", "asgi": {"version": "3.0"}, "state": {}}, vao.get, ra.put))
    await vao.put({"type": "lifespan.startup"})
    m = await asyncio.wait_for(ra.get(), 10)
    assert m["type"] == "lifespan.startup.complete", m
    kq = []
    try:
        for v in viec:
            if callable(v):
                v()
            else:
                kq.append(await _http(app, *v))
    finally:
        await vao.put({"type": "lifespan.shutdown"})
        await asyncio.wait_for(ra.get(), 10)
        await asyncio.wait_for(chay, 10)
    return kq


def goi_mcp(app, *viec) -> list[PhanHoi]:
    """`viec`: (method, path, than | None, headers) hoặc hàm không đối số. Trả phản hồi theo thứ tự yêu cầu."""
    return asyncio.run(_phien(app, viec))


def ket_qua(r: PhanHoi) -> dict:
    """`result` của phản hồi JSON-RPC (status 200)."""
    assert r.status == 200, (r.status, r.body[:300])
    d = r.json()
    assert "result" in d, d
    return d["result"]


def van_ban(r: PhanHoi) -> tuple[bool, str]:
    """(isError, nội dung chữ) của tools/call."""
    kq = ket_qua(r)
    return kq.get("isError", False), "\n".join(c["text"] for c in kq["content"] if c["type"] == "text")
