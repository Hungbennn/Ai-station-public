import asyncio
import json
import pytest
from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from tram.api.than import ThanChot


def raw_app(app, raw, *, slow=False):
    async def wrapped(scope, receive, send):
        scope = {**scope, 'headers': [*scope['headers'], (b'content-type', b'application/json')]}
        async def nhan():
            if slow:
                await asyncio.sleep(.05)
            return {'type':'http.request', 'body':raw, 'more_body':False}
        await app(scope, nhan, send)
    wrapped.state = getattr(app, 'state', None)
    return wrapped


@pytest.mark.parametrize('char,escaped', [('a',False), ('ệ',False), ('😀',True)])
def test_chot_max_schema_qua_ca_hai_lop(tmp_path, char, escaped):
    app, pt = tao_app_gia(tmp_path,{})
    pt.cac_du_an=lambda:['hr']; pt.bat_ghi=lambda _:False
    body={'ma_thao_tac':'v2-chot-max','expected_version':'','tra_loi':[char*4000]*20}
    ThanChot.model_validate(body)
    raw=json.dumps(body,ensure_ascii=escaped).encode()
    assert 65536 < len(raw) < 1024*1024
    r=goi(raw_app(app,raw),'POST','/api/bead/hr/hr-1/chot',headers=DAI_CA)
    assert r.status == 422 and 'bat_ghi: false' in r.json()['loi']


@pytest.mark.parametrize('path,limit',[('/api/passkey/bat-dau',65536),('/api/bead/hr/hr-1/chot',1048576)])
def test_han_tren_app_truoc_parse(tmp_path,path,limit):
    app,_=tao_app_gia(tmp_path,{})
    assert goi(raw_app(app,b' '*limit),'POST',path,headers=DAI_CA).status == 422
    r=goi(raw_app(app,b' '*(limit+1)),'POST',path,headers=DAI_CA)
    assert r.status == 413 and r.headers['cache-control']=='no-store'
    from tram.api.passkey_http import GioiHanThan
    limited=GioiHanThan(app,han=.01)
    assert goi(raw_app(limited,b'{}',slow=True),'POST',path,headers=DAI_CA).status == 408


def test_phieu_hop_le_tren_64k_khong_bi_chan(tmp_path):
    from api_yeu_cau_gia import mo_app, than, XEM, TAO, dau
    app,_,bd,_=mo_app(tmp_path)
    for path,body in [(XEM,than()),(TAO,{**than(),'dau_xem':dau()})]:
        raw=json.dumps(body).encode()+b' '*70000
        r=goi(raw_app(app,raw),'POST',path,headers=DAI_CA)
        assert r.status == (200 if path==XEM else 201)
    assert bd.so_lan_tao()==1


def test_bao_tho_hop_le_tren_64k(tmp_path):
    from tho_api_gia import tao_tram
    from tram.phieu.bao import ThanBao
    t=tao_tram(tmp_path)
    # moc không có ban_giao, chuỗi giao_id hợp lệ nhưng không tồn tại: cửa nghiệp vụ 409.
    body={'khe_id':'B/claude-1','giao_id':'khong-co','luot':1,'loai':'moc','request_id':'body-v2-001'}
    ThanBao.model_validate(body)
    raw=json.dumps(body).encode()+b' '*70000
    r=goi(raw_app(t.app,raw),'POST','/api/tho/bao',headers={'Authorization':'Bearer '+t.token['B']})
    assert r.status == 409 and r.json() == {'ly_do':'luot-cu'}
