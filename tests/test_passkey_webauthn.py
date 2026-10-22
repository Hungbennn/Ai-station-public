import json
import pytest
from passkey_gia import KhoaGia
from tram.passkey.webauthn import dang_ky, dang_nhap, tuy_chon, TuChoi


def test_verifier_that_va_uv_bat_buoc():
    k, c = KhoaGia(), b'c' * 32
    opt = tuy_chon('b.test', 'chu', b'u' * 32, c, [], True)
    assert opt['authenticatorSelection']['userVerification'] == 'required'
    r = dang_ky(k.tra(c, dang_ky=True), c, 'b.test')
    assert r.credential_id == k.id
    a = dang_nhap(k.tra(c), c, 'b.test', r.credential_public_key, 0)
    assert a.user_verified and a.new_sign_count == 0
    assert tuy_chon('b.test', 'chu', b'u'*32, c, [k.id], False)['userVerification'] == 'required'


@pytest.mark.parametrize('loi', ['uv', 'origin', 'rp', 'challenge', 'chu_ky', 'dem'])
def test_tu_choi_bang_chung_sai(loi):
    k, c = KhoaGia(), b'c' * 32
    r = dang_ky(k.tra(c, dang_ky=True), c, 'b.test')
    kw = {'uv': False} if loi == 'uv' else {loi: 'gia'} if loi in ('rp', 'origin') else {}
    a = k.tra(b'x'*32 if loi == 'challenge' else c, **kw)
    if loi == 'chu_ky':
        a['response']['signature'] = 'AAAA'
    with pytest.raises(TuChoi, match='Chưa xác nhận') as e:
        dang_nhap(a, c, 'b.test', r.credential_public_key, 1 if loi == 'dem' else 0)
    assert 'gia' not in str(e.value)


def test_dang_ky_khong_uv():
    k, c = KhoaGia(), b'c'*32
    with pytest.raises(TuChoi):
        dang_ky(k.tra(c, dang_ky=True, uv=False), c, 'b.test')
