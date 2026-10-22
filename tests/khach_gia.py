"""`KhachTram` gọi thẳng tram-api trong bộ nhớ (CHỈ DÙNG TRONG TEST) — thay `urllib.request.urlopen` bằng ASGI."""
import io
import json
import urllib.error

from asgi_gia import goi
from tram.tho.khach import KhachTram


class _TraLoi:
    def __init__(self, status: int, body: bytes):
        self.status, self._body = status, body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def khach_asgi(app, token: str) -> KhachTram:
    def mo(yc, timeout=None):
        duong = yc.full_url.removeprefix("http://127.0.0.1:7700")
        than = json.loads(yc.data) if yc.data else None
        h = {k: v for k, v in yc.header_items()}
        r = goi(app, yc.get_method(), duong, json_body=than, headers=h)
        if r.status >= 400:
            raise urllib.error.HTTPError(yc.full_url, r.status, "loi", {}, io.BytesIO(r.body))
        return _TraLoi(r.status, r.body)
    return KhachTram("http://127.0.0.1:7700", token, mo=mo)
