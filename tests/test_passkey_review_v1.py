from api_gia import DAI_CA, LOGIN, MAY_B, tao_app_gia
from asgi_gia import goi
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from tram.chu import estop
from tram.passkey.dich_vu import DichVu


def test_quan_ly_cung_ma_khac_thiet_bi_phai_409(tmp_path):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
    app.state.passkey_path = tmp_path / 'pk.db'
    dv = DichVu(app.state.passkey_path, LOGIN, MAY_B)
    keys = [KhoaGia(), KhoaGia(), KhoaGia()]
    for k in keys:
        o = dv.bat_dau('dang-ky', ma=dv.cap_ma())
        dv.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                    dang_ky=True, rp=MAY_B, origin='https://' + MAY_B))
    o = dv.bat_dau('phien')
    c = dv.ket_thuc(o['id'], keys[0].tra(base64url_to_bytes(o['publicKey']['challenge']),
                    rp=MAY_B, origin='https://' + MAY_B))['cookie']
    hs = {**DAI_CA, 'Cookie': '__Host-tram-phien=' + c}

    def post(viec, body):
        return goi(app, 'POST', '/api/passkey/' + viec, json_body=body, headers=hs)

    def xac_nhan(than):
        r = post('bat-dau', {'loai': 'r', 'duong': '/api/passkey/thu-hoi', 'than': than})
        assert r.status == 200
        o = r.json()
        r = post('ket-thuc', {'id': o['id'], 'credential': keys[0].tra(
            base64url_to_bytes(o['publicKey']['challenge']), rp=MAY_B, origin='https://' + MAY_B)})
        assert r.status == 200
        return r.json()['quyen']

    a = {'ma_thao_tac': 'review-cung-ma-01', 'id': bytes_to_base64url(keys[1].id)}
    b = {**a, 'id': bytes_to_base64url(keys[2].id)}
    qa, qb = xac_nhan(a), xac_nhan(b)
    assert post('thu-hoi', {'than': a, 'quyen': qa}).status == 200
    assert post('thu-hoi', {'than': a, 'quyen': qa}).status == 200
    assert post('thu-hoi', {'than': b, 'quyen': qb}).status == 409
    assert len(dv.trang_thai(c)['thiet_bi']) == 2


def test_estop_khong_can_mo_kho_passkey(tmp_path, monkeypatch):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)

    def kho_hong(self):
        raise AssertionError('Estop không được phụ thuộc kho passkey')

    monkeypatch.setattr(DichVu, 'mo', kho_hong)
    r = goi(app, 'POST', '/api/chu/estop', headers=DAI_CA,
            json_body={'ma_thao_tac': 'review-estop-01', 'expected_version': '', 'ly_do': 'Dừng'})
    assert r.status == 200
    assert estop.dang_bat()

    r2 = goi(app, 'POST', '/api/chu/estop', headers=DAI_CA,
             json_body={'ma_thao_tac': 'review-estop-01', 'expected_version': '', 'ly_do': 'Dừng'})
    assert r2.status == 200 and r2.json()['lap_lai'] is True
    for hs in ({}, {**DAI_CA, 'Origin':'https://gia'}, {**DAI_CA,'X-Tram':'0'}):
        assert goi(app,'POST','/api/chu/estop',headers=hs,
                   json_body={'ma_thao_tac':'review-estop-02','expected_version':'','ly_do':'Dừng'}).status == 403
