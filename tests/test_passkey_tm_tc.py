"""Ghép D138/D140: phiên/chữ ký thật, ledger TM/TC thật, không override cửa quyền."""
from contextlib import closing
from copy import deepcopy
import concurrent.futures
import pytest
from api_gia import tao_app_gia, DAI_CA, LOGIN, MAY_B
from asgi_gia import goi
from bd_gia import BdGia
from passkey_gia import KhoaGia
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import mo_kho, giao_dich
from tram.passkey.chinh_sach import rang_buoc
from tram.tu_dong.cai_dat import CaiDatTuDong, sang_api
from tram.tu_dong.luu import doi_cai_dat, doc_cai_dat
from webauthn.helpers import base64url_to_bytes

CD = '/api/du-an/hr/tu-dong/cai-dat'
TC = '/api/du-an/hr/tu-cap-nhat'
P = ['/api/du-an/hr/tu-dong/tiep-tuc', '/api/tu-dong/tiep-tuc',
     '/api/du-an/hr/tu-dong/deploy', TC, CD]


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    monkeypatch.setattr("tram.thao_tac.tu_dong.can_duong", lambda *a: None)
    app, pt = tao_app_gia(tmp_path, {'hr': BdGia()}, co_passkey=False)
    pt.bat_ghi = lambda _: True
    dv = DichVu(tmp_path/'pk.db', LOGIN, MAY_B)
    app.state.passkey_path = dv.path
    k = KhoaGia()
    def ceremony(loai, **kw):
        o = dv.bat_dau(loai, **kw)
        return dv.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                          dang_ky=loai == 'dang-ky', rp=MAY_B, origin='https://'+MAY_B))
    ceremony('dang-ky', ma=dv.cap_ma())
    c = ceremony('phien')['cookie']
    h = {**DAI_CA, 'Cookie':'__Host-tram-phien='+c}
    def r(path, body):
        return {**h, 'X-Tram-Xac-Nhan':ceremony('r', cookie=c, rang=rang_buoc(path, body))['quyen']}
    return app, pt, dv, c, h, r


def body(ma='tm-passkey-001', version='0', **doi):
    return {'ma_thao_tac':ma, 'expected_version':version,
            'cai_dat':sang_api(CaiDatTuDong(**doi))}


def gui(app, path, b, h):
    return goi(app, 'POST', path, json_body=b, headers=h)


@pytest.mark.parametrize('path', P)
def test_p_khong_cookie_bi_chan_truoc_kho(ctx, monkeypatch, path):
    app, pt, *_ = ctx
    def cam(): pytest.fail('Không được mở kho nghiệp vụ')
    monkeypatch.setattr(pt, 'mo_kho', cam)
    b = body() if path == CD else {'ma_thao_tac':'tm-passkey-001','expected_version':''}
    assert gui(app,path,b,{**DAI_CA,'Cookie':''}).json()['detail'] == 'Cần phiên passkey'


@pytest.mark.parametrize('path', ['/api/du-an/hr/tu-dong/tam-dung','/api/tu-dong/tam-dung'])
def test_n_tam_dung_chua_dang_ky_va_kho_passkey_hong(tmp_path, path):
    app, pt = tao_app_gia(tmp_path, {'hr':BdGia()}, co_passkey=False)
    app.state.passkey_path = tmp_path/'hong.db'
    app.state.passkey_path.write_text('khong phai sqlite')
    b = {'ma_thao_tac':'tm-stop-001','expected_version':''}
    assert gui(app,path,b,DAI_CA).status == 200
    assert gui(app,path,b,DAI_CA).json()['lap_lai'] is True
    assert gui(app,path,b,{**DAI_CA,'Origin':'https://sai'}).status == 403


@pytest.mark.parametrize('doi', [{'tu_merge':True},{'dk_ci':False},{'dk_cot':False},{'dk_hang_rao':False}])
def test_cai_dat_p_cookie_tren_header(ctx, doi):
    app, pt, dv, c, h, r = ctx
    assert gui(app,CD,body(**doi),h).status == 200


@pytest.mark.parametrize('doi', [{'lenh_deploy':'deploy.sh'}, {'lenh_kiem_song':'song.sh'}, {'lenh_lui':'lui.sh'},
    {'tu_deploy':True,'lenh_deploy':'d.sh','lenh_kiem_song':'k.sh','lenh_lui':'l.sh'}])
def test_r_cookie_khong_du_ky_dung_retry_mot_lan(ctx, doi):
    app, pt, dv, c, h, r = ctx
    b = body(**doi)
    assert gui(app,CD,b,h).status == 403
    hr = r(CD,b)
    assert gui(app,CD,b,hr).status == 200
    with mo_kho(dv.path) as db, giao_dich(db):
        db.execute('UPDATE quyen SET han=0')
    # Kết quả cũ vẫn cần phiên, nhưng không cần chạm lại dù R hết hạn.
    assert gui(app,CD,b,h).json()['lap_lai'] is True
    assert gui(app,CD,b,{**h,'Cookie':''}).status == 403
    with closing(pt.mo_kho()) as kho:
        assert kho.db.execute("SELECT count(*) FROM su_kien WHERE loai='tu_dong.cai_dat'").fetchone()[0] == 1


@pytest.mark.parametrize('sai', ['path','payload','ma','version'])
def test_r_sai_rang_buoc_khong_ghi(ctx, sai):
    app, pt, dv, c, h, r = ctx
    b = body(lenh_deploy='d.sh'); ky = deepcopy(b)
    if sai == 'payload': ky['cai_dat']['tu_merge'] = True
    if sai == 'ma': ky['ma_thao_tac'] = 'ma-khac-001'
    if sai == 'version': ky['expected_version'] = '99'
    hr = r(CD+'/khac' if sai == 'path' else CD, ky)
    assert gui(app,CD,b,hr).status == 403
    with closing(pt.mo_kho_tt()) as kt: assert kt.lay(b['ma_thao_tac']) is None


def test_ma_khac_noi_dung_409_va_retry_sau_loi_phai_kiem_r(ctx, monkeypatch):
    app, pt, dv, c, h, r = ctx
    b = body(lenh_deploy='d.sh'); hr = r(CD,b)
    from tram.tu_dong import luu
    original = luu.doi_cai_dat
    monkeypatch.setattr('tram.thao_tac.tu_dong.doi_cai_dat', lambda *a, **kw: (_ for _ in ()).throw(ValueError('loi gia')))
    with pytest.raises(ValueError, match='loi gia'): gui(app,CD,b,hr)
    monkeypatch.setattr('tram.thao_tac.tu_dong.doi_cai_dat', original)
    with mo_kho(dv.path) as db, giao_dich(db): db.execute('UPDATE quyen SET han=0')
    assert gui(app,CD,b,hr).status == 403
    assert gui(app,CD,b,r(CD,b)).status == 200
    changed = body(lenh_deploy='khac.sh')
    assert gui(app,CD,changed,r(CD,changed)).status == 409


@pytest.mark.parametrize('loai',['het-phien','thu-hoi','login'])
def test_retry_da_xong_van_kiem_phien_va_danh_tinh(ctx, loai):
    app, pt, dv, c, h, r = ctx
    b = body(lenh_deploy='d.sh')
    assert gui(app,CD,b,r(CD,b)).status == 200
    if loai == 'login': h = {**h,'Tailscale-User-Login':'khac@example.com'}
    else:
        with mo_kho(dv.path) as db, giao_dich(db):
            if loai == 'het-phien': db.execute('UPDATE phien SET han=0')
            else: db.execute('UPDATE khoa SET thu=1')
    assert gui(app,CD,b,h).status == 403


def test_tc_cookie_tat_chinh_va_tiep_tuc(ctx):
    app, pt, dv, c, h, r = ctx
    b = {'ma_thao_tac':'tc-passkey-001','expected_version':'0',
         'cai_dat':{'bat':True,'tien_do':True,'viec_moi':True,'bi_chan':True}}
    out = gui(app,TC,b,h)
    assert out.status == 200
    assert gui(app,TC,b,h).json()['lap_lai'] is True
    v = out.json()['ket_qua']['tu_cap_nhat.cai_dat']['phien_ban']
    b.update(ma_thao_tac='tc-passkey-002',expected_version=v)
    b['cai_dat'].update(bat=False,tien_do=False)
    assert gui(app,TC,b,h).status == 200
    for i,path in enumerate(P[:2]):
        assert gui(app,path,{'ma_thao_tac':f'tiep-tuc-00{i}','expected_version':''},h).status == 200


def test_r_dong_thoi_va_tat_deploy_chi_can_p(ctx):
    app, pt, dv, c, h, r = ctx
    b = body(tu_deploy=True,lenh_deploy='d.sh',lenh_kiem_song='k.sh',lenh_lui='l.sh'); hr = r(CD,b)
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        rs = list(pool.map(lambda _:gui(app,CD,b,hr), range(2)))
    assert [x.status for x in rs] == [200,200]
    assert sorted(x.json()['lap_lai'] for x in rs) == [False,True]
    with closing(pt.mo_kho()) as kho: cd,v = doc_cai_dat(kho.db,'hr')
    b2 = body('tm-passkey-002',v,lenh_deploy='d.sh',lenh_kiem_song='k.sh',lenh_lui='l.sh')
    assert gui(app,CD,b2,h).status == 200
