import asyncio
import pytest
from test_passkey_http_v1 import test_ngat_client_khong_nhan_doi_giao_dich as chay_ngat


def test_threadpool_loi_truoc_entered_khong_treo(tmp_path, monkeypatch):
    import starlette.concurrency
    async def hong(*args):
        raise ValueError('threadpool chưa khởi động')
    monkeypatch.setattr(starlette.concurrency, 'run_in_threadpool', hong)
    run = asyncio.run
    monkeypatch.setattr(asyncio, 'run', lambda coro: run(asyncio.wait_for(coro, .2)))
    with pytest.raises(ValueError, match='threadpool chưa khởi động'):
        chay_ngat(tmp_path, monkeypatch)
