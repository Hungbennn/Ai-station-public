"""bs-863.16 (V2-6c): nối dừng hữu hạn vào đẩy mốc và vòng phiếu — đẩy mốc thôi thử lại ngay khi bị hủy; CLI lỗi thì
dừng luồng đọc (có hạn, không đọc lần cuối), luồng chưa dừng thì `LoiThuHoi` thắng lỗi gốc. Mọi thứ GIẢ."""
import threading
import time
from types import SimpleNamespace

import pytest

import tram.tho.phieu_chay as phieu_chay
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho import day


def test_day_mot_dung_thi_thoi_thu_lai_ngay(monkeypatch):
    monkeypatch.setattr(day, "dua_len_ref_tam", lambda *a, **k: False)
    p = SimpleNamespace(giao_id="g-1", luot=1, khe_id="B/claude-1", bead_id="hr-1")
    huy = threading.Event()
    threading.Timer(0.1, huy.set).start()
    t0 = time.monotonic()
    kq = day.day_va_cong_bo(None, p, "a" * 40, khach=None, phuong_an="ref-tam", han=time.monotonic() + 60, cho=5,
                            dung=huy)
    assert kq == "chua-cong-bo" and time.monotonic() - t0 < 2


def test_cli_loi_thi_dung_luong_khong_doc_cuoi_va_thu_hoi_loi_thang(monkeypatch):
    goi = []

    class TD:
        def __init__(self, *a, **kw):
            pass

        def bat_dau(self):
            return self

        def dung_lai(self):
            goi.append("dung_lai")
            raise LoiThuHoi("luồng chưa dừng")

        def ket_thuc(self):
            goi.append("ket_thuc")
    monkeypatch.setattr(phieu_chay, "TheoDoi", TD)
    monkeypatch.setattr(phieu_chay, "ly_do_khong_chay", lambda *a: None)
    monkeypatch.setattr(phieu_chay, "chay_mot_lan", lambda *a: (_ for _ in ()).throw(OSError("log")))
    with pytest.raises(LoiThuHoi):
        phieu_chay._mot_vong(object(), SimpleNamespace(dong_ho=lambda: None), SimpleNamespace(lenh=None))
    assert goi == ["dung_lai"]
