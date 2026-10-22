import asyncio
import json
import threading
from fastapi import Request
from api_gia import tao_app_gia, DAI_CA
from tram.api.passkey import ghi
from tram.passkey.dich_vu import DichVu


def test_body_som_va_han_tuyet_doi(tmp_path):
    from tram.api.passkey_http import GioiHanThan
    async def run():
        reached = []
        async def endpoint(scope, receive, send):
            reached.append(True)
        app = GioiHanThan(endpoint, han=0.02)
        for chunks, expected in [([b'x'*40000, b'x'*40000], 413), ([b'x', None], 408)]:
            sent = []
            async def receive():
                b = chunks.pop(0)
                if b is None:
                    await asyncio.sleep(.1)
                return {'type':'http.request', 'body':b or b'', 'more_body':bool(chunks)}
            async def send(m): sent.append(m)
            await app({'type':'http','method':'POST','path':'/api/passkey/bat-dau'}, receive, send)
            assert sent[0]['status'] == expected
        assert reached == []
    asyncio.run(co_han(run()))


def test_ceremony_khong_chan_event_loop(tmp_path, monkeypatch):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
    entered, released = threading.Event(), threading.Event()
    def busy(self, *args, **kwargs):
        entered.set()
        assert released.wait(1), 'SQLite/verifier chặn event loop'
        return {'id':'ok'}
    monkeypatch.setattr(DichVu, 'bat_dau', busy)
    async def run():
        scope = {'type':'http','method':'POST','path':'/api/passkey/bat-dau','app':app,
                 'headers':[(k.lower().encode(),v.encode()) for k,v in DAI_CA.items()]}
        async def receive():
            return {'type':'http.request','body':json.dumps({'loai':'phien'}).encode()}
        task = asyncio.create_task(ghi('bat-dau', Request(scope, receive)))
        try:
            await cho_event(entered, task)
            released.set()
            assert (await asyncio.wait_for(task, 2)).status_code == 200
        finally:
            released.set()
            if not task.done(): task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    asyncio.run(co_han(run()))


def test_kho_sqlite_ban_request_khac_van_tien_trien(tmp_path):
    from tram.passkey.kho import mo_kho
    app,_=tao_app_gia(tmp_path,{})
    async def run():
        scope={'type':'http','method':'POST','path':'/api/passkey/bat-dau','app':app,
               'headers':[(k.lower().encode(),v.encode()) for k,v in DAI_CA.items()]}
        async def receive():
            return {'type':'http.request','body':b'{"loai":"phien"}'}
        with mo_kho(app.state.passkey_path) as db:
            db.execute('BEGIN IMMEDIATE')
            task=asyncio.create_task(ghi('bat-dau',Request(scope,receive)))
            await asyncio.sleep(.03)
            assert not task.done()
            db.rollback()
        assert (await asyncio.wait_for(task,1)).status_code == 200
    asyncio.run(co_han(run()))


def test_ngat_client_khong_nhan_doi_giao_dich(tmp_path, monkeypatch):
    from test_passkey_dich_vu import them, login
    from tram.passkey.chinh_sach import rang_buoc
    from tram.passkey.kho import mo_kho
    d=DichVu(tmp_path/'cancel.db','chu','b.test')
    k=them(d); c=login(d,k)['cookie']; body={'ma_thao_tac':'cancel-01'}
    q=login(d,k,'r',c,rang_buoc('/api/passkey/moi',body))['quyen']
    entered, released, finished = threading.Event(), threading.Event(), threading.Event()
    original=DichVu.quan_ly
    def slow(self,*args):
        entered.set()
        assert released.wait(1)
        try: return original(self,*args)
        finally: finished.set()
    monkeypatch.setattr(DichVu,'quan_ly',slow)
    async def run():
        from starlette.concurrency import run_in_threadpool
        task=asyncio.create_task(run_in_threadpool(d.quan_ly,c,q,'moi',body))
        try:
            await cho_event(entered, task)
            task.cancel()
        finally:
            released.set()
            if not task.done(): task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        async with asyncio.timeout(2):
            while not finished.is_set(): await asyncio.sleep(.001)
    asyncio.run(co_han(run()))
    assert d.quan_ly(c,q,'moi',body) == {'da_cap':True,'ma':None}
    with mo_kho(d.path) as db:
        assert db.execute('select count(*) from ket_qua').fetchone()[0] == 1
        assert db.execute('select count(*) from ma').fetchone()[0] == 1


async def co_han(coro):
    async with asyncio.timeout(3):
        return await coro


async def cho_event(event, task):
    async with asyncio.timeout(1):
        while not event.is_set():
            if task.done():
                await task
                raise AssertionError('Task kết thúc trước khi vào worker')
            await asyncio.sleep(.001)
