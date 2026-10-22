import pytest
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from passkey_gia import KhoaGia
from test_passkey_dich_vu import dv, them, login
from tram.passkey.chinh_sach import rang_buoc
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import mo_kho, TuChoi


def anh_quan_ly(d):
    with mo_kho(d.path) as db:
        return {bang: [tuple(row) for row in db.execute(f'SELECT * FROM {bang} ORDER BY 1')]
                for bang in ('ma', 'tin', 'ket_qua', 'thao_tac')}


def test_retry_da_commit_sau_120_giay_va_mo_lai_dich_vu(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    body = {'ma_thao_tac': 'v3-moi-da-commit'}
    rang = rang_buoc('/api/passkey/moi', body)
    q = login(dv, k, 'r', c, rang)['quyen']
    assert dv.quan_ly(c, q, 'moi', body)['ma']
    # Quyền chưa dùng khác phải hết hạn; không được lấy ngoại lệ retry làm quyền ghi mới.
    other = {'ma_thao_tac': 'v3-moi-chua-ghi'}
    q2 = login(dv, k, 'r', c, rang_buoc('/api/passkey/moi', other))['quyen']
    before = anh_quan_ly(dv)
    dv.clock[0] += 120
    reopened = DichVu(dv.path, dv.login, dv.rp, dv.dong_ho)
    assert reopened.quan_ly(c, q, 'moi', body) == {'da_cap': True, 'ma': None}
    with pytest.raises(TuChoi):
        reopened.quan_ly(c, q2, 'moi', other)
    assert anh_quan_ly(reopened) == before
    # Hết phiên tuyệt đối vẫn từ chối, dù ledger còn kết quả đã commit.
    dv.clock[0] += 28800
    with pytest.raises(TuChoi):
        reopened.quan_ly(c, q, 'moi', body)
    assert anh_quan_ly(reopened) == before


def test_thu_hoi_huy_ma_con_ca_khi_da_xin_challenge(dv):
    a, b = them(dv), them(dv)
    ca, cb = login(dv, a)['cookie'], login(dv, b)['cookie']
    invite = {'ma_thao_tac': 'v3-moi-tu-b'}
    qb = login(dv, b, 'r', cb, rang_buoc('/api/passkey/moi', invite))['quyen']
    ma = dv.quan_ly(cb, qb, 'moi', invite)['ma']
    pending = dv.bat_dau('dang-ky', ma=ma)
    third = KhoaGia()
    body = {'ma_thao_tac': 'v3-thu-hoi-b', 'id': bytes_to_base64url(b.id)}
    qa = login(dv, a, 'r', ca, rang_buoc('/api/passkey/thu-hoi', body))['quyen']
    assert dv.quan_ly(ca, qa, 'thu-hoi', body) == {'da_thu_hoi': True}
    before = anh_quan_ly(dv)
    reopened = DichVu(dv.path, dv.login, dv.rp, dv.dong_ho)
    with pytest.raises(TuChoi):
        reopened.ket_thuc(pending['id'], third.tra(
            base64url_to_bytes(pending['publicKey']['challenge']), dang_ky=True))
    with pytest.raises(TuChoi):
        reopened.can_phien(cb)
    with pytest.raises(TuChoi):
        reopened.quan_ly(cb, qb, 'moi', invite)
    with pytest.raises(TuChoi):
        login(reopened, b)
    assert reopened.can_phien(ca)
    assert [k['id'] for k in reopened.trang_thai(ca)['thiet_bi']] == [bytes_to_base64url(a.id)]
    assert anh_quan_ly(reopened) == before
    assert before['ma'] == []
    assert len(before['ket_qua']) == 2
    assert [row[1] for row in before['tin']] == ['them', 'them', 'thu-hoi']
