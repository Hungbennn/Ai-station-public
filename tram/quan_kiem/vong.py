"""Một chủ giữ cổng và receipt; không hàng đợi, không tự mở sau crash."""
import json
import os
import threading
from pathlib import Path

from tram.giao_viec.cong_luot import CongDong
from tram.quan_kiem.giao_thuc import bam, fingerprint, yeu_cau


class QuanKiem:
    def __init__(self, goc, cong, thuc_thi, mo_that=None):
        self.goc, self.cong, self.thuc_thi = Path(goc), cong, thuc_thi
        self.mo_that = mo_that or cong.mo_lai
        self.khoa, self.dung, self.dang = threading.Lock(), threading.Event(), None
        (self.goc / 'luot').mkdir(mode=0o700, exist_ok=True)
        for p in (self.goc / 'luot').glob('*.json'):
            try:
                if json.loads(p.read_bytes())['trang_thai'] == 'dang-chay':
                    self.cong.dong('restart-giua-luot')
            except (ValueError, KeyError, OSError):
                self.cong.dong('receipt-hong')
        if (self.goc / 'kiem-lai.dong').exists():
            self.cong.dong('han-tong-chua-don')

    def ghi(self, id_, d):
        p = self.goc / 'luot' / (id_ + '.json')
        tam = p.with_suffix('.tam')
        with open(tam, 'w', encoding='utf-8') as f:
            json.dump(d, f, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tam, p)
        fd = os.open(p.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def trang_thai(self, id_):
        p = self.goc / 'luot' / (id_ + '.json')
        try:
            return json.loads(p.read_bytes())
        except FileNotFoundError:
            return {'trang_thai': 'khong-co', 'cong': self.cong.trang_thai()['trang_thai']}

    def huy(self, id_):
        if id_ != self.dang:
            return False
        self.dung.set()
        return True

    def dong(self):
        self.dung.set()
        if self.khoa.acquire(blocking=False):
            try:
                self._dong_loi('loi-kenh')
            finally:
                self.khoa.release()

    def _dong_loi(self, ly_do):
        tt = self.cong.trang_thai()
        if tt['trang_thai'] != 'dong' or not tt.get('ly_do'):
            self.cong.dong(ly_do)

    def mo(self):
        if not self.khoa.acquire(blocking=False):
            raise OSError('dang-ban')
        try:
            self.mo_that()
        except BaseException:
            self._dong_loi('mo-lai-chua-ro')
            raise
        finally:
            self.khoa.release()

    def chay(self, d, nguon, env, mat_kenh):
        yeu_cau(d)
        if not self.khoa.acquire(blocking=False):
            raise OSError('dang-ban')
        fp = fingerprint(d)
        try:
            cu = self.trang_thai(d['id'])
            if cu['trang_thai'] != 'khong-co':
                if cu['fingerprint'] != fp:
                    raise ValueError('id-khac-noi-dung')
                return cu
            if len(nguon) != d['nguon_n'] or bam(nguon) != d['nguon_sha'] or \
                    len(env) != d['env_n'] or bam(env) != d['env_sha']:
                raise ValueError('digest-sai')
            self.cong.vao(d['id'])
            r = {'fingerprint': fp, 'trang_thai': 'dang-chay',
                 'id': d['id'], 'giao_id': d['giao_id'], 'luot': d['luot'], 'commit': d['commit']}
            self.ghi(d['id'], r)
            self.dang = d['id']
            self.dung.clear()
            try:
                kq = self.thuc_thi(d, nguon, env, lambda: self.dung.is_set() or mat_kenh())
                if self.cong.trang_thai()['trang_thai'] != 'mo':
                    raise CongDong('worker-chua-xac-nhan-don')
                r |= {'trang_thai': 'xong', 'ket_qua': kq, 'da_thu_hoi': True}
                self.ghi(d['id'], r)
                return r
            except BaseException:
                self._dong_loi('loi-luot')
                self.ghi(d['id'], r | {'trang_thai': 'dong', 'loi': 'loi-luot'})
                raise
            finally:
                self.dang = None
        finally:
            self.khoa.release()
