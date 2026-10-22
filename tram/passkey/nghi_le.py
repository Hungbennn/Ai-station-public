"""Ceremony nguyên tử: mã/challenge dùng một lần, UV do thư viện kiểm."""
import secrets
from tram.passkey.kho import bam, cac_khoa, phien, TuChoi
from tram.passkey.webauthn import dang_ky, dang_nhap, tuy_chon
from webauthn.helpers import base64url_to_bytes


def bat_dau(db, u, rp, luc, loai, cookie, rang, ma):
    if loai not in ('dang-ky', 'phien', 'r') or len(rang) > 128:
        raise TuChoi('Yêu cầu không hợp lệ')
    han, mh, ph = luc+120, '', ''
    if loai == 'dang-ky':
        sai = db.execute('SELECT * FROM sai WHERE nguoi=?', (u['id'],)).fetchone()
        if sai and sai['han'] > luc and sai['dem'] >= 5:
            raise TuChoi('Quá nhiều lần — thử lại sau')
        m = db.execute('SELECT * FROM ma WHERE bam=? AND nguoi=? AND han>?', (bam(ma), u['id'], luc)).fetchone()
        if m is None:
            dem, het = (sai['dem']+1, sai['han']) if sai and sai['han'] > luc else (1, luc+600)
            db.execute('INSERT OR REPLACE INTO sai VALUES(?,?,?)', (u['id'], dem, het))
            db.commit()  # giữ lần sai dù giao dịch ngoài từ chối; chưa có thay đổi nào khác
            raise TuChoi('Mã không hợp lệ hoặc hết hạn')
        mh, han = m['bam'], min(han, m['han'])
    elif not cac_khoa(db, u):
        raise TuChoi('Cần đăng ký passkey')
    elif loai == 'r':
        ph = phien(db, u, cookie, luc)['bam']
        if not rang:
            raise TuChoi('Thiếu thao tác')
    cid, challenge = secrets.token_urlsafe(32), secrets.token_bytes(32)
    db.execute('DELETE FROM hoi WHERE han<=?', (luc,))
    if db.execute('SELECT count(*) FROM hoi WHERE nguoi=?', (u['id'],)).fetchone()[0] >= 20:
        raise TuChoi('Quá nhiều lần — thử lại sau')
    db.execute('INSERT INTO hoi VALUES(?,?,?,?,?,?,?,?)',
               (cid, u['id'], challenge, loai, rang, ph, mh, han))
    return {'id': cid, 'publicKey': tuy_chon(rp, u['login'], u['id'], challenge,
            [k['id'] for k in cac_khoa(db, u)], loai == 'dang-ky')}


def ket_thuc(db, u, rp, luc, cid, credential, ten):
    h = db.execute('SELECT * FROM hoi WHERE id=? AND nguoi=? AND han>?', (cid, u['id'], luc)).fetchone()
    if h is None:
        raise TuChoi('Chưa xác nhận — thử lại')
    if h['loai'] == 'dang-ky':
        m = db.execute('SELECT * FROM ma WHERE bam=? AND nguoi=? AND han>?',
                       (h['ma'], u['id'], luc)).fetchone()
        if m is None:
            raise TuChoi('Mã không hợp lệ hoặc hết hạn')
        r = dang_ky(credential, h['challenge'], rp)
        if db.execute('SELECT 1 FROM khoa WHERE id=?', (r.credential_id,)).fetchone():
            raise TuChoi('Passkey đã có')
        db.execute('INSERT INTO khoa VALUES(?,?,?,?,?,?,NULL,NULL)',
                   (r.credential_id, u['id'], r.credential_public_key, r.sign_count, ten[:80], luc))
        db.execute('DELETE FROM ma WHERE bam=?', (h['ma'],))
        db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)', ('them', luc))
        out = {'da_dang_ky': True}
    else:
        try:
            kid = base64url_to_bytes(credential['id'])
        except Exception:
            raise TuChoi('Chưa xác nhận — thử lại') from None
        k = db.execute('SELECT * FROM khoa WHERE id=? AND nguoi=? AND thu IS NULL', (kid, u['id'])).fetchone()
        if k is None:
            raise TuChoi('Chưa xác nhận — thử lại')
        r = dang_nhap(credential, h['challenge'], rp, k['public'], k['dem'])
        handle = credential.get('response', {}).get('userHandle')
        if handle is not None and base64url_to_bytes(handle) != u['id']:
            raise TuChoi('Chưa xác nhận — thử lại')
        db.execute('UPDATE khoa SET dem=?,dung=? WHERE id=?', (r.new_sign_count, luc, kid))
        token = secrets.token_urlsafe(32)
        if h['loai'] == 'phien':
            db.execute('INSERT INTO phien VALUES(?,?,?,?,?)', (bam(token), u['id'], kid, u['login'], luc+28800))
            out = {'cookie': token, 'han': luc+28800}
        else:
            p = db.execute('SELECT p.* FROM phien p JOIN khoa k ON p.khoa=k.id WHERE p.bam=? '
                           'AND p.han>? AND k.thu IS NULL', (h['phien'], luc)).fetchone()
            if p is None:
                raise TuChoi('Cần phiên passkey')
            cu = db.execute('SELECT * FROM quyen WHERE nguoi=? AND phien=? AND rang=?',
                            (u['id'], h['phien'], h['rang'])).fetchone()
            if cu:
                token = cu['id']
                if not cu['dung']:
                    db.execute('UPDATE quyen SET han=? WHERE id=?', (min(luc+120, p['han']), token))
            else:
                db.execute('INSERT INTO quyen VALUES(?,?,?,?,?,0)',
                           (token, u['id'], h['phien'], h['rang'], min(luc+120, p['han'])))
            out = {'quyen': token}
    db.execute('DELETE FROM hoi WHERE id=?', (cid,))
    return out
