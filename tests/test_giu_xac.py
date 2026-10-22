"""V2-0: `Nhom` biết gốc đã thoát mà KHÔNG gặt — xác giữ số nhóm gốc tới khi thu hồi xác nhận xong; đăng ký kqueue lỗi
khác ESRCH thì KHÔNG gặt (R2-01). Tiến trình thật chỉ là `python -c` của chính user đang test, nhóm riêng, tự thu hồi
đúng PID mình tạo."""
import errno
import os
import signal
import subprocess
import sys
import time

import pytest

from test_vong_doi import _chau, _song
from tram.kiem import giu_xac
from tram.kiem.bang_tien_trinh import mot_nhan
from tram.kiem.giu_xac import Goc
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo


def test_cho_tra_ma_nhung_giu_xac_toi_khi_thu_hoi_xong():
    n = khoi_chay([sys.executable, "-c", "import sys; sys.exit(7)"], kill=kill_cuc_bo, chu=[])
    try:
        assert n.cho(10) == 7
        xac = mot_nhan(n.p.pid)
        assert n.p.returncode is None and xac is not None and xac.pgid == n.p.pid       # còn xác, giữ số nhóm
        assert n.thu_hoi(cho_term=0.3, cho_cuoi=1) is True
        assert n.p.returncode == 7 and mot_nhan(n.p.pid) is None
    finally:
        if n.p.returncode is None:
            n.p.kill()
            n.p.wait(5)


def test_mo_coi_o_nhom_goc_sau_khi_goc_thoat_van_bi_thu_hoi(tmp_path):
    n, chau = _chau(tmp_path, moi=False, ngu=0)                 # cha thoát ngay, cháu cùng nhóm gốc bỏ qua SIGTERM
    try:
        assert n.cho(10) == 0 and n.p.returncode is None and mot_nhan(chau).pgid == n.p.pid
        assert n.thu_hoi(cho_term=0.3, cho_cuoi=3) is True and not _song(chau)
    finally:
        if n.p.returncode is None:
            kill_cuc_bo(n.p.pid, signal.SIGKILL)
        if _song(chau):
            os.kill(chau, signal.SIGKILL)


def test_goc_thoat_truoc_khi_dang_ky_van_lay_dung_ma():
    p = subprocess.Popen([sys.executable, "-c", "import sys; sys.exit(3)"], start_new_session=True)
    time.sleep(1.0)                                             # thường đã là xác → kqueue trả ESRCH → gặt ngay
    g = Goc(p)
    assert g.thoat(10) is True and g.ma() == 3
    g.gat()
    assert p.returncode == 3 and mot_nhan(p.pid) is None


class KqLoi:
    def control(self, ds, n, t):
        import select
        return [select.kevent(ds[0].ident, select.KQ_FILTER_PROC, select.KQ_EV_ERROR, 0, errno.EINVAL)]

    def close(self):
        pass


def kq_khong_tao_duoc():
    raise OSError(errno.EMFILE, "quá nhiều fd")


class KqDongLoi(KqLoi):
    def close(self):
        raise OSError(errno.EBADF, "đóng kqueue lỗi")


@pytest.mark.parametrize("kq", [KqLoi, kq_khong_tao_duoc, KqDongLoi])
def test_dang_ky_loi_khac_esrch_tren_xac_thi_khong_gat_va_khong_bao_gio_xac_nhan_thoat(monkeypatch, kq):
    p = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
    try:
        time.sleep(0.5)                                         # gốc đã là xác
        monkeypatch.setattr(giu_xac, "_kqueue", kq)
        g = Goc(p)
        assert g.hong and p.returncode is None and mot_nhan(p.pid) is not None          # xác còn giữ số nhóm
        assert g.thoat(0.1) is False and g.chua_gat() and g.ma() is None
    finally:
        p.wait(5)


def test_kqueue_loi_khi_doc_van_thu_hoi_va_bao_loi_thu_hoi(monkeypatch):
    from types import SimpleNamespace
    from tram.kiem.so_huu import so_huu
    from tram.kiem.vong_doi import LoiThuHoi

    class KqDocLoi(KqDongLoi):
        def control(self, ds, n, t):
            if ds is not None:
                return [SimpleNamespace(flags=0, data=0)]
            raise OSError(errno.EBADF, "đọc kqueue lỗi")

    monkeypatch.setattr(giu_xac, "_kqueue", KqDocLoi)
    chu = []
    try:
        with pytest.raises(LoiThuHoi, match="chưa xác nhận"):
            with so_huu("chưa xác nhận", cho_term=0.0, cho_cuoi=0.0) as chu:
                n = khoi_chay([sys.executable, "-c", "import time; time.sleep(30)"],
                             kill=kill_cuc_bo, chu=chu)
                assert n.cho(0.0) is None and n.goc.hong
        assert len(chu) == 1 and n.ket_thu_hoi is False and n.p.returncode is None
    finally:
        for n in chu:
            n.p.kill()
            n.p.wait(5)
