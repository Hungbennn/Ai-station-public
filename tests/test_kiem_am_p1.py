"""bs-863.14: thăm dò cách ly qua primitive P1 — hạn tuyệt đối, thu hồi cả cây bằng `kill` của principal; lỗi hạ tầng
(quá hạn, không khởi chạy, chưa thu hồi) KHÔNG BAO GIỜ thành "bị chặn"; dương hỏng → âm không kết luận. Chạy/kill GIẢ,
trừ một ca dùng `python -c` của chính user đang test (tự thu hồi đúng PID mình tạo)."""
import os
import signal
import subprocess
import sys
import time

from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo
from tram.tho.kiem_am import ThamDo, chay_tham_do

DS = [ThamDo("keychain", ["/usr/bin/security"], "keychain"), ThamDo("đọc", ["/bin/cat"], "doc"),
      ThamDo("hợp lệ", ["/usr/bin/true"], "ok")]
LOI = {44: "The specified item could not be found in the keychain.", 1: "cat: x: Permission denied"}


def chay_gia(ket: dict, goi: list):
    def chay(argv, **kw):
        goi.append((argv, kw))
        r = ket[argv[-1]]
        if isinstance(r, BaseException):
            raise r
        return subprocess.CompletedProcess(argv, r, "", LOI.get(r, ""))
    return chay


def test_qua_p1_voi_kill_cua_principal_duong_chay_truoc():
    goi, kill = [], lambda g, s: None
    kq = chay_tham_do(DS, boc=lambda a: ["/usr/bin/sudo", "-n", *a], env={"PATH": "/x"}, kill=kill,
                      chay=chay_gia({"/usr/bin/security": 44, "/bin/cat": 1, "/usr/bin/true": 0}, goi))
    assert [k.dat for k in kq] == [True, True, True] and [k.ten for k in kq] == ["keychain", "đọc", "hợp lệ"]
    assert [a[-1] for a, _ in goi] == ["/usr/bin/true", "/usr/bin/security", "/bin/cat"]
    assert all(a[:2] == ["/usr/bin/sudo", "-n"] and kw["kill"] is kill and kw["timeout"] == 30
               and kw["env"] == {"PATH": "/x"} for a, kw in goi)


def test_loi_ha_tang_khong_bao_gio_la_bi_chan():
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia(
        {"/usr/bin/security": subprocess.TimeoutExpired("x", 30), "/bin/cat": OSError("spawn"),
         "/usr/bin/true": 0}, []))
    assert [k.dat for k in kq] == [False, False, True] and all("không kết luận" in k.chi_tiet for k in kq[:2])


def test_duong_hong_thi_am_khong_chay_khong_xanh():
    goi = []
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia({"/usr/bin/true": 1}, goi))
    assert [k.dat for k in kq] == [False, False, False] and len(goi) == 1 and "dương" in kq[0].chi_tiet


def test_chua_thu_hoi_duoc_thi_dung_khong_chay_tiep():
    goi = []
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia(
        {"/usr/bin/true": 0, "/usr/bin/security": LoiThuHoi("x"), "/bin/cat": 1}, goi))
    assert [k.dat for k in kq] == [False, False, True] and [a[-1] for a, _ in goi] == ["/usr/bin/true",
                                                                                          "/usr/bin/security"]


def test_that_qua_han_va_kill_bi_tu_choi_van_tra_trong_han():
    from functools import partial
    from tram.kiem.chay_gioi_han import chay_gioi_han
    from tram.kiem.vong_doi import khoi_chay

    cac_chu = []
    treo = "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)"

    def khoi(argv, **kw):
        cac_chu.append(kw["chu"])
        return khoi_chay(argv, **kw)

    def tu_choi(g, s):
        raise PermissionError

    t0 = time.monotonic()
    try:
        kq = chay_tham_do([ThamDo("treo", ["x"], "doc")], boc=lambda a: [sys.executable, "-c", treo],
                          env=dict(os.environ), kill=tu_choi, timeout=0.5,
                          chay=partial(chay_gioi_han, khoi=khoi))
        assert cac_chu and len(cac_chu[0]) == 1
        assert time.monotonic() - t0 < 10 and not kq[0].dat and "không kết luận" in kq[0].chi_tiet
    finally:
        for chu in cac_chu:
            for n in chu:
                if n.p.returncode is None:
                    n.p.kill()
                n.p.wait(timeout=5)
                n.goc.gat()
