import concurrent.futures
import sqlite3
import pytest
from test_passkey_dich_vu import dv, them, login
from passkey_gia import KhoaGia
from tram.passkey.kho import mo_kho, TuChoi
from tram.su_kien.phien_ban import nang_cap, LoiPhienBan
from webauthn.helpers import base64url_to_bytes
from api_gia import tao_app_gia, DAI_CA, LOGIN, MAY_B
from asgi_gia import goi


def test_migration_loi_giu_schema_version_va_backup(tmp_path):
    p = tmp_path/'pk.db'
    with mo_kho(p) as db:
        before = db.execute('SELECT sql FROM sqlite_master ORDER BY name').fetchall()
        with pytest.raises(LoiPhienBan):
            nang_cap(db, thu_muc_sao_luu=tmp_path/'backup', moi=2,
                     buoc={2:('CREATE TABLE tam(id INT)', 'INVALID SQL')})
        assert db.execute('pragma user_version').fetchone()[0] == 1
        assert db.execute('SELECT sql FROM sqlite_master ORDER BY name').fetchall() == before
    backups = list((tmp_path/'backup').glob('*.db'))
    assert len(backups) == 1
    with sqlite3.connect(backups[0]) as db:
        assert db.execute('pragma user_version').fetchone()[0] == 1
        assert not db.execute("SELECT 1 FROM sqlite_master WHERE name='tam'").fetchone()


@pytest.mark.parametrize('loai', ['phien', 'r'])
def test_cung_assertion_dong_thoi_chi_mot_quyen(dv, loai):
    k = them(dv)
    c = login(dv,k)['cookie']
    o = dv.bat_dau(loai, cookie=c, rang='target')
    assertion = k.tra(base64url_to_bytes(o['publicKey']['challenge']))
    def go(_):
        try: return dv.ket_thuc(o['id'], assertion)
        except TuChoi: return None
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        results = list(pool.map(go, range(2)))
    assert sum(r is not None for r in results) == 1


def test_challenge_het_120_khi_ma_con_han(dv):
    m = dv.cap_ma()
    o = dv.bat_dau('dang-ky', ma=m)
    dv.clock[0] += 120
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], KhoaGia().tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True))
    assert dv.bat_dau('dang-ky', ma=m)['id'] != o['id']


@pytest.mark.parametrize('dang_ky', [True, False])
def test_up_0_khong_cap_quyen(dv, dang_ky):
    k = KhoaGia() if dang_ky else them(dv)
    o = dv.bat_dau('dang-ky',ma=dv.cap_ma()) if dang_ky else dv.bat_dau('phien')
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=dang_ky, up=False))


def test_ma_passkey_khong_doi_token_http(tmp_path):
    from tram.passkey.dich_vu import DichVu
    from tram.phieu.kho import KhoPhieu
    app, pt = tao_app_gia(tmp_path, {})
    pt.mo_kho_phieu = lambda: KhoPhieu(tmp_path/'phieu.db')
    ma = DichVu(app.state.passkey_path, LOGIN, MAY_B).cap_ma()
    r = goi(app,'POST','/api/ghep-may',json_body={'ma':ma})
    assert r.status == 403 and 'token' not in r.json()


@pytest.mark.parametrize('path,extra', [
    ('/api/bead/hr/hr-1/chot', {'tra_loi':['đồng ý']}),
    ('/api/phe-duyet/hr/hr-1/duyet', {}),
    ('/api/phe-duyet/hr/hr-1/tra-loi', {'tra_loi':'đồng ý'}),
    ('/api/chu/tiep-tuc', {}),
    ('/api/khe/B/main/bat', {}),
    ('/api/khe/B/main/cau-dao-dong', {}),
    ('/api/nho/xoa', {'id':'x'}),
])
def test_route_p_that_thieu_cookie_khong_ghi(tmp_path, monkeypatch, path, extra):
    app, pt = tao_app_gia(tmp_path,{})
    calls=[]
    def forbidden(*args, **kwargs):
        calls.append(1)
        pytest.fail('Không được mở kho nghiệp vụ')
    for name in ('mo_kho','mo_kho_tt','mo_kho_phieu','tao_bd'):
        monkeypatch.setattr(pt,name,forbidden)
    from tram.api.than import ThanGhi, ThanChot, ThanDuyet, ThanTraLoi, ThanNhoXoa
    from tram.api.doi_ngu import ThanKhe
    cls={'chot':ThanChot,'duyet':ThanDuyet,'tra-loi':ThanTraLoi,'xoa':ThanNhoXoa,'bat':ThanKhe}
    body={'ma_thao_tac':'v1-p-001','expected_version':'', **extra}
    cls.get(path.rsplit('/',1)[-1],ThanGhi).model_validate(body)
    r=goi(app,'POST',path,headers={**DAI_CA,'Cookie':''},json_body=body)
    assert r.status == 403 and r.json()['detail'] == 'Cần phiên passkey'
    assert calls == []


def test_moi_retry_phien_moi_khong_huy_ma_cu(dv):
    from tram.passkey.chinh_sach import rang_buoc
    from tram.passkey.thao_tac import XungDotMa
    k=them(dv)
    than={'ma_thao_tac':'moi-01'}
    rang=rang_buoc('/api/passkey/moi',than)
    c=login(dv,k)['cookie']; q=login(dv,k,'r',c,rang)['quyen']
    first=dv.quan_ly(c,q,'moi',than)
    c2=login(dv,k)['cookie']; q2=login(dv,k,'r',c2,rang)['quyen']
    assert dv.quan_ly(c2,q2,'moi',than) == {'da_cap':True,'ma':None}
    them(dv,first['ma'])
    assert dv.quan_ly(c2,q2,'moi',than) == {'da_cap':True,'ma':None}
    with mo_kho(dv.path) as db:
        assert db.execute('select count(*) from ket_qua').fetchone()[0] == 1
        assert db.execute('select count(*) from ma').fetchone()[0] == 0
    changed={**than,'khac':True}
    q3=login(dv,k,'r',c2,rang_buoc('/api/passkey/moi',changed))['quyen']
    with pytest.raises(XungDotMa): dv.quan_ly(c2,q3,'moi',changed)


def test_quan_ly_bi_tu_choi_khong_giu_ma(dv):
    from tram.passkey.chinh_sach import rang_buoc
    k=them(dv); c=login(dv,k)['cookie']
    body={'ma_thao_tac':'moi-02'}
    with pytest.raises(TuChoi): dv.quan_ly(c,'gia','moi',body)
    with mo_kho(dv.path) as db:
        assert db.execute('select count(*) from thao_tac').fetchone()[0] == 0
        assert db.execute('select count(*) from ket_qua').fetchone()[0] == 0


def test_marker_khong_ro_qua_loi_su_kien_telegram(tmp_path, caplog, capsys):
    from datetime import datetime, timezone
    from tram.passkey.dich_vu import DichVu
    from tram.bao_tin.passkey import gui_cho
    app, pt=tao_app_gia(tmp_path,{},co_passkey=False)
    app.state.passkey_path=tmp_path/'pk.db'
    d=DichVu(app.state.passkey_path,LOGIN,MAY_B)
    marker='V1-PRIVATE-MARKER-7f2a'
    ma=d.cap_ma()
    k=KhoaGia()
    o=d.bat_dau('dang-ky',ma=ma)
    cred=k.tra(base64url_to_bytes(o['publicKey']['challenge']),dang_ky=True,rp=MAY_B,origin='https://'+MAY_B)
    r=goi(app,'POST','/api/passkey/ket-thuc',headers=DAI_CA,
          json_body={'id':o['id'],'credential':cred,'ten':marker})
    assert r.status == 200
    # Nhánh schema và verifier; credential ID hợp lệ để lỗi đi tới verifier thật.
    o = d.bat_dau('phien')
    bad = k.tra(base64url_to_bytes(o['publicKey']['challenge']), rp=MAY_B, origin='https://'+MAY_B)
    bad['response']['signature'] = marker
    for body in ({'credential':marker}, {'id':o['id'], 'credential':bad}):
        r=goi(app,'POST','/api/passkey/ket-thuc',headers=DAI_CA,json_body=body)
        assert r.status in (403,422) and marker not in r.body.decode()
    sent=[]
    assert gui_cho(d.path,None,datetime.now(timezone.utc),sent.append) == 1
    with mo_kho(d.path) as db:
        events=repr([tuple(row) for row in db.execute('select * from tin')])
    out=capsys.readouterr()
    assert marker not in caplog.text+out.out+out.err+events+repr(sent)
    assert ma not in caplog.text+out.out+out.err+events+repr(sent)
    from contextlib import closing
    with closing(pt.mo_kho()) as kho:
        assert marker not in repr(kho.gan_day('_tram',None,100))
