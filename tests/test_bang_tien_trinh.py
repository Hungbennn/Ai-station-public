"""Bảng tiến trình của nhân qua sysctl (V2-0, dot7-C01): định danh sinh (pid, sinh µs), tự kiểm bố cục. Ca giả dùng byte
dựng tay; ca thật CHỈ ĐỌC bảng (như `ps`) và chỉ tạo/giết `python -c` của chính user đang test."""
import os
import struct
import subprocess
import sys

import pytest

from tram.kiem.bang_tien_trinh import CO, chup_nhan, doc_kinfo, mot_nhan, phien_khoi_dong
from tram.kiem.cay_tien_trinh import TienTrinh


def dong(pid, ppid, pgid, uid, ruid, giay=1_700_000_000, micro=5) -> bytes:
    b = bytearray(CO)
    struct.pack_into("<qi", b, 0, giay, micro)
    struct.pack_into("<i", b, 40, pid)
    struct.pack_into("<ii", b, 560, ppid, pgid)
    struct.pack_into("<I", b, 392, ruid)
    struct.pack_into("<I", b, 420, uid)
    return bytes(b)


TOI = dong(os.getpid(), os.getppid(), os.getpgrp(), os.geteuid(), os.getuid())


def test_doc_kinfo_lay_dung_cot_va_sinh_micro_giay():
    ds = doc_kinfo(dong(5000, 4242, 5000, 502, 501, giay=10, micro=7) + TOI)
    assert ds[0] == TienTrinh(5000, 4242, 5000, 502, 501, 10_000_007) and ds[0].khoa == (5000, 10_000_007)
    with pytest.raises(OSError):
        doc_kinfo(TOI + b"\0")


@pytest.mark.parametrize("bang", [dong(5000, 1, 5000, 0, 0),                      # thiếu dòng của chính mình
                                  dong(os.getpid(), 1, 1, 0, 0),                  # bố cục lệch: cột không khớp
                                  TOI + TOI],                                     # hai dòng cùng pid
                         ids=["thieu-toi", "lech-cot", "trung-pid"])  # PID mỗi worker khác nhau; tên ca phải cố định.
def test_tu_kiem_bo_cuc_hong_thi_nem(bang):
    with pytest.raises(OSError):
        chup_nhan(doc=lambda mib: bang)
    with pytest.raises(OSError):
        mot_nhan(5000, doc=lambda mib: bang if mib[-1] == os.getpid() else dong(5000, 1, 5000, 0, 0))


def test_mot_nhan_khong_con_thi_none_pid_khong_hop_le_thi_nem():
    assert mot_nhan(5000, doc=lambda mib: TOI if mib[-1] == os.getpid() else b"") is None
    with pytest.raises(ValueError):
        mot_nhan(0)


def test_bang_that_thay_con_cua_minh_voi_sinh_on_dinh():
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
    try:
        con = mot_nhan(p.pid)
        assert con is not None and (con.ppid, con.pgid, con.uid) == (os.getpid(), p.pid, os.geteuid())
        assert next(t for t in chup_nhan() if t.pid == p.pid).sinh == con.sinh
    finally:
        p.kill()
        p.wait(5)
    assert mot_nhan(p.pid) is None or mot_nhan(p.pid).sinh != con.sinh


def test_phien_khoi_dong_on_dinh_va_khong_rong():
    assert phien_khoi_dong() == phien_khoi_dong() and len(phien_khoi_dong()) >= 8
