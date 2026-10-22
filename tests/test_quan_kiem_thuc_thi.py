import pytest
from types import SimpleNamespace
from tram.quan_kiem.thuc_thi import thuc_thi, chay_con


def test_huy_giu_dau_va_don_co_han(tmp_path, monkeypatch):
    import tram.quan_kiem.thuc_thi as m
    calls = []
    def chay(mode, p, han, huy, **kw):
        calls.append((mode, han))
        if mode == 'luot':
            raise TimeoutError()
    monkeypatch.setattr(m, 'chay_con', chay)
    with pytest.raises(TimeoutError):
        thuc_thi({'id': 'a'*32}, b'', b'', lambda: True, cfg={'home': str(tmp_path)}, pk=None)
    assert calls == [('luot', 3300), ('don', 240)]
    assert (tmp_path / 'kiem-lai.dong').exists()


def test_loi_spawn_van_thu_hoi_chu(monkeypatch):
    import tram.quan_kiem.thuc_thi as m
    calls = []
    monkeypatch.setattr(m, 'thu_hoi_con_lai', lambda chu: calls.append(tuple(chu)) or True)
    def loi(*a, chu, **kw):
        chu.append('da-spawn')
        raise OSError()
    with pytest.raises(OSError):
        chay_con('luot', 'x', 1, lambda: False, cfg=dict(python='p', entry='e', home='h'),
                 pk=SimpleNamespace(kill_nhom=lambda *a: None), khoi=loi)
    assert calls == [('da-spawn',)]


def test_worker_cu_sau_crash_chan_mo_cong(monkeypatch):
    import tram.quan_kiem.cong as m
    from tram.kiem.cay_tien_trinh import TienTrinh
    ds = [TienTrinh(10, 1, 10, 504, 504, 1), TienTrinh(11, 10, 11, 504, 504, 2)]
    monkeypatch.setattr(m.os, 'getpid', lambda: 11)
    monkeypatch.setattr(m.os, 'getppid', lambda: 10)
    monkeypatch.setattr(m.os, 'getuid', lambda: 504)
    monkeypatch.setattr(m, 'con_uid', lambda *a, **kw: ds)
    monkeypatch.setattr(m, 'mot_nhan', lambda pid: next(t for t in ds if t.pid == pid))
    m.quan_uq()
    ds.append(TienTrinh(12, 1, 12, 504, 504, 3))
    with pytest.raises(OSError, match='ngoai-luot'):
        m.quan_uq()
