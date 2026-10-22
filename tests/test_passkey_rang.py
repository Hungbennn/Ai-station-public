import pytest
from fastapi import FastAPI, Depends
from api_gia import tao_pt, DAI_CA, LOGIN, MAY_B
from asgi_gia import goi
from tram.api.bao_mat import yeu_cau_ghi
from tram.passkey.dich_vu import DichVu
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes


def test_cung_ma_khac_payload_409(tmp_path):
    app = FastAPI(); app.state.pt = tao_pt(tmp_path,{})
    app.state.passkey_path = tmp_path/'pk.db'
    calls = []
    @app.post('/api/nho/ghi',dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        calls.append(1)
        return {'ok':True}
    dv = DichVu(app.state.passkey_path, LOGIN, MAY_B)
    k = KhoaGia(); o = dv.bat_dau('dang-ky',ma=dv.cap_ma())
    dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                             dang_ky=True,rp=MAY_B,origin='https://'+MAY_B))
    body = {'ma_thao_tac':'m','noi_dung':'mot'}
    assert goi(app,'POST','/api/nho/ghi',headers=DAI_CA,json_body=body).status == 200
    assert goi(app,'POST','/api/nho/ghi',headers=DAI_CA,json_body={**body,'noi_dung':'hai'}).status == 409
    assert len(calls) == 1


def test_loi_xac_thuc_khong_cache(tmp_path):
    from api_gia import tao_app_gia
    app,_ = tao_app_gia(tmp_path,{}, co_passkey=False)
    r = goi(app,'POST','/api/passkey/bat-dau',json_body={'ma':'marker'})
    assert r.status == 403 and r.headers['cache-control'] == 'no-store'
