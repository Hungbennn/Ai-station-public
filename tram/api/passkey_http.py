"""Chặn thân POST trước FastAPI parse: hạn theo tuyến và hạn tổng 5 giây."""
import re
import anyio
from tram.passkey.chinh_sach import TUYEN, TUYEN_TM_TC
from fastapi.responses import JSONResponse


def han_than(path):
    if path.startswith('/api/passkey/'):
        return 65536
    if path.startswith('/api/feature/'):
        return None
    for route, muc in (TUYEN | TUYEN_TM_TC).items():
        pattern = re.sub(r'\{[^}]+\}', '[^/]+', route)
        if muc in ('N', 'P', 'P/R') and re.fullmatch(pattern, path):
            return 1024 * 1024 if route.endswith('/chot') else 65536
    return None


class GioiHanThan:
    def __init__(self, app, han=5):
        self.app, self.han = app, han

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        limit = han_than(scope.get('path', ''))
        if limit is None:
            return await self.app(scope, receive, send)
        raw = bytearray()
        try:
            with anyio.fail_after(self.han):
                while True:
                    m = await receive()
                    if m['type'] == 'http.disconnect':
                        return
                    chunk = m.get('body', b'')
                    if len(raw) + len(chunk) > limit:
                        return await self.loi(413, scope, receive, send)
                    raw.extend(chunk)
                    if not m.get('more_body', False):
                        break
        except TimeoutError:
            return await self.loi(408, scope, receive, send)
        body = bytes(raw)
        delivered = False

        async def nhan():
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {'type':'http.request', 'body':body, 'more_body':False}

        await self.app(scope, nhan, send)

    async def loi(self, status, scope, receive, send):
        await JSONResponse({'loi':'Thân yêu cầu quá lớn hoặc nhận quá hạn'}, status_code=status,
                           headers={'Cache-Control':'no-store'})(scope, receive, send)
