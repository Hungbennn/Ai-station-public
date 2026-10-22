from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.noi_that import dung_bo_that


def test_bo_that_chi_noi_socket_khong_giu_cong_local(monkeypatch):
    import tram.giao_viec.noi_that as m
    monkeypatch.setattr(m, 'nap_phu_thuoc_4c', lambda: None)
    b = dung_bo_that(CauHinhGiaoViec(), CauHinhTram())
    assert b.kiem_tu_xa is not None
    assert b.boc is None and b.don_sach is None and b.boc_luot is None
    assert type(b.cong).__name__ == 'CongTuXa'


def test_ket_qua_muon_khong_duoc_ghi(monkeypatch):
    from contextlib import contextmanager
    from types import SimpleNamespace
    import tram.quan_kiem.fencing as m
    writes, locked = [], []
    @contextmanager
    def transaction():
        locked.append(True)
        try:
            yield
        finally:
            locked.pop()
    def lay(id_):
        assert locked
        return SimpleNamespace(ket_thuc='thu_hoi')
    kho = SimpleNamespace(giao_dich=transaction, lay=lay, ghi_su_kien=lambda *a, **kw: writes.append(a))
    p = SimpleNamespace(giao_id='g', bead_id='b', luot=1)
    assert m.ghi_ket_qua(kho, SimpleNamespace(ten='d'), p, 'a'*40, {'dat': True}, None) == 'luot-cu'
    assert writes == [] and not locked
