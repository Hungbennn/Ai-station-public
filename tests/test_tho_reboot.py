"""R5: boot trước GUI, chờ trong tiến trình; đồng hồ/tín hiệu/API/CLI đều giả."""
import signal
import threading
import time
from types import SimpleNamespace

import pytest

from test_doi_ngu_nen import ch
from tram.tho import cau_hinh, khach, lenh_chay, san_sang_b, vong_khe


@pytest.fixture
def boot(monkeypatch):
    tinh = SimpleNamespace(gio=0.0, cho=[], api=[], da_chay=[], do=0, tin={}, khi_cho=None,
                          san_sang=lambda: True, loi_api=0, ma_api=200, token="token-gia-khong-duoc-in")
    event_that = threading.Event

    class EventGia(event_that):
        def wait(self, timeout=None):
            if timeout is None:
                return super().wait(timeout)
            if not self.is_set():
                tinh.cho.append(timeout)
                if tinh.khi_cho:
                    tinh.khi_cho()
                if not self.is_set():
                    tinh.gio += timeout
            return self.is_set()

    def do(ch):
        tinh.do += 1
        return tinh.san_sang()

    def goi(self, method, duong, than=None, **kw):
        tinh.api.append((method, duong, than))
        if tinh.loi_api:
            tinh.loi_api -= 1
            raise khach.LoiKhachTram("chi-tiet-bi-mat-khong-duoc-in")
        return tinh.ma_api, {}

    def chay(self, tat):
        tinh.da_chay.append(self.k.ten)
        tat.set()

    monkeypatch.setattr(cau_hinh, "nap_cau_hinh_tho", ch)
    monkeypatch.setattr(lenh_chay, "doc_token_may", lambda **kw: tinh.token)
    monkeypatch.setattr(lenh_chay, "doc_principal", lambda p: None)
    monkeypatch.setattr(san_sang_b, "san_sang_b", do)
    monkeypatch.setattr(khach.KhachTram, "goi", goi)
    monkeypatch.setattr(vong_khe.VongKhe, "chay", chay)
    monkeypatch.setattr(threading, "Event", EventGia)
    monkeypatch.setattr(time, "monotonic", lambda: tinh.gio)
    monkeypatch.setattr(signal, "signal", lambda s, ham: tinh.tin.__setitem__(s, ham))
    return tinh


def test_api_loi_hai_lan_roi_dang_ky_va_chay(boot, capsys):
    boot.loi_api = 2
    assert lenh_chay._chay(SimpleNamespace()) == 0
    assert len(boot.api) == 3 and boot.da_chay
    assert all(a[:2] == ("POST", "/api/tho/dang-ky") for a in boot.api)
    assert boot.cho == [10, 20]
    out = capsys.readouterr()
    dong = (out.out + out.err).splitlines()
    assert len(dong) == 2 and all("tram-api" in d for d in dong)
    assert "1" in dong[0] and "2" in dong[1]
    assert "bi-mat" not in out.out + out.err and boot.token not in out.out + out.err


def test_dang_nhap_false_hai_lan_roi_chay(boot):
    ket = iter([False, False, True])
    boot.san_sang = lambda: next(ket)
    assert lenh_chay._chay(SimpleNamespace()) == 0
    assert boot.do == 3 and boot.cho == [10, 20] and boot.da_chay


def test_het_han_dang_nhap_thoat_0_va_nhac_khoi_dong_lai(boot, capsys):
    boot.san_sang = lambda: False
    assert lenh_chay._chay(SimpleNamespace()) == 0
    assert boot.gio == 900 and max(boot.cho) == 60 and boot.cho[:3] == [10, 20, 40]
    assert not boot.da_chay
    out = capsys.readouterr()
    assert "khởi động lại thợ" in out.out + out.err


def test_cho_tram_api_khong_het_han_va_log_thua_dan(boot, capsys):
    # tram-api là LaunchAgent: chỉ lên khi Đại ca đăng nhập GUI — có thể sau nhiều giờ (reboot đêm).
    boot.san_sang = lambda: boot.gio >= 450
    boot.loi_api = 200
    assert lenh_chay._chay(SimpleNamespace()) == 0
    assert boot.gio > 900 * 10 and boot.da_chay and max(boot.cho) == 60
    dong = [d for d in capsys.readouterr().out.splitlines() if "tram-api" in d]
    assert 5 < len(dong) < 20


@pytest.mark.parametrize("ly_do", ["dang-nhap", "api"])
def test_sigterm_giua_cho_thoat_0_ngay(boot, capsys, ly_do):
    boot.san_sang = lambda: ly_do == "api"
    boot.loi_api = 100
    boot.khi_cho = lambda: boot.tin[signal.SIGTERM](signal.SIGTERM, None)
    assert lenh_chay._chay(SimpleNamespace()) == 0
    assert boot.gio == 0 and boot.cho == [10] and not boot.da_chay
    assert "khởi động lại" not in str(capsys.readouterr())


def test_thieu_token_thoat_0_khong_cho_khong_do_dang_nhap(boot, capsys):
    boot.token = None
    boot.san_sang = lambda: False
    assert lenh_chay._chay(SimpleNamespace()) == 0
    assert not boot.cho and boot.do == 0 and not boot.api and not boot.da_chay
    assert "Chưa có token máy hợp lệ" in capsys.readouterr().err


@pytest.mark.parametrize("loi", [ValueError("bi-mat"), OSError("bi-mat")])
def test_cau_hinh_hong_thoat_ngay(boot, monkeypatch, capsys, loi):
    def hong():
        raise loi
    monkeypatch.setattr(cau_hinh, "nap_cau_hinh_tho", hong)
    assert lenh_chay._chay(SimpleNamespace()) == 0
    assert not boot.cho and boot.do == 0 and not boot.api
    assert "bi-mat" not in str(capsys.readouterr())


def test_http_loi_giu_ma_thoat_cu_khong_thu_lai(boot):
    boot.ma_api = 403
    assert lenh_chay._chay(SimpleNamespace()) == 2
    assert not boot.cho and not boot.da_chay
