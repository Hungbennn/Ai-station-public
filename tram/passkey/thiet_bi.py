"""R chỉ dành đúng một thao tác; retry cùng thao tác không sinh quyền mới."""
import hashlib
import hmac
from webauthn.helpers import base64url_to_bytes
from tram.passkey.kho import bam, cac_khoa, phien, TuChoi


def can_r(db, u, cookie, qid, rang, luc):
    p = phien(db, u, cookie, luc)
    q = db.execute('SELECT * FROM quyen WHERE id=? AND nguoi=? AND phien=? AND rang=?',
                   (qid, u['id'], p['bam'], rang)).fetchone()
    if q is None or (not q['dung'] and q['han'] <= luc):
        raise TuChoi('Cần chạm lại cho thao tác này')
    return p, q


def moi(db, u, cookie, qid, rang, luc):
    p, q = can_r(db, u, cookie, qid, rang, luc)
    ma = hmac.new(cookie.encode(), qid.encode(), hashlib.sha256).hexdigest()
    if not q['dung']:
        db.execute('DELETE FROM ma WHERE nguoi=?', (u['id'],))
        db.execute('INSERT INTO ma VALUES(?,?,?,?)', (bam(ma), u['id'], p['khoa'], luc+600))
        db.execute('UPDATE quyen SET dung=1 WHERE id=?', (qid,))
    else:
        m = db.execute('SELECT 1 FROM ma WHERE bam=? AND han>?', (bam(ma), luc)).fetchone()
        if m is None:
            raise TuChoi('Mã đã dùng hoặc hết hạn — tạo yêu cầu mới')
    return {'ma': ma}


def thu_hoi(db, u, cookie, qid, target, rang, luc):
    _, q = can_r(db, u, cookie, qid, rang, luc)
    if q['dung']:
        return {'da_thu_hoi': True}
    try:
        kid = base64url_to_bytes(target)
    except Exception:
        raise TuChoi('Thiết bị không hợp lệ') from None
    ks = cac_khoa(db, u)
    if len(ks) <= 1:
        raise TuChoi('Không thể thu hồi passkey cuối cùng — khôi phục tại máy B')
    if kid not in [k['id'] for k in ks]:
        raise TuChoi('Thiết bị không hợp lệ')
    db.execute('UPDATE khoa SET thu=? WHERE id=?', (luc, kid))
    db.execute('DELETE FROM quyen WHERE phien IN (SELECT bam FROM phien WHERE khoa=?)', (kid,))
    db.execute('DELETE FROM hoi WHERE phien IN (SELECT bam FROM phien WHERE khoa=?)', (kid,))
    db.execute('DELETE FROM phien WHERE khoa=?', (kid,))
    db.execute('DELETE FROM ma WHERE nguon=?', (kid,))
    db.execute('UPDATE quyen SET dung=1 WHERE id=?', (qid,))
    db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)', ('thu-hoi', luc))
    return {'da_thu_hoi': True}
