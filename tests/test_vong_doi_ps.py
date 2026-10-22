"""Primitive P1 khi không chụp được bảng tiến trình LÚC GỬI (V2-0): không dùng ảnh cũ làm bằng chứng — chỉ nhóm gốc
chưa gặt (số chưa thể cấp lại) được gửi, kết quả không xác nhận. Popen/bảng/kill GIẢ."""
import signal

from test_vong_doi import SUDO, PopenGia
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.vong_doi import Nhom


def _chup_hong_tu_lan(k):
    lan = []

    def chup():
        lan.append(1)
        if len(lan) >= k:
            raise OSError("ps")
        return [SUDO, TienTrinh(5000, 4242, 5000, 502, 502, 11)]
    return chup


def test_khong_chup_duoc_luc_gui_chi_gui_nhom_goc_va_khong_xac_nhan():
    gui = []
    n = Nhom(PopenGia(), kill=lambda g, s: gui.append((g, s)), chup=_chup_hong_tu_lan(2), mot=lambda pid: None)
    n.cay()
    assert n.thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.1) is False
    assert gui == [(4242, signal.SIGTERM), (4242, signal.SIGKILL)]


def test_anh_cu_khong_con_la_bang_chung_du_vua_chup():
    gui = []
    n = Nhom(PopenGia(), kill=lambda g, s: gui.append(g), chup=_chup_hong_tu_lan(3), mot=lambda pid: None)
    n.cay()
    assert n.thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.1) is False and set(gui) == {4242}
