"""Hợp đồng sở hữu (`tram/kiem/so_huu.py`; review vòng 1 A03, vòng 2 R2-01/R2-02): sau Popen, `Nhom` LUÔN vào danh sách
sở hữu của người gọi trước mọi lối ra; nhánh lỗi đăng ký kqueue KHÔNG gặt gốc (xác giữ số nhóm) nên không tín hiệu nào
trúng nhóm được cấp lại; kill bị từ chối/gốc treo → `LoiThuHoi`, `Nhom` vẫn trong `chu`. Ngắt lúc spawn:
`test_so_huu_ngat.py`; mọi người gọi: `test_so_huu_nguoi_goi.py`. Nhân/Popen GIẢ cho ca tái dùng số — `os.killpg` thật
bị thay bằng bản ghi để không tín hiệu nào rời test; tiến trình thật chỉ là `python -c` của chính user đang test."""
import errno
import os
import select
import signal
import subprocess
import sys

import pytest

from test_vong_doi import PopenGia
from tram.kiem import giu_xac
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.so_huu import so_huu, thu_hoi_con_lai
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

NGU = [sys.executable, "-c", "import time; time.sleep(60)"]
QUAN_LY = os.getuid()
GOC = TienTrinh(4242, 1, 4242, QUAN_LY, QUAN_LY, 42)
LA = TienTrinh(7000, 1, 4242, QUAN_LY, QUAN_LY, 70)      # việc khác của tài khoản quản lý nhận lại số nhóm 4242


class KqLoi:
    """kqueue đăng ký trả receipt lỗi KHÁC ESRCH (vd. EINVAL)."""
    def control(self, ds, n, t):
        return [select.kevent(ds[0].ident, select.KQ_FILTER_PROC, select.KQ_EV_ERROR, 0, errno.EINVAL)]

    def close(self):
        pass


class Nhan:
    """Nhân GIẢ: gửi tới nhóm g trúng mọi tiến trình mang nhóm g lúc gửi."""
    def __init__(self):
        self.bang, self.trung = [GOC], []

    def chup(self):
        return list(self.bang)

    def kill(self, g, sig):
        self.trung += [(t.pid, sig) for t in self.bang if t.pgid == g]


class PopenTaiCap(subprocess.Popen):
    """Gốc đã là xác; GẶT nó thì số 4242 về nhân và được cấp ngay cho `LA`. Không fork (không gọi `Popen.__init__`)."""
    def __init__(self, nhan):
        self.pid, self.returncode, self.nhan = 4242, None, nhan
        self.stdin = self.stdout = self.stderr = None

    def poll(self):
        if self.returncode is None:
            self.returncode, self.nhan.bang = 0, [LA]
        return self.returncode

    def wait(self, timeout=None):
        return self.poll()


def test_dang_ky_loi_khac_esrch_khong_gat_goc_va_khong_tin_hieu_nao_trung_nhom_thay_the(monkeypatch):
    nh, that, chu = Nhan(), [], []
    monkeypatch.setattr(giu_xac, "_kqueue", KqLoi)
    monkeypatch.setattr(os, "killpg", lambda g, s: that.append((g, s)))
    with pytest.raises(LoiThuHoi):
        khoi_chay(["gia"], kill=nh.kill, chu=chu, popen=lambda a, **kw: PopenTaiCap(nh), chup=nh.chup)
    assert thu_hoi_con_lai(chu, cho_term=0.1, cho_cuoi=0.1, han_gui=1) is False      # không bao giờ xác nhận
    assert 7000 not in {pid for pid, _ in nh.trung} and that == []
    assert len(chu) == 1 and chu[0].p.returncode is None and nh.trung                 # xác giữ số; gốc vẫn được gửi


def test_dang_ky_loi_voi_con_that_van_giu_xac_va_giet_duoc_nhom_goc(monkeypatch):
    monkeypatch.setattr(giu_xac, "_kqueue", KqLoi)
    chu = []
    try:
        with pytest.raises(LoiThuHoi, match="chưa xác nhận"):
            khoi_chay(NGU, kill=kill_cuc_bo, chu=chu)
        assert thu_hoi_con_lai(chu, cho_term=0.2, cho_cuoi=0.5) is False and chu[0].p.returncode is None
        assert chu[0].p.wait(5) in (-signal.SIGTERM, -signal.SIGKILL)                 # nhóm gốc (chưa gặt) bị giết
    finally:
        for n in chu:
            if n.p.poll() is None:
                n.p.kill()
                n.p.wait(5)


@pytest.mark.parametrize("loi_than", [None, RuntimeError("BI-MAT")])
def test_kill_bi_tu_choi_hay_goc_treo_thi_loi_thu_hoi_nhom_van_trong_chu(loi_than):
    def tu_choi(g, s):
        raise PermissionError
    with pytest.raises(LoiThuHoi, match="KHÔNG xác nhận") as e:
        with so_huu("KHÔNG xác nhận — cổng đóng", cho_term=0.1, cho_cuoi=0.1, han_gui=0.2) as chu:
            khoi_chay(["x"], kill=tu_choi, chu=chu, popen=lambda a, **kw: PopenGia(), chup=lambda: [])
            if loi_than:
                raise loi_than
    assert chu[0].ket_thu_hoi is False and chu[0].p.returncode is None              # còn chủ, không gặt
    assert "BI-MAT" not in str(e.value) and (loi_than is None or e.value.__suppress_context__)


def test_khoi_chay_bat_buoc_danh_sach_so_huu_truoc_khi_spawn():
    goi = []
    with pytest.raises(TypeError):
        khoi_chay(["x"], kill=kill_cuc_bo, chu=None, popen=lambda a, **kw: goi.append(1))
    assert goi == []
