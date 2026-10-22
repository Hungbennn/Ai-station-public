"""Gọi một ứng dụng ASGI trong bộ nhớ — thay TestClient để khỏi thêm httpx (spec §8)."""
import asyncio
import json as _json
from dataclasses import dataclass


@dataclass
class PhanHoi:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self):
        return _json.loads(self.body)


def goi(app, phuong_thuc: str, duong_dan: str, *, json_body=None, headers: dict | None = None) -> PhanHoi:
    path, _, query = duong_dan.partition("?")
    body = b"" if json_body is None else _json.dumps(json_body, ensure_ascii=False).encode()
    hdr = {"host": "127.0.0.1:7700"}
    if (ck := getattr(getattr(app, "state", None), "cookie_test", None)):
        hdr["cookie"] = ck
    if json_body is not None:
        hdr["content-type"] = "application/json"
    hdr.update({k.lower(): v for k, v in (headers or {}).items()})
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": phuong_thuc, "scheme": "http", "path": path, "raw_path": path.encode(),
        "query_string": query.encode(), "root_path": "",
        "headers": [(k.encode("latin-1"), v.encode("latin-1")) for k, v in hdr.items()],
        "client": ("127.0.0.1", 50000), "server": ("127.0.0.1", 7700),
    }
    nhan = [{"type": "http.request", "body": body, "more_body": False}]
    gui: list[dict] = []

    async def receive():
        return nhan.pop(0) if nhan else {"type": "http.disconnect"}

    async def send(m):
        gui.append(m)

    asyncio.run(app(scope, receive, send))
    dau = next(m for m in gui if m["type"] == "http.response.start")
    return PhanHoi(dau["status"], {k.decode(): v.decode() for k, v in dau["headers"]},
                   b"".join(m.get("body", b"") for m in gui if m["type"] == "http.response.body"))
