"""bs-863.16 (V2-6c): luồng đọc hàng đợi DỪNG HỮU HẠN — hủy giữa các dòng và trong lúc chờ đẩy mốc, `ket_thuc` có hạn,
chưa dừng → `LoiThuHoi` (khe dừng, giữ phiếu) và KHÔNG đọc lần cuối song song; dòng cuối giao đúng một lần. Hàng đợi,
hộp thư, đẩy ref đều GIẢ; không push/API thật."""
import threading
import time
from types import SimpleNamespace

import pytest

from tram.kiem.vong_doi import LoiThuHoi
from tram.tho import theo_doi
from tram.tho.hang_doi import DongHangDoi
from tram.tho.theo_doi import TheoDoi


class Hop:
    """`gui_mot` GIẢ: lần gọi đầu có thể chặn (handshake `vao`/`tha`) hoặc ném."""
    def __init__(self, chan=False, nem=False):
        self.da, self.chan, self.nem = [], chan, nem
        self.vao, self.tha = threading.Event(), threading.Event()

    def gui_mot(self, khach, duong, than):
        if self.chan and not self.vao.is_set():
            self.vao.set()
            self.tha.wait(10)
        if self.nem:
            self.nem = False
            raise RuntimeError("mất mạng")
        self.da.append(than["request_id"])


def dung(monkeypatch, dong, hop, *, cho_xong=0.2, lenh_nhip=lambda: None):
    def xu_ly(p, *, khe_id, giao_id, luot, tu_dong=0):
        return [DongHangDoi(i, {**t, "request_id": f"r-{i}"}) for i, t in enumerate(dong) if i >= tu_dong], len(dong)
    monkeypatch.setattr(theo_doi, "xu_ly_hang_doi", xu_ly)
    pc = SimpleNamespace(hang_doi=None, hop=hop, wt=None, luu=lambda: None,
                         p=SimpleNamespace(khe_id="B/claude-1", giao_id="g-1", luot=1),
                         tt=SimpleNamespace(vi_tri_hang_doi=0, ban_giao_tam=None))
    nc = SimpleNamespace(khach=None, cho_doc=0.01, cho_xong=cho_xong, cho_thu_lai=0.01,
                         ch=SimpleNamespace(tren_may_b=False, chay=SimpleNamespace(day="kho-tho")))
    return TheoDoi(pc, nc, threading.Event(), lenh_nhip=lenh_nhip), pc


def test_luong_ket_io_thi_ket_thuc_tra_loi_trong_han_khong_doc_song_song(monkeypatch):
    hop = Hop(chan=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}], hop)
    td.bat_dau()
    assert hop.vao.wait(5)
    t0 = time.monotonic()
    try:
        with pytest.raises(LoiThuHoi):
            td.ket_thuc(han=0.2)
        assert time.monotonic() - t0 < 2 and hop.da == [] and pc.tt.vi_tri_hang_doi == 0
    finally:
        hop.tha.set()
        td._luong.join(5)
    assert hop.da == ["r-0"]                                            # chỉ luồng nền giao, không lần đọc thứ hai


def test_huy_giua_cac_dong_dong_con_lai_giao_dung_mot_lan(monkeypatch):
    hop = Hop(chan=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}, {"loai": "moc"}, {"loai": "moc"}], hop)
    td.bat_dau()
    assert hop.vao.wait(5)
    kt = threading.Thread(target=td.ket_thuc, kwargs={"han": 5})
    kt.start()
    time.sleep(0.1)
    hop.tha.set()
    kt.join(10)
    assert not kt.is_alive() and hop.da == ["r-0", "r-1", "r-2"] and pc.tt.vi_tri_hang_doi == 3


def test_xong_dat_dung_dung_han_khi_luong_ket_va_ket_thuc_huy_hen(monkeypatch):
    ket = threading.Event()
    td, _ = dung(monkeypatch, [{"loai": "xong"}], Hop(), lenh_nhip=lambda: ket.wait(10) and None)
    td.bat_dau()
    try:
        assert td.dung.wait(3) and td.xong is not None                 # hẹn 0,2 s chạy dù luồng đang kẹt
    finally:
        ket.set()
        td.ket_thuc(han=5)
    td2, _ = dung(monkeypatch, [{"loai": "xong"}], Hop(), cho_xong=5)
    td2.mot_luot()
    td2.ket_thuc(han=5)
    time.sleep(0.1)
    assert not td2.dung.is_set() and not td2._hen.is_alive()


def test_loi_o_luong_nen_thi_doc_cuoi_thu_lai_dung_mot_lan(monkeypatch):
    hop = Hop(nem=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}], hop)
    td.bat_dau()
    het = time.monotonic() + 5
    while td.loi_nen is None and time.monotonic() < het:
        time.sleep(0.01)
    td.ket_thuc(han=5)
    assert td.loi_nen == "RuntimeError" and hop.da == ["r-0"] and pc.tt.vi_tri_hang_doi == 1


def test_doc_cuoi_ket_io_thi_ket_thuc_tra_loi_trong_mot_han(monkeypatch):
    """A06: hạn của `ket_thuc` bao trùm cả lần đọc cuối — chặn RIÊNG lần đọc cuối (luồng nền không có gì kẹt)."""
    hop = Hop(chan=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}], hop)              # không bat_dau: dòng chỉ được đọc ở lần cuối
    t0 = time.monotonic()
    try:
        with pytest.raises(LoiThuHoi):
            td.ket_thuc(han=0.3)
        assert time.monotonic() - t0 < 2 and hop.vao.is_set() and pc.tt.vi_tri_hang_doi == 0
    finally:
        hop.tha.set()


class HopCham(Hop):
    def gui_mot(self, khach, duong, than):
        time.sleep(0.05)
        self.da.append(than["request_id"])


def test_backlog_nhieu_dong_doc_cuoi_thoi_o_ranh_gioi_dong_trong_han(monkeypatch):
    hop = HopCham()
    td, pc = dung(monkeypatch, [{"loai": "moc"}] * 50, hop)
    t0 = time.monotonic()
    with pytest.raises(LoiThuHoi):
        td.ket_thuc(han=0.5)
    assert time.monotonic() - t0 < 1.5
    td._luong_cuoi[0].join(5)                                       # luồng đọc cuối thôi ở ranh giới dòng kế tiếp
    assert 0 < len(hop.da) < 50 and len(set(hop.da)) == len(hop.da) and pc.tt.vi_tri_hang_doi == len(hop.da)


def test_xong_gap_o_lan_doc_cuoi_khong_tao_hen_sau_khi_dung(monkeypatch):
    td, _ = dung(monkeypatch, [{"loai": "xong"}], Hop(), cho_xong=0.1)
    td.ket_thuc(han=5)
    time.sleep(0.3)
    assert td.xong is not None and not td.dung.is_set() and td._hen is None
    td._dat_hen()                                                   # đã bắt đầu dừng: không bao giờ tạo hẹn mới
    assert td._hen is None
