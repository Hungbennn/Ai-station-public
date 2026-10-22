"""Kết quả bền theo người/mã; không lưu mã mời rõ, không cấp lại khi mất phản hồi."""
from tram.passkey import thiet_bi
from tram.passkey.chinh_sach import rang_buoc
from tram.passkey.thao_tac import rang_ma


def thuc_hien(db, u, cookie, quyen, viec, than, luc):
    ma = than.get('ma_thao_tac')
    if not isinstance(ma, str) or not ma or len(ma) > 128:
        raise ValueError('Thiếu mã thao tác')
    path = '/api/passkey/' + viec
    rang = rang_buoc(path, than)
    thiet_bi.can_r(db, u, cookie, quyen, rang, luc)
    rang_ma(db, u, path, than)
    cu = db.execute('SELECT * FROM ket_qua WHERE ma=? AND nguoi=?', (ma, u['id'])).fetchone()
    if cu:
        if viec == 'thu-hoi':
            return {'da_thu_hoi': True}
        # Mã chỉ hiện ở phản hồi đầu. Retry trả kết quả đã cấp, kể cả mã đã dùng/hết hạn.
        return {'da_cap': True, 'ma': None}
    if viec == 'moi':
        out = thiet_bi.moi(db, u, cookie, quyen, rang, luc)
    else:
        out = thiet_bi.thu_hoi(db, u, cookie, quyen, than['id'], rang, luc)
    db.execute('INSERT INTO ket_qua VALUES(?,?,?,?)', (ma, u['id'], rang, viec))
    return out
