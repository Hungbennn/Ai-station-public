"""Lý do worker ghi phải sống qua vong.mo/chay và dich_vu.phuc_vu."""
from types import SimpleNamespace

import pytest

from tram.giao_viec.cong_luot import CongLuot, CongDong
from tram.quan_kiem.vong import QuanKiem
from test_quan_kiem_giao_thuc import mau


def phuc_vu(monkeypatch, q, op):
    import tram.quan_kiem.dich_vu as m
    reply, closed = [], []
    d = {'v': 1, 'op': 'mo', 'id': '0'*32} if op == 'mo' else mau()
    monkeypatch.setattr(m, 'xac_thuc', lambda *a: None)
    monkeypatch.setattr(m, 'doc', lambda *a, **kw: d)
    monkeypatch.setattr(m, 'digest_policy', lambda *a: 'd' * 64)
    monkeypatch.setattr(m, 'nhan', lambda s, n, het: b'abc' if n else b'')
    monkeypatch.setattr(m, 'ghi', lambda s, r: reply.append(r))
    m.phuc_vu(SimpleNamespace(close=lambda: closed.append(True)), q, {
        'uid_tram': 501, 'g4': False, 'policy': {'repo': {
            'mac_dinh': ['python -m pytest'], 'cho_phep': ['python -m pytest']}}})
    assert [r['loi'] for r in reply] == ['khong-cong-nhan'] and closed == [True]
    assert reply[0]['ly_do'].endswith((': loi-mo', ': loi-chay'))


@pytest.mark.parametrize('op', ['mo', 'chay'])
def test_ly_do_con_ghi_khong_bi_hai_lop_bat_loi_de(monkeypatch, tmp_path, capsys, op):
    import tram.quan_kiem.cong as m
    c = CongLuot(tmp_path / 'cong.json', lambda: None, [], ngu=lambda n: None)
    c.mo_lai()
    writes, ghi = [], c._ghi
    def ghi_dem(tt):
        writes.append(tt)
        ghi(tt)
    monkeypatch.setattr(c, '_ghi', ghi_dem)
    def sai_digest():
        raise ValueError('Python kiểm sai digest — cài lại')
    # Phục hồi dùng đúng CongLuot, chỉ giả các lời gọi macOS ở biên.
    con = CongLuot(c.tep, lambda: None, [sai_digest], ngu=lambda n: None)
    monkeypatch.setattr(m, 'thu_hoi_theo_uid', lambda pk: None)
    monkeypatch.setattr(m, 'don_ban', lambda *a, **kw: None)
    monkeypatch.setattr(m, 'ngu_canh_hien_hanh', lambda ten: 'nc')
    monkeypatch.setattr(m, 'dung', lambda *a: con)
    def worker(*a):
        try:
            m.phuc_hoi({'home': str(tmp_path), 'goc': str(tmp_path)}, 'mo', '0'*32)
        except CongDong:
            raise OSError('payload-env-nguon-bi-mat') from None
    q = QuanKiem(tmp_path, c, worker, worker)
    phuc_vu(monkeypatch, q, op)
    assert c.trang_thai() == {'trang_thai': 'dong',
        'ly_do': 'mở lại: ValueError: Python kiểm sai digest — cài lại'}
    assert all(tt['trang_thai'] != 'dong' for tt in writes)
    assert capsys.readouterr().err == f'OSError: loi-{op}\n'


@pytest.mark.parametrize('op,ly_do', [('mo', 'mo-lai-chua-ro'), ('chay', 'loi-luot')])
def test_worker_chua_ghi_ly_do_van_dong_va_log_kin(monkeypatch, tmp_path, capsys, op, ly_do):
    c = CongLuot(tmp_path / 'cong.json', lambda: None, [])
    c._ghi({'trang_thai': 'mo'})
    def hong(*a):
        raise TimeoutError('payload-env-nguon-bi-mat')
    q = QuanKiem(tmp_path, c, hong, hong)
    phuc_vu(monkeypatch, q, op)
    assert c.trang_thai() == {'trang_thai': 'dong', 'ly_do': ly_do}
    assert capsys.readouterr().err == f'TimeoutError: loi-{op}\n'


@pytest.mark.parametrize('tt', [{'trang_thai': 'mo'}, {'trang_thai': 'dang-chay', 'luot': 'x'},
                               {'trang_thai': 'hong'}, {'trang_thai': 'dong'}])
def test_dong_kenh_khong_co_ly_do_phai_ghi_dong(tmp_path, tt):
    c = CongLuot(tmp_path / 'cong.json', lambda: None, [])
    q = QuanKiem(tmp_path, c, None)
    c._ghi(tt)
    q.dong()
    assert c.trang_thai() == {'trang_thai': 'dong', 'ly_do': 'loi-kenh'}
    assert q.dung.is_set()


def test_log_hong_van_dong_va_tra_tu_choi(monkeypatch, tmp_path):
    import tram.quan_kiem.dich_vu as m
    c = CongLuot(tmp_path / 'cong.json', lambda: None, [])
    c._ghi({'trang_thai': 'mo'})
    def hong(*a):
        raise OSError('bi-mat')
    q = QuanKiem(tmp_path, c, hong, hong)
    with monkeypatch.context() as mp:
        mp.setattr(m.sys, 'stderr', SimpleNamespace(write=hong, flush=lambda: None))
        phuc_vu(mp, q, 'chay')
    assert q.dung.is_set()
    assert c.trang_thai() == {'trang_thai': 'dong', 'ly_do': 'loi-luot'}


def test_ly_do_tra_ve_kem_dong_con_moi_ghi_khong_lay_dong_cu(monkeypatch, tmp_path):
    import tram.quan_kiem.dich_vu as m
    log = tmp_path / 'daemon.log'
    log.write_text('con luot: Cu: dong cu\n')
    reply = []

    def doc(*a, **kw):
        with open(log, 'a') as f:
            f.write('con luot: LoiBanChep: moi\n')
        raise OSError('x')
    monkeypatch.setattr(m, 'xac_thuc', lambda *a: None)
    monkeypatch.setattr(m, 'doc', doc)
    monkeypatch.setattr(m, 'ghi', lambda s, r: reply.append(r))
    m.phuc_vu(SimpleNamespace(close=lambda: None), SimpleNamespace(dong=lambda: None), {'uid_tram': 501,
              'home': str(tmp_path)})
    assert reply == [{'loi': 'khong-cong-nhan', 'ly_do': 'OSError: loi-kenh | con luot: LoiBanChep: moi'}]
