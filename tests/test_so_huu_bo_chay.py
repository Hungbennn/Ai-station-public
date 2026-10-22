"""Review vòng 1 A03, vòng 2 R2-02/R2-03/R2-04: bộ chạy `chay_gioi_han` KHÔNG gặt gốc bằng `communicate` (gặt sớm làm
nhóm gốc mất bảo vệ), hạn tính TRƯỚC spawn, mọi bước sau spawn trong vùng sở hữu; lỗi đóng ống/selector/đọc không chặn
thu hồi và không che "chưa xác nhận" (`test_so_huu_ong.py`); `chay_han_tong`: `test_so_huu_han_tong.py`. Tiến
trình thật chỉ là `python -c` của chính user đang test; kênh gửi là bản ghi lại rồi gửi cục bộ."""
import os
import signal
import subprocess
import time

import pytest

from test_vong_doi import CHAU, PY, _song
from tram.kiem import chay_gioi_han as cgh
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo


def test_goc_thoat_nhanh_chau_o_nhom_goc_van_thu_hoi_qua_nhom_goc(tmp_path):
    gui, goc = [], []

    def kill(g, s):
        gui.append(g)
        kill_cuc_bo(g, s)

    def khoi(argv, **kw):
        n = khoi_chay(argv, **kw)
        goc.append(n.p.pid)
        return n
    try:
        r = chay_gioi_han([PY, "-c", CHAU.format(moi=False, ngu=0)], kill=kill, timeout=20, cwd=tmp_path, khoi=khoi)
        chau = int((tmp_path / "chau.pid").read_text())
        assert r.returncode == 0 and not _song(chau) and set(gui) == set(goc)       # chỉ nhóm gốc, số còn giữ bởi xác
    finally:
        if (tmp_path / "chau.pid").exists() and _song(chau := int((tmp_path / "chau.pid").read_text())):
            os.kill(chau, signal.SIGKILL)                   # đúng PID test vừa tạo


def test_han_tinh_truoc_spawn_spawn_cham_thi_het_han_va_van_thu_hoi(monkeypatch):
    goi, con, that = [], [], cgh._ong

    def khoi(a, **kw):
        time.sleep(0.4)                                     # spawn tiêu hết hạn 0,2 s
        goi.append(khoi_chay(a, **kw))
        return goi[-1]

    def ong(n, vao, het):
        con.append(het - time.monotonic())                  # phần hạn còn lại khi bắt đầu đọc
        return that(n, vao, het)
    monkeypatch.setattr(cgh, "_ong", ong)
    with pytest.raises(subprocess.TimeoutExpired):
        chay_gioi_han([PY, "-c", "import time; time.sleep(60)"], kill=kill_cuc_bo, timeout=0.2, khoi=khoi)
    assert con[0] <= 0 and not _song(goi[0].p.pid)
