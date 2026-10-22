"""Một kết nối/giao dịch mỗi lời gọi; không giữ kết nối xuyên luồng."""
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable
from webauthn.helpers import bytes_to_base64url
from tram.passkey import nghi_le, thiet_bi
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma, cac_khoa, phien, TuChoi


@dataclass
class DichVu:
    path: Path
    login: str
    rp: str
    dong_ho: Callable = time.time

    @contextmanager
    def mo(self):
        with mo_kho(self.path) as db, giao_dich(db):
            yield db, nguoi(db, self.login), self.dong_ho()

    def cap_ma(self, khoi_phuc=False):
        with self.mo() as (db, u, luc):
            return cap_ma(db, u, luc, khoi_phuc)

    def bat_dau(self, loai, *, cookie='', rang='', ma=''):
        with self.mo() as (db, u, luc):
            return nghi_le.bat_dau(db, u, self.rp, luc, loai, cookie, rang, ma)

    def ket_thuc(self, cid, credential, ten='Thiết bị'):
        with self.mo() as (db, u, luc):
            return nghi_le.ket_thuc(db, u, self.rp, luc, cid, credential, ten)

    def can_phien(self, cookie):
        with self.mo() as (db, u, luc):
            return dict(phien(db, u, cookie, luc))

    def trang_thai(self, cookie):
        with self.mo() as (db, u, luc):
            try:
                con = max(0, int(phien(db, u, cookie, luc)['han']-luc))
            except TuChoi:
                con = 0
            return {'con_giay': con, 'cho_gui': db.execute('SELECT count(*) FROM tin WHERE gui=0').fetchone()[0],
                    'thiet_bi': [{'id': bytes_to_base64url(k['id']), 'ten': k['ten'], 'tao': k['tao'],
                                 'dung': k['dung']} for k in cac_khoa(db, u)]}

    def moi(self, cookie, quyen, *, rang):
        with self.mo() as (db, u, luc):
            return thiet_bi.moi(db, u, cookie, quyen, rang, luc)

    def thu_hoi(self, cookie, quyen, target, *, rang):
        with self.mo() as (db, u, luc):
            return thiet_bi.thu_hoi(db, u, cookie, quyen, target, rang, luc)

    def quan_ly(self, cookie, quyen, viec, than):
        from tram.passkey.quan_ly import thuc_hien
        with self.mo() as (db, u, luc):
            return thuc_hien(db, u, cookie, quyen, viec, than, luc)
