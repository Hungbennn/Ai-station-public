"""Review vòng 1 A03, vòng 2 R2-02/R2-03: `chay_han_tong` spawn TRONG try/finally thu hồi + dọn — `khoi` hỏng sau khi có
PID, gốc không theo dõi được, ngắt khi `Nhom` đã ở `chu`: thu hồi vẫn chạy, `don()` vẫn chạy, dấu chỉ xoá khi cả hai xác
nhận; dò danh tính không tự gặt gốc. Tiến trình thật chỉ là `python -c` của chính user đang test."""
import signal

import pytest

from test_so_huu import KqLoi
from test_so_huu_ngat import Ngat, ngat
from test_so_huu_ong import NhomGia
from test_vong_doi import PY, SUDO, PopenGia
from tram.kiem import giu_xac
from tram.kiem.danh_tinh import LoiDanhTinh, quan_sat
from tram.kiem.han_tong import chay_han_tong
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo


def test_han_tong_khoi_chay_hong_sau_khi_co_pid_van_don_va_giu_dau(tmp_path):
    goi = []

    def khoi(*a, **kw):
        raise LoiThuHoi("khởi chạy hỏng sau khi đã có tiến trình")
    with pytest.raises(LoiThuHoi):
        chay_han_tong(["gia"], han=1, kill=kill_cuc_bo, dau=tmp_path / "dau", don=lambda: goi.append(1) or True,
                      khoi=khoi)
    assert goi == [1] and (tmp_path / "dau").exists()


def test_han_tong_goc_khong_theo_doi_duoc_nhom_trong_chu_van_bi_giet_dau_giu(tmp_path, monkeypatch):
    goi, chu = [], []
    monkeypatch.setattr(giu_xac, "_kqueue", KqLoi)

    def khoi(a, **kw):
        chu.append(kw["chu"])
        return khoi_chay(a, **kw)
    try:
        with pytest.raises(LoiThuHoi, match="chưa xác nhận"):
            chay_han_tong([PY, "-c", "import time; time.sleep(60)"], han=5, kill=kill_cuc_bo, dau=tmp_path / "dau",
                          don=lambda: goi.append(1) or True, khoi=khoi)
        n, = chu[0]
        assert goi == [1] and (tmp_path / "dau").exists() and n.ket_thu_hoi is False and n.p.returncode is None
        assert n.p.wait(5) in (-signal.SIGTERM, -signal.SIGKILL)                  # nhóm gốc (chưa gặt) đã bị giết
    finally:
        for n in (chu[0] if chu else []):
            if n.p.poll() is None:
                n.p.kill()
                n.p.wait(5)


def test_han_tong_ngat_sau_khi_nhan_nhom_van_thu_hoi_nhom_trong_danh_sach(tmp_path):
    n, goi = NhomGia(True), []

    def khoi(*a, chu, **kw):
        chu.append(n)                                       # `khoi_chay` đã đưa Nhom vào danh sách sở hữu
        raise KeyboardInterrupt                             # ngắt được phát lại khi rời `hoan()`, trước khi trả
    with pytest.raises(KeyboardInterrupt):
        chay_han_tong(["gia"], han=1, kill=kill_cuc_bo, dau=tmp_path / "dau", don=lambda: goi.append(1) or True,
                      khoi=khoi)
    assert n.da == ["thu"] and goi == [1] and not (tmp_path / "dau").exists()


def test_han_tong_ngat_lan_hai_luc_thu_hoi_ghi_ket_qua_roi_moi_nem(tmp_path):
    goi, cu = [], signal.signal(signal.SIGINT, ngat)                # handler của người gọi

    class N:
        def cho(self, han):
            raise Ngat("lần một")

        def thu_hoi(self):
            signal.raise_signal(signal.SIGINT)                      # lần hai, giữa lúc thu hồi: được hoãn
            goi.append("thu")
            return True
    try:
        with pytest.raises(Ngat):
            chay_han_tong(["gia"], han=1, kill=kill_cuc_bo, dau=tmp_path / "dau",
                          don=lambda: goi.append("don") or True, khoi=lambda a, **kw: N())
        assert goi == ["thu", "don"] and not (tmp_path / "dau").exists()
    finally:
        signal.signal(signal.SIGINT, cu)


class PopenDem(PopenGia):
    """Gốc không bao giờ thoát; đếm số lần `poll` (gặt) bị gọi."""
    def __init__(self):
        self.dem = 0

    def poll(self):
        self.dem += 1
        return None


def test_do_danh_tinh_khong_tu_gat_goc():
    p = PopenDem()
    with pytest.raises((LoiDanhTinh, LoiThuHoi)):
        quan_sat(lambda a: a, lambda g, s: None, khoi=lambda argv, **kw: khoi_chay(argv, popen=lambda a, **k: p, **kw),
                 chup=lambda: [SUDO], han=0.2)
    assert p.dem == 0                                       # chỉ `Nhom.thu_hoi` (khi đã xác nhận) mới gặt
