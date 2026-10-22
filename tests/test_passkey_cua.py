import pytest
from types import SimpleNamespace
from fastapi import FastAPI, Depends, Request
from api_gia import tao_pt, DAI_CA, LOGIN, MAY_B
from asgi_gia import goi
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes
from tram.api.bao_mat import yeu_cau_ghi
from tram.passkey.chinh_sach import TUYEN
from tram.passkey.dich_vu import DichVu


@pytest.mark.parametrize('path,muc', [(p,m) for p,m in TUYEN.items() if m in ('N','P')])
def test_moi_tuyen_n_p_thieu_dung_het_phien(tmp_path,path,muc):
    app = FastAPI()
    app.state.pt = tao_pt(tmp_path,{})
    app.state.passkey_path = tmp_path/'pk.db'
    calls = []
    @app.post(path,dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        calls.append(1)
        return {'da_ghi':True}
    url = path.replace('{du_an}','x').replace('{bead_id}','x').replace('{may_id}','x').replace('{ten}','x')
    dv = DichVu(app.state.passkey_path,LOGIN,MAY_B)
    k = KhoaGia()
    o = dv.bat_dau('dang-ky',ma=dv.cap_ma())
    dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                             dang_ky=True,rp=MAY_B,origin='https://'+MAY_B))
    r = goi(app,'POST',url,headers=DAI_CA,json_body={})
    assert r.status == (403 if muc == 'P' else 200)
    assert len(calls) == (0 if muc == 'P' else 1)
    o = dv.bat_dau('phien')
    c = dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                                rp=MAY_B,origin='https://'+MAY_B))['cookie']
    hs = {**DAI_CA,'Cookie':'__Host-tram-phien='+c}
    assert goi(app,'POST',url,headers=hs,json_body={}).status == 200
    before = len(calls)
    for headers in ({}, {**hs,'Tailscale-User-Login':'gia'}, {**hs,'Origin':'https://gia'},
                    {**hs,'X-Tram':'0'}):
        assert goi(app,'POST',url,headers=headers,json_body={}).status == 403
    assert len(calls) == before
    from tram.passkey.kho import mo_kho,giao_dich
    with mo_kho(dv.path) as db,giao_dich(db):
        db.execute('UPDATE phien SET han=0')
    assert goi(app,'POST',url,headers=hs,json_body={}).status == (403 if muc == 'P' else 200)


def test_ghi_la_dong_mac_dinh(tmp_path):
    app=FastAPI(); app.state.pt=tao_pt(tmp_path,{})
    @app.post('/api/la',dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        pytest.fail('không chạy nghiệp vụ')
    assert goi(app,'POST','/api/la',headers=DAI_CA,json_body={}).status == 403
