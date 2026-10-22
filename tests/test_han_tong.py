"""Hạn tổng harness (3C-B): tiến trình con thay luồng nền; quá hạn thu hồi cả cây; cổng chỉ mở khi dọn xác nhận.
Harness giả là `python -c` của chính user đang test; `don` là spy (không chạm lịch thật)."""
import os
import signal
import sys
import time

import pytest

from test_vong_doi import KILL_UID
from tram.kiem.han_tong import HetHanTong, chay_han_tong, cong_dong
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable
TREO = ("import subprocess, sys, time\n"
        "c = subprocess.Popen([sys.executable, '-c', 'import signal, time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'], start_new_session=True)\n"
        "open('chau.pid', 'w').write(str(c.pid)); time.sleep(60)\n")


def _song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_qua_han_thu_hoi_ca_chau_roi_don_va_mo_cong(tmp_path):
    don, dau, t0 = [], tmp_path / "cong" / "kiem.dong", time.monotonic()
    with pytest.raises(HetHanTong, match="đã thu hồi và dọn"):
        chay_han_tong([PY, "-c", TREO], han=1.0, kill=KILL_UID, dau=dau, don=lambda: don.append(1) or True,
                      cwd=tmp_path)
    chau = int((tmp_path / "chau.pid").read_text())
    assert time.monotonic() - t0 < 10 and not _song(chau) and don == [1] and not cong_dong(dau)


@pytest.mark.parametrize("don", [lambda: False, lambda: None, lambda: 1 / 0])
def test_don_khong_xac_nhan_thi_cong_giu_dong_va_luot_sau_bi_tu_choi(tmp_path, don):
    dau = tmp_path / "kiem.dong"
    with pytest.raises(LoiThuHoi, match="cổng giữ đóng"):
        chay_han_tong([PY, "-c", "pass"], han=10, kill=kill_cuc_bo, dau=dau, don=don)
    assert cong_dong(dau)
    goi = []
    with pytest.raises(LoiThuHoi, match="cổng đang đóng"):
        chay_han_tong([PY, "-c", "pass"], han=10, kill=kill_cuc_bo, dau=dau, don=lambda: True,
                      khoi=lambda *a, **k: goi.append(1))
    assert goi == []


def test_xong_trong_han_tra_ma_va_mo_cong(tmp_path):
    dau = tmp_path / "kiem.dong"
    assert chay_han_tong([PY, "-c", "import sys; sys.exit(1)"], han=10, kill=kill_cuc_bo, dau=dau,
                         don=lambda: True) == 1
    assert not cong_dong(dau)


def test_kill_bi_tu_choi_van_don_lich_va_cong_giu_dong(tmp_path):
    dau, pid, don = tmp_path / "kiem.dong", [], []

    def khoi(argv, **kw):
        n = khoi_chay(argv, **kw)
        pid.append(n.p.pid)
        return n
    try:
        with pytest.raises(HetHanTong, match="CỔNG GIỮ ĐÓNG"):
            chay_han_tong([PY, "-c", "import time; time.sleep(60)"], han=0.3, kill=lambda g, s: None, dau=dau,
                          don=lambda: don.append(1) or True, khoi=khoi)
        assert cong_dong(dau) and don == [1]                    # vẫn gỡ lịch dù cây chưa thu hồi được
    finally:
        os.killpg(pid[0], signal.SIGKILL)


@pytest.mark.parametrize("han", [float("inf"), float("nan"), 0])
def test_han_khong_huu_han_bi_tu_choi_truoc_khi_dat_dau(tmp_path, han):
    with pytest.raises(ValueError):
        chay_han_tong([PY, "-c", "pass"], han=han, kill=kill_cuc_bo, dau=tmp_path / "d", don=lambda: True)
    assert not cong_dong(tmp_path / "d")
