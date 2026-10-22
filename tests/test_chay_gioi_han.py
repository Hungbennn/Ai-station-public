"""`chay_gioi_han` (3C-B): như `subprocess.run` nhưng có hạn, thu hồi cả cây, ngoại lệ không mang argv/stdout."""
import os
import subprocess
import sys
import time

import pytest

from test_vong_doi import CHAU, KILL_UID, SUDO, PopenGia, _song
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable


def test_giong_run_capture_text_input_check():
    r = chay_gioi_han([PY, "-c", "import sys; print(sys.stdin.read().upper()); sys.exit(3)"], kill=kill_cuc_bo,
                      timeout=10, capture_output=True, text=True, input="abc")
    assert (r.returncode, r.stdout) == (3, "ABC\n")
    with pytest.raises(subprocess.CalledProcessError) as e:
        chay_gioi_han([PY, "-c", "import sys; sys.exit(2)"], kill=kill_cuc_bo, timeout=10, check=True)
    assert e.value.cmd == [PY.rsplit("/", 1)[-1]]


def test_qua_han_thu_hoi_roi_nem_timeout_khong_kem_argv():
    t0 = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired) as e:
        chay_gioi_han([PY, "-c", "import time; time.sleep(60)", "BI-MAT-ARGV"], kill=kill_cuc_bo, timeout=0.3,
                      capture_output=True)
    assert time.monotonic() - t0 < 6 and "BI-MAT-ARGV" not in str(e.value)


def test_goc_khong_chet_thi_loi_thu_hoi():
    def khoi(argv, **kw):
        return khoi_chay(argv, popen=lambda a, **k: _PopenTreo(), chup=lambda: [SUDO], **kw)

    def tu_choi(g, s):
        raise PermissionError
    with pytest.raises(LoiThuHoi):
        chay_gioi_han(["/usr/bin/sudo", "x"], kill=tu_choi, timeout=0.1, khoi=khoi)


def test_chau_tu_tach_phien_khi_dang_chay_van_bi_thu_hoi(tmp_path):
    chay_gioi_han([PY, "-c", CHAU.format(moi=True, ngu=1.5)], kill=KILL_UID, timeout=20, cwd=tmp_path)
    assert not _song(int((tmp_path / "chau.pid").read_text()))


def test_loi_khoi_chay_khong_chep_duong_dan():
    with pytest.raises(OSError) as e:
        chay_gioi_han(["/BI-MAT-THU-MUC/x"], kill=kill_cuc_bo, timeout=1)
    assert "BI-MAT" not in str(e.value)


def test_dau_ra_khong_phai_utf8_van_thu_hoi_va_timeout_phai_huu_han():
    r = chay_gioi_han([PY, "-c", "import sys; sys.stdout.buffer.write(bytes([0xff, 0x41]))"], kill=kill_cuc_bo,
                      timeout=10, capture_output=True, text=True)
    assert r.stdout == "\ufffdA"
    goi = []
    with pytest.raises(ValueError):
        chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=float("inf"), khoi=lambda *a, **k: goi.append(1))
    assert goi == []


def test_stdin_la_file_object_truyen_thang_khong_doc_vao_ram(tmp_path):
    goi = []

    def khoi(argv, **kw):
        goi.append(kw["stdin"])
        return khoi_chay(argv, **kw)
    (f := tmp_path / "vao").write_bytes(b"abc")
    with open(f, "rb") as vao:
        r = chay_gioi_han([PY, "-c", "import sys; print(sys.stdin.read().upper())"], kill=kill_cuc_bo, timeout=10,
                          capture_output=True, text=True, stdin=vao, khoi=khoi)
        assert goi == [vao] and not vao.closed                      # người gọi giữ và tự đóng bản sao của mình
    assert r.stdout == "ABC\n"


def test_input_va_stdin_loai_tru_truoc_khi_spawn(tmp_path):
    goi = []
    with pytest.raises(ValueError, match="loại trừ"):
        chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=1, input=b"BI-MAT-ENV", stdin=subprocess.DEVNULL,
                      khoi=lambda *a, **k: goi.append(1))
    assert goi == []


def test_stdin_ong_nguon_qua_han_thi_thu_hoi_khong_kem_du_lieu(tmp_path):
    r, w = os.pipe()
    os.write(w, b"BI-MAT-ENV")                                      # nguồn còn mở, không EOF: đích chờ mãi
    try:
        with pytest.raises(subprocess.TimeoutExpired) as e:
            chay_gioi_han([PY, "-c", "import sys; sys.stdin.read()"], kill=kill_cuc_bo, timeout=0.3, stdin=r)
        assert "BI-MAT-ENV" not in str(e.value) and e.value.output is None
    finally:
        os.close(r)
        os.close(w)


class _PopenTreo(PopenGia):
    stdin = stdout = stderr = None

    def communicate(self, input=None, timeout=None):
        time.sleep(timeout)
        raise subprocess.TimeoutExpired("x", timeout)
