import pytest
from api_gia import tao_app_gia, DAI_CA, MAY_B, LOGIN
from asgi_gia import goi
from tram.passkey.chinh_sach import TUYEN, TUYEN_TM_TC, rang_buoc
from tram.passkey.dich_vu import DichVu
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes


def test_du_tuyen_head_va_tm_tc(tmp_path):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
    ds = {p for p, methods in app.openapi()['paths'].items() if 'post' in methods and '/passkey/' not in p}
    tm_tc = {
        '/api/du-an/{ten}/tu-dong/cai-dat', '/api/du-an/{ten}/tu-dong/tam-dung',
        '/api/du-an/{ten}/tu-dong/tiep-tuc', '/api/tu-dong/tam-dung', '/api/tu-dong/tiep-tuc',
        '/api/du-an/{ten}/tu-dong/deploy', '/api/du-an/{ten}/tu-cap-nhat',
    }
    assert ds == set(TUYEN) | tm_tc and len(ds) == 30
    assert set(TUYEN_TM_TC) == tm_tc


@pytest.mark.parametrize('path,muc', list(TUYEN.items()))
def test_tuyen_ghi_truoc_dang_ky(tmp_path, path, muc):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
    path = path.replace('{du_an}', 'x').replace('{bead_id}', 'x').replace('{may_id}', 'x').replace('{ten}', 'x')
    r = goi(app, 'POST', path, json_body={}, headers=DAI_CA)
    if muc in ('N', 'P') and path not in ('/api/chu/estop', '/api/feature/yeu-cau/xem'):
        assert r.status == 403
    else:
        assert r.status != 200  # payload trống / máy thiếu token, không có side effect


def test_cookie_va_login_sai(tmp_path):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
    dv = DichVu(tmp_path/'pk.db', LOGIN, MAY_B)
    app.state.passkey_path = dv.path
    k = KhoaGia()
    def post(path, body, headers=DAI_CA):
        return goi(app, 'POST', '/api/passkey/'+path, json_body=body, headers=headers)
    o = post('bat-dau', {'loai':'dang-ky', 'ma':dv.cap_ma()}).json()
    a = k.tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True, rp=MAY_B, origin='https://'+MAY_B)
    assert post('ket-thuc', {'id':o['id'], 'credential':a, 'ten':'A'}).status == 200
    o = post('bat-dau', {'loai':'phien'}).json()
    a = k.tra(base64url_to_bytes(o['publicKey']['challenge']), rp=MAY_B, origin='https://'+MAY_B)
    r = post('ket-thuc', {'id':o['id'], 'credential':a})
    ck = r.headers['set-cookie']
    for flag in ('HttpOnly', 'Secure', 'SameSite=strict', 'Max-Age=28800', 'Path=/'):
        assert flag in ck
    assert 'Domain' not in ck and 'cookie' not in r.json()
    assert r.headers['cache-control'] == 'no-store'
    h = {**DAI_CA, 'Cookie':ck.split(';')[0]}
    assert goi(app,'GET','/api/passkey/trang-thai',headers=h).json()['con_giay'] > 0
    assert post('bat-dau',{'loai':'phien'}, {**h,'Tailscale-User-Login':'khac'}).status == 403
    assert post('bat-dau',{'loai':'phien'}, {**h,'Origin':'https://gia'}).status == 403
    assert post('bat-dau',{'loai':'phien'}, {**h,'Host':'gia'}).status == 421
    bad = post('ket-thuc', {'id': 'marker-secret', 'credential':{}})
    assert 'marker-secret' not in bad.body.decode()


def test_rang_buoc_khong_doi_payload():
    a = rang_buoc('/api/x', {'ma_thao_tac':'a','x':1})
    assert a == rang_buoc('/api/x', {'x':1,'ma_thao_tac':'a'})
    assert a != rang_buoc('/api/x', {'x':2,'ma_thao_tac':'a'})
    assert a != rang_buoc('/api/y', {'x':1,'ma_thao_tac':'a'})


def test_get_trinh_duyet_khong_co_origin(tmp_path):
    app, _ = tao_app_gia(tmp_path,{}, co_passkey=False)
    r = goi(app,'GET','/api/passkey/trang-thai',headers={'Tailscale-User-Login':LOGIN})
    assert r.status == 200
    assert r.headers['cache-control'] == 'no-store'
