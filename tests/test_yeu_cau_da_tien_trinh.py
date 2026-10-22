"""Nhiều tiến trình THẬT trên cùng file SQLite tạm và cùng `bd` giả (plan 4d 4D-1c): gửi đồng thời cùng mã, tiến trình
chết thật (`os._exit`) ở từng cửa sổ rồi tiến trình mới tiếp nhận lại. Không `bd` thật, không mạng."""
import multiprocessing as mp
import time

import pytest
from tien_trinh_thu import quan_ly_con
from yeu_cau_gia import LOGIN, MA, BdTep, chay_mot, yc

from tram.yeu_cau.dich_vu import HAN_GIAY, tiep_nhan
from tram.yeu_cau.so_nhan import SoNhan

CTX = mp.get_context("spawn")


def chay(n, db, thu_muc, su_co=None):
    cho, hang = (CTX.Barrier(n) if n > 1 else None), CTX.Queue()
    ds = []
    with quan_ly_con(ds, hang):
        for _ in range(n):
            p = CTX.Process(target=chay_mot, args=(str(db), str(thu_muc), cho, hang, su_co))
            ds.append(p)
            p.start()
        for p in ds:
            p.join(60)
        ma_thoat = [p.exitcode for p in ds]
        assert all(c is not None for c in ma_thoat), "Tiến trình test quá hạn"
        kq = [hang.get(timeout=5) for c in ma_thoat if c == 0]
        return sorted(kq), ma_thoat


def test_bon_tien_trinh_cung_ma_chi_mot_lan_create(tmp_path):
    kq, ma_thoat = chay(4, tmp_path / "sk.db", tmp_path)
    assert ma_thoat == [0, 0, 0, 0]
    assert kq.count("da_tao") == 1 and set(kq) <= {"da_tao", "dang_xu_ly", "da_co"}
    bd = BdTep(tmp_path)
    assert bd.so_lan_tao() == 1 and len(bd.tat_ca()) == 1
    assert tiep_nhan(SoNhan(tmp_path / "sk.db"), bd, yc(), nguoi_gui=LOGIN).trang_thai == "da_co"


@pytest.mark.parametrize("diem, sau_khi_qua_han, so_lan_tao", [
    ("doc", "da_tao", 1),             # chết giữa giữ chỗ và create → tiến trình mới giành chỗ, tạo đúng một lần
    ("truoc_ghi", "khong_ro", 1),     # chết sau khi gọi create, chưa commit → chỉ còn đối soát
    ("sau_ghi", "da_co", 1),          # Beads đã commit, sổ chưa ghi → đối soát ra feature
])
def test_tien_trinh_chet_o_tung_cua_so_roi_khoi_dong_lai(tmp_path, diem, sau_khi_qua_han, so_lan_tao):
    kq, ma_thoat = chay(1, tmp_path / "sk.db", tmp_path, su_co=(diem, "chet"))
    assert (kq, ma_thoat) == ([], [9])
    so, bd = SoNhan(tmp_path / "sk.db"), BdTep(tmp_path)
    assert tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN).trang_thai == "dang_xu_ly"        # chủ cũ còn hạn
    sau = lambda: time.time() + HAN_GIAY + 1                                           # noqa: E731
    assert tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN, dong_ho=sau).trang_thai == sau_khi_qua_han
    assert tiep_nhan(so, bd, yc(), nguoi_gui=LOGIN, dong_ho=sau).trang_thai in ("da_co", "khong_ro")
    assert bd.so_lan_tao() == so_lan_tao and len(bd.tat_ca()) <= 1
    assert so.lay(MA).trang_thai == ("khong_ro" if diem == "truoc_ghi" else "da_tao")
