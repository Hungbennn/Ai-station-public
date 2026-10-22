"""Hợp đồng P1 H2 (lát 3c): `PrincipalKiem.kill_nhom` gửi tín hiệu dưới `tram-kiem` qua `chay_ngan` — hạn TUYỆT ĐỐI 5 s,
không `subprocess.run(timeout=…)` (CPython còn `wait()` trần khi `kill()` bị từ chối). Không sudo: `chay_ngan` giả."""
import fnmatch
import inspect
import signal

import pytest

from tram.giao_viec import principal_kiem
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
from tram.tho.quyen_kiem import dong_sudoers_kiem


@pytest.mark.parametrize("co_che", ["user", "sandbox"])
def test_kill_nhom_qua_chay_ngan_han_5_giay_khop_sudoers(monkeypatch, co_che):
    goi, pk = [], tu_cach_ly(f"{co_che}:tram-kiem")
    monkeypatch.setattr(principal_kiem, "chay_ngan", lambda argv, **kw: goi.append((argv, kw)) or (0, b""))
    pk.kill_nhom(123, signal.SIGKILL)
    assert goi == [(pk.boc_lenh(["/bin/kill", "-s", "KILL", "--", "-123"]), {"timeout": 5})]
    mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che=co_che).split("NOPASSWD:SETENV: ", 1)[1]
    assert mau == "ALL" or fnmatch.fnmatchcase(" ".join(goi[0][0][goi[0][0].index("--") + 1:]), mau)


def test_kill_nhom_qua_han_tra_ve_khong_cho_va_khong_nhan_chay(monkeypatch):
    goi = []
    monkeypatch.setattr(principal_kiem, "chay_ngan", lambda argv, **kw: goi.append(kw) or (None, b""))  # sudo treo
    PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--")).kill_nhom(9, 15)   # không ném/chờ
    assert goi == [{"timeout": 5}] and "chay" not in inspect.signature(PrincipalKiem.kill_nhom).parameters
