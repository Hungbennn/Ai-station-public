"""bs-863.19 phần còn lại + B03 (vòng 1): SIGTERM ở CLI cha `tram giao nghiem-thu-kiem` đi đường ngắt có kiểm soát ở
MỌI đoạn đã/đang sở hữu tiến trình con — preflight (tiến trình dò UID), tạo dấu + spawn harness, chờ, dọn. Con GIẢ,
không tín hiệu thật (gọi thẳng handler đang cài), không sudo/tiến trình con. `chan_sigterm_mac_dinh`: handler canh của
test — nếu mã chưa cài `term_thanh_ngat` mà tín hiệu (kể cả bản phát lại của `hoan()`) tới, test ĐỎ thay vì SIGTERM
mặc định giết luôn pytest."""
import signal

import pytest

from test_lenh_nghiem_thu import args, cau_hinh  # noqa: F401 — fixture `cau_hinh` dùng chung
from tram.giao_viec import lenh_nghiem_thu as lnt
from tram.giao_viec.cong_luot import CongLuot
from tram.kiem.ngat import NgatTerm


class SigtermLot(Exception):
    """SIGTERM tới mà CLI cha chưa cài handler — mặc định sẽ giết CLI cha, bỏ lại con/tiến trình dò."""


@pytest.fixture(autouse=True)
def chan_sigterm_mac_dinh():
    def canh(so, khung):
        raise SigtermLot()
    cu = signal.signal(signal.SIGTERM, canh)
    yield
    signal.signal(signal.SIGTERM, cu)


def _sigterm():
    h = signal.getsignal(signal.SIGTERM)
    assert callable(h), "SIGTERM chưa có handler ở đoạn này — mặc định giết CLI cha, con/tiến trình dò bị bỏ lại"
    h(signal.SIGTERM, None)                                         # như nhân giao SIGTERM — không gửi tín hiệu thật


class ConGia:
    """Harness con GIẢ dưới `chay_han_tong` thật: SIGTERM tới cha trong lúc chờ."""
    def __init__(self, goi):
        self.goi = goi

    def cho(self, han):
        _sigterm()

    def thu_hoi(self):
        self.goi.append("thu")
        return True


def test_sigterm_o_cha_thu_hoi_con_va_don_xong_moi_tra(cau_hinh, tram_home_tam, monkeypatch, capsys):
    goi, truoc = [], signal.getsignal(signal.SIGTERM)
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", lambda a, **kw: ConGia(goi))
    monkeypatch.setattr(lnt, "_don", lambda pk, goc: goi.append("don") or True)
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777) == 143
    assert goi == ["thu", "don"] and not (tram_home_tam / "kiem-lai.dong").exists()
    assert signal.getsignal(signal.SIGTERM) is truoc and "SIGTERM" in (e := capsys.readouterr().err) and "đã xoá" in e


def test_sigterm_luc_xac_minh_uid_cho_tien_trinh_do_thu_hoi_xong_roi_moi_dung(cau_hinh, tram_home_tam, capsys):
    """B03: preflight có spawn (tiến trình dò UID dưới principal) — SIGTERM tới giữa chừng: dò chạy tới hết (gồm thu
    hồi của nó), rồi CLI dừng 143, KHÔNG tạo dấu, KHÔNG spawn harness."""
    goi = []

    def xac_minh(*a):
        _sigterm()
        goi.append("do-da-thu-hoi")
        return 777
    assert lnt.lenh_nghiem_thu(args(), xac_minh=xac_minh, han_tong=lambda *a, **kw: goi.append("harness")) == 143
    assert goi == ["do-da-thu-hoi"] and not (tram_home_tam / "kiem-lai.dong").exists()
    assert "SIGTERM" in capsys.readouterr().err


def test_sigterm_giua_luc_spawn_harness_thu_hoi_con_roi_moi_tra(cau_hinh, tram_home_tam, monkeypatch):
    """B03: SIGTERM tới khi `khoi_chay` của harness đang chạy (sau Popen) — con vẫn được nhận chủ, thu hồi, dọn."""
    goi = []

    def khoi(a, **kw):
        _sigterm()
        goi.append("khoi")
        return ConGia(goi)
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", khoi)
    monkeypatch.setattr(lnt, "_don", lambda pk, goc: goi.append("don") or True)
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777) == 143
    assert goi == ["khoi", "thu", "don"] and not (tram_home_tam / "kiem-lai.dong").exists()


def test_ngat_lan_hai_trong_luc_don_giu_dau_va_dong_cong(cau_hinh, tram_home_tam, monkeypatch, tmp_path, capsys):
    goi = []
    c = CongLuot(tmp_path / "c.json", thu_hoi=lambda: None, quan_sat=[], ngu=lambda s: None)
    c.mo_lai()
    c.quan_sat = [_sigterm]                                          # SIGTERM lần hai tới giữa lúc `_don` quan sát
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", lambda a, **kw: ConGia(goi))
    monkeypatch.setattr("tram.giao_viec.cong_that.dung_cong", lambda pk, goc, cac_du_an: c)
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777) == 143
    assert goi == ["thu"] and (tram_home_tam / "kiem-lai.dong").exists() and c.trang_thai()["trang_thai"] == "dong"
    assert "CÒN" in capsys.readouterr().err and not isinstance(NgatTerm(), Exception)   # `except Exception` không nuốt
