"""Kho passkey riêng tư; giao dịch ngắn, gọi WebAuthn cục bộ trong khoá ghi."""
import hashlib
import secrets
import sqlite3
from contextlib import contextmanager

from tram.passkey.luoc_do import BUOC
from tram.passkey.webauthn import TuChoi
from tram.su_kien.ket_noi import mo_ket_noi
from tram.su_kien.phien_ban import nang_cap


def bam(s):
    return hashlib.sha256(s.encode()).hexdigest()


@contextmanager
def mo_kho(path):
    db = mo_ket_noi(path)
    try:
        nang_cap(db, thu_muc_sao_luu=path.parent/'sao-luu-passkey', buoc=BUOC, moi=1)
        db.row_factory = sqlite3.Row
        yield db
    finally:
        db.close()


@contextmanager
def giao_dich(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.commit()
    except BaseException:
        db.rollback()
        raise


def nguoi(db, login):
    u = db.execute('SELECT * FROM nguoi WHERE login=?', (login,)).fetchone()
    if u is None and not db.execute('SELECT 1 FROM nguoi').fetchone():
        db.execute('INSERT INTO nguoi VALUES(?,?,?,1)', (secrets.token_bytes(32), login, 'chu'))
        u = db.execute('SELECT * FROM nguoi WHERE login=?', (login,)).fetchone()
    if u is None or not u['bat'] or u['vai'] != 'chu':
        raise TuChoi('Không có quyền')
    return u


def cap_ma(db, u, luc, khoi_phuc=False, nguon=None):
    if khoi_phuc:
        db.execute('UPDATE khoa SET thu=? WHERE nguoi=? AND thu IS NULL', (luc, u['id']))
        for bang in ('phien', 'hoi', 'quyen', 'sai'):
            db.execute(f'DELETE FROM {bang} WHERE nguoi=?', (u['id'],))
        db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)', ('khoi-phuc', luc))
    db.execute('DELETE FROM ma WHERE nguoi=?', (u['id'],))
    ma = secrets.token_urlsafe(32)
    db.execute('INSERT INTO ma VALUES(?,?,?,?)', (bam(ma), u['id'], nguon, luc+600))
    return ma


def phien(db, u, cookie, luc):
    p = db.execute('SELECT p.* FROM phien p JOIN khoa k ON k.id=p.khoa '
                   'WHERE p.bam=? AND p.nguoi=? AND p.login=? AND p.han>? AND k.thu IS NULL',
                   (bam(cookie), u['id'], u['login'], luc)).fetchone()
    if p is None:
        raise TuChoi('Cần phiên passkey')
    return p


def cac_khoa(db, u):
    return db.execute('SELECT * FROM khoa WHERE nguoi=? AND thu IS NULL ORDER BY tao', (u['id'],)).fetchall()
