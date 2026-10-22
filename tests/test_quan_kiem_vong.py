import json
import pytest
from tram.giao_viec.cong_luot import CongLuot, CongDong
from tram.quan_kiem.vong import QuanKiem
from test_quan_kiem_giao_thuc import mau


def tao(tmp_path, chay=None):
    c = CongLuot(tmp_path / 'cong.json', lambda: None, [], ngu=lambda n: None)
    c.mo_lai()
    def worker(d, a, e, huy):
        r = chay(d, a, e, huy) if chay else {'dat': True, 'ket_qua': []}
        c.ra(d['id'])
        return r
    q = QuanKiem(tmp_path, c, worker)
    return q, c


def test_replay_khong_chay_lai(tmp_path):
    calls = []
    q, c = tao(tmp_path, lambda *a: calls.append(a) or {'dat': True, 'ket_qua': []})
    a = q.chay(mau(), b'abc', b'', lambda: False)
    assert q.chay(mau(), b'abc', b'', lambda: False) == a
    assert len(calls) == 1
    with pytest.raises(ValueError, match='id-khac-noi-dung'):
        q.chay(mau() | {'luot': 2}, b'abc', b'', lambda: False)


def test_loi_va_restart_khong_tu_mo(tmp_path):
    def hong(*a):
        raise OSError('khong-duoc-lo-noi-dung')
    q, c = tao(tmp_path, hong)
    with pytest.raises(OSError):
        q.chay(mau(), b'abc', b'', lambda: False)
    assert c.trang_thai()['trang_thai'] == 'dong'
    QuanKiem(tmp_path, c, hong)
    assert c.trang_thai()['trang_thai'] == 'dong'
    assert 'khong-duoc-lo' not in (tmp_path / 'luot' / ('a'*32 + '.json')).read_text()


def test_crash_sau_nhan(tmp_path):
    q, c = tao(tmp_path)
    q.ghi(mau()['id'], {'fingerprint': 'd', 'trang_thai': 'dang-chay'})
    QuanKiem(tmp_path, c, lambda *a: None)
    assert c.trang_thai()['trang_thai'] == 'dong'


def test_digest_sai_khong_chay(tmp_path):
    q, c = tao(tmp_path, lambda *a: pytest.fail('khong duoc spawn'))
    with pytest.raises(ValueError):
        q.chay(mau(), b'sai', b'', lambda: False)


def test_huy_chi_dung_luot(tmp_path):
    q, c = tao(tmp_path)
    assert q.huy('b'*32) is False
    q.dang = 'a'*32
    assert q.huy('b'*32) is False
    assert q.huy('a'*32) is True
    assert q.dung.is_set()
