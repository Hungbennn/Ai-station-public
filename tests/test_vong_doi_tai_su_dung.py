"""V2-0 (dot7-C01): thu hồi KHÔNG BAO GIỜ gửi tín hiệu cho nhóm không chứng minh được thuộc cây — số nhóm/PID có thể
được cấp lại giữa hai ảnh chụp. Popen/bảng tiến trình/kill GIẢ; mỗi ca so ĐÚNG tập nhóm đã nhận tín hiệu."""
import os

from test_vong_doi import SUDO, PopenGia
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.vong_doi import Nhom


class PopenXong(PopenGia):
    """Gốc đã được gặt (mã 0) — số 4242 có thể đã được cấp lại."""
    returncode = 0

    def poll(self):
        return 0


def con(pid, ppid=4242, pgid=None, sinh=None):
    return TienTrinh(pid, ppid, pid if pgid is None else pgid, 502, 502, sinh)


class May:
    """`chup` trả lần lượt các ảnh (ảnh cuối lặp lại; Exception thì ném); `mot` đọc ảnh vừa trả, hoặc `doi` — mô phỏng
    thay đổi GIỮA ảnh chụp và lúc gửi."""
    def __init__(self, *anh, doi=None):
        self.anh, self.i, self.doi, self.hien = list(anh), 0, doi, []

    def chup(self):
        a = self.anh[min(self.i, len(self.anh) - 1)]
        self.i += 1
        if isinstance(a, Exception):
            raise a
        self.hien = a
        return list(a)

    def mot(self, pid):
        if isinstance(self.doi, Exception):
            raise self.doi
        return next((t for t in (self.hien if self.doi is None else self.doi) if t.pid == pid), None)


class Gui:
    """Kênh gửi GIẢ chạy dưới UID dành riêng (principal `user`) — ghi lại mọi nhóm được gửi."""
    co_che = "user"

    def __init__(self):
        self.da = []

    def kill_nhom(self, g, s):
        self.da.append(g)


def thu(may, goc=None):
    gui = Gui()
    n = Nhom(goc or PopenGia(), kill=gui.kill_nhom, chup=may.chup, mot=may.mot)
    n.cay()
    return n.thu_hoi(cho_term=0, cho_cuoi=0, han_gui=1), set(gui.da)


def test_nhom_tai_su_dung_khong_duoc_kill():
    gui = []
    cu = [SUDO, TienTrinh(5000, 4242, 5000, 502, 502)]
    moi = [SUDO, TienTrinh(5000, 1, 5000, 502, 502)]
    anh = iter([cu, moi])
    n = Nhom(PopenGia(), kill=lambda g, s: gui.append(g),
             chup=lambda: next(anh, moi))
    n.cay()
    assert n.thu_hoi(cho_term=0, cho_cuoi=0, han_gui=1) is False
    assert 5000 not in gui


def test_cung_so_cung_uid_sinh_khac_khong_nhan():
    assert thu(May([SUDO, con(5000, sinh=11)], [SUDO, con(5000, ppid=1, sinh=22)])) == (False, {4242})


def test_mo_coi_da_thay_doi_nhom_van_theo_no_so_nhom_cu_thi_mo_ho():
    # 5001 đã thấy; cha chết (ppid=1), nó sang nhóm 6000. Nhóm cũ 5001 giờ có 5002 lạ → mơ hồ: không gửi, không xác nhận
    may = May([SUDO, con(5001, sinh=11)],
              [SUDO, con(5001, ppid=1, pgid=6000, sinh=11), con(5002, ppid=1, pgid=5001, sinh=12), con(5000, ppid=1)])
    assert thu(may) == (False, {4242, 6000})


def test_mo_coi_hop_le_cung_sinh_van_bi_gui():
    assert thu(May([SUDO, con(5001, sinh=11)], [SUDO, con(5001, ppid=1, sinh=11)])) == (False, {4242, 5001})


def test_khong_chup_duoc_luc_gui_chi_nhom_goc_chua_gat():
    assert thu(May([SUDO, con(5001, sinh=11)], OSError("sysctl"))) == (False, {4242})
    assert thu(May([con(5001, ppid=1, sinh=11)], OSError("sysctl")), PopenXong()) == (False, set())


def test_goc_da_gat_cay_rong_thi_xac_nhan_khong_gui_gi():
    assert thu(May([]), PopenXong()) == (True, set())


def test_goc_da_gat_tien_trinh_mang_so_nhom_goc_la_mo_ho():
    # fork rồi cha thoát TRƯỚC ảnh đầu, người khác đã gặt gốc: số 4242 có thể đã cấp lại → không gửi, không xác nhận
    assert thu(May([con(7000, ppid=1, pgid=4242, sinh=5)]), PopenXong()) == (False, set())


def test_fork_setsid_truoc_anh_dau_nhom_khong_thay_duoc_khong_gui():
    # GIỚI HẠN của MỘT `Nhom` (polling): tách phiên + cha thoát trước ảnh đầu → không thấy, không gửi gì; True ở đây chỉ
    # nghĩa "cây QUAN SÁT ĐƯỢC đã hết". Khe thợ không dừng ở đây: `tho.don_uid` quét toàn UID của khe trước khi sang
    # lượt sau (test_don_uid.py, test_khe_tan_du.py); `tram-kiem` có `cong_that.thu_hoi_theo_uid`.
    assert thu(May([con(8000, ppid=1, sinh=7)]), PopenXong()) == (True, set())


def test_khong_bao_gio_gui_nhom_0_1_va_nhom_cua_quan_ly():
    ql = os.getpgrp()
    may = May([SUDO, con(5001, pgid=0, sinh=1), con(5002, pgid=1, sinh=2), con(5003, pgid=ql, sinh=3)])
    assert thu(may) == (False, {4242})


def test_neo_doi_giua_anh_va_luc_gui_thi_khong_gui():
    truoc = [SUDO, con(5001, sinh=11)]
    assert thu(May(truoc, doi=[SUDO, con(5001, ppid=1, sinh=99)])) == (False, {4242})      # số 5001 đã cấp lại
    assert thu(May(truoc, doi=[SUDO, con(5001, pgid=6000, sinh=11)])) == (False, {4242})   # neo rời nhóm 5001
    assert thu(May(truoc, doi=OSError("sysctl"))) == (False, {4242})                      # không kiểm lại được


def test_neo_dau_da_chet_thanh_vien_khac_con_thi_van_gui():
    may = May([SUDO, con(5001, sinh=11), con(5002, pgid=5001, sinh=12)], doi=[SUDO, con(5002, pgid=5001, sinh=12)])
    assert thu(may) == (False, {4242, 5001})
