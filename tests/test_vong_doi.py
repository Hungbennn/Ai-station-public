"""Primitive vòng đời tiến trình (lát P1): hạn hữu hạn, thu hồi cả cây. Tiến trình thật chỉ là `python -c` của chính
user đang test, trong tmp_path, tự thu hồi; ca sudo/root/kill bị từ chối dùng Popen/ps/kill GIẢ. Nhóm ngoài gốc chỉ được
gửi qua kênh theo UID dành riêng (A01): ca thật dùng `KILL_UID` — principal `user` GIẢ, UID riêng = chính user test."""
import os
import signal
import subprocess
import sys
import time

import pytest

from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.vong_doi import Nhom, khoi_chay, kill_cuc_bo

PY = sys.executable
SUDO = TienTrinh(4242, 1, 4242, 0, 501)
CHAU = ("import subprocess, sys, time\n"
        "c = subprocess.Popen([sys.executable, '-c', 'import signal, time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'], start_new_session={moi})\n"
        "open('chau.pid', 'w').write(str(c.pid)); time.sleep({ngu})\n")


class PrCungUser:
    """Principal cơ chế `user` GIẢ: trong test "UID dành riêng" là chính user đang test (`gui_tin.kill_uid` nhận nó)."""
    co_che = "user"

    def kill_nhom(self, pgid, sig):
        kill_cuc_bo(pgid, sig)


KILL_UID = PrCungUser().kill_nhom


class PopenGia:
    """Gốc không bao giờ thoát (vd. `sudo` root không nhận tín hiệu của tiến trình quản lý)."""
    pid, returncode = 4242, None

    def wait(self, timeout=None):
        time.sleep(min(timeout or 0, 0.05))
        raise subprocess.TimeoutExpired("x", timeout)

    def poll(self):
        return None


def _song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _chau(tmp_path, *, moi: bool, ngu: float, kill=KILL_UID):
    n = khoi_chay([PY, "-c", CHAU.format(moi=moi, ngu=ngu)], kill=kill, chu=[], cwd=tmp_path)
    het = time.monotonic() + 10
    while not (tmp_path / "chau.pid").exists() and time.monotonic() < het:
        time.sleep(0.02)
    return n, int((tmp_path / "chau.pid").read_text())


def test_treo_sau_sigkill_tra_false_trong_han():
    gui = []

    def kill(g, sig):
        gui.append((g, sig))
        raise PermissionError
    n, t0 = Nhom(PopenGia(), kill=kill, chup=lambda: [SUDO]), time.monotonic()
    assert n.thu_hoi(cho_term=0.2, cho_cuoi=0.2, han_gui=0.2) is False
    assert time.monotonic() - t0 < 1.5 and gui == [(4242, signal.SIGTERM), (4242, signal.SIGKILL)]
    with pytest.raises(ValueError):
        n.cho(float("inf"))


def test_kill_cham_nhieu_nhom_moi_pha_van_gui_va_co_han():
    cay = [SUDO, *(TienTrinh(5000 + i, 4242, 5000 + i, 502, 502, 7 + i) for i in range(50))]
    gui = []

    class Cham(PrCungUser):
        def kill_nhom(self, g, sig):
            gui.append(sig)
            time.sleep(0.1)
            raise subprocess.TimeoutExpired(["kill"], 0.1)
    t0, mot = time.monotonic(), lambda pid: next((t for t in cay if t.pid == pid), None)
    assert Nhom(PopenGia(), kill=Cham().kill_nhom, chup=lambda: cay, mot=mot).thu_hoi(cho_term=0.1, cho_cuoi=0.1,
                                                                                       han_gui=0.3) is False
    assert time.monotonic() - t0 < 2 and signal.SIGKILL in gui and 2 < len(gui) < 20


def test_da_thoat_cay_rong_khong_gui_gi():
    p = subprocess.Popen([PY, "-c", "pass"], start_new_session=True)
    p.wait(10)
    gui = []
    assert Nhom(p, kill=lambda g, s: gui.append(g), chup=lambda: []).thu_hoi() is True and gui == []


@pytest.mark.parametrize("moi, ngu, cha_thoat", [(True, 60, False), (False, 0, True), (True, 1.5, True)])
def test_thu_hoi_chau_bo_qua_sigterm(tmp_path, moi, ngu, cha_thoat):
    """Cháu ở phiên mới (như pty của sudo) hoặc cùng nhóm; cha còn chạy hoặc đã thoát bình thường."""
    n, chau = _chau(tmp_path, moi=moi, ngu=ngu)
    try:
        assert (n.cho(10) == 0) if cha_thoat else (n.cho(0.3) is None)
        t0 = time.monotonic()
        assert n.thu_hoi(cho_term=0.3, cho_cuoi=3) is True and time.monotonic() - t0 < 6 and not _song(chau)
    finally:
        kill_cuc_bo(n.p.pid, signal.SIGKILL)
        if _song(chau):
            os.kill(chau, signal.SIGKILL)


def test_kenh_cuc_bo_khong_gui_nhom_ngoai_goc_chau_tach_phien_thi_khong_xac_nhan(tmp_path):
    """A01: kênh cục bộ (tài khoản quản lý/trạm chạy nhiều việc khác) không bao giờ gửi nhóm ngoài gốc."""
    n, chau = _chau(tmp_path, moi=True, ngu=60, kill=kill_cuc_bo)
    try:
        assert n.cho(0.3) is None and n.thu_hoi(cho_term=0.2, cho_cuoi=0.5) is False and _song(chau)
    finally:
        kill_cuc_bo(n.p.pid, signal.SIGKILL)
        if _song(chau):
            os.kill(chau, signal.SIGKILL)


def test_khoi_chay_luon_nhom_rieng():
    goi = []

    def popen(argv, **kw):
        goi.append(kw)
        return PopenGia()
    khoi_chay(["x"], kill=kill_cuc_bo, chu=[], popen=popen, start_new_session=False, cwd="/")
    assert goi == [{"start_new_session": True, "cwd": "/"}]
