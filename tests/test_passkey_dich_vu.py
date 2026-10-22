import concurrent.futures
import pytest
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma, cac_khoa, TuChoi


@pytest.fixture
def dv(tmp_path):
    clock = [100.0]
    d = DichVu(tmp_path/'passkey.db', 'chu', 'b.test', lambda: clock[0])
    d.clock = clock
    return d


def them(d, ma=None):
    k = KhoaGia()
    if ma is None:
        ma = d.cap_ma()
    o = d.bat_dau('dang-ky', ma=ma)
    d.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True), ten='Máy A')
    return k


def login(d, k, loai='phien', cookie='', rang=''):
    o = d.bat_dau(loai, cookie=cookie, rang=rang)
    return d.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge'])))


def test_phien_8_gio_va_login_thu_hoi(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    dv.clock[0] += 28799
    assert dv.trang_thai(c)['con_giay'] == 1
    dv.clock[0] += 1
    assert dv.trang_thai(c)['con_giay'] == 0
    with pytest.raises(TuChoi):
        dv.can_phien(c)
    with pytest.raises(TuChoi):
        DichVu(dv.path, 'khac', dv.rp).trang_thai(c)
    dv.cap_ma(khoi_phuc=True)
    assert dv.trang_thai(c)['thiet_bi'] == []


def test_r_gan_payload_khong_gia_han_va_chan_cuoi(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    dv.clock[0] += 99
    q = login(dv, k, 'r', c, 'thu:1')['quyen']
    with pytest.raises(TuChoi):
        dv.thu_hoi(c, q, 'khac', rang='thu:2')
    with pytest.raises(TuChoi, match='cuối'):
        dv.thu_hoi(c, q, dv.trang_thai(c)['thiet_bi'][0]['id'], rang='thu:1')
    assert dv.trang_thai(c)['con_giay'] == 28701
    k2 = them(dv)
    c2 = login(dv, k2)['cookie']
    target = dv.trang_thai(c)['thiet_bi'][1]['id']
    q = login(dv, k, 'r', c, 'thu:2')['quyen']
    dv.thu_hoi(c, q, target, rang='thu:2')
    with pytest.raises(TuChoi):
        dv.can_phien(c2)


def test_replay_race_ma_va_challenge(dv):
    ma = dv.cap_ma()
    ks = [KhoaGia(), KhoaGia()]
    os = [dv.bat_dau('dang-ky', ma=ma) for _ in ks]
    def go(i):
        try:
            return dv.ket_thuc(os[i]['id'], ks[i].tra(
                base64url_to_bytes(os[i]['publicKey']['challenge']), dang_ky=True))
        except TuChoi:
            return None
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = list(pool.map(go, range(2)))
    assert sum(r is not None for r in results) == 1
    assert len(dv.trang_thai('')['thiet_bi']) == 1
    assert go(0) is None and go(1) is None


def test_han_ma_challenge_va_rate_limit(dv):
    ma = dv.cap_ma()
    dv.clock[0] += 599
    o = dv.bat_dau('dang-ky', ma=ma)
    dv.clock[0] += 1
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], KhoaGia().tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True))
    for _ in range(5):
        with pytest.raises(TuChoi):
            dv.bat_dau('dang-ky', ma='sai')
    with pytest.raises(TuChoi, match='Quá nhiều'):
        dv.bat_dau('dang-ky', ma=ma)


def test_khoi_phuc_huy_het_va_tin_ben(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    q = login(dv, k, 'r', c, 'them')['quyen']
    ma = dv.moi(c, q, rang='them')['ma']
    o = dv.bat_dau('dang-ky', ma=ma)
    moi = dv.cap_ma(khoi_phuc=True)
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], KhoaGia().tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True))
    with pytest.raises(TuChoi):
        dv.can_phien(c)
    with mo_kho(dv.path) as db:
        assert db.execute('select count(*) from tin').fetchone()[0] == 2
    them(dv, moi)


def test_r_het_han_va_retry_khong_cap_ma_lan_hai(dv):
    k = them(dv)
    c = login(dv,k)['cookie']
    q = login(dv,k,'r',c,'them-het')['quyen']
    dv.clock[0] += 120
    with pytest.raises(TuChoi):
        dv.moi(c,q,rang='them-het')
    q = login(dv,k,'r',c,'them-cung-ma')['quyen']
    m = dv.moi(c,q,rang='them-cung-ma')
    q2 = login(dv,k,'r',c,'them-cung-ma')['quyen']
    assert q2 == q
    assert dv.moi(c,q2,rang='them-cung-ma') == m


def test_khoa_nguoi_va_vai_khong_cho_phien(dv):
    k = them(dv); c = login(dv,k)['cookie']
    with mo_kho(dv.path) as db,giao_dich(db):
        db.execute("UPDATE nguoi SET vai='xem'")
    with pytest.raises(TuChoi):
        dv.can_phien(c)
    with mo_kho(dv.path) as db,giao_dich(db):
        db.execute("UPDATE nguoi SET vai='chu',bat=0")
    with pytest.raises(TuChoi):
        dv.can_phien(c)
