import os
import sys
import time

import pytest

from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem

PY = sys.executable


def _chay(tmp_path, argv, **kw):
    kw.setdefault("thoi_gian_cho", 20)
    return chay_mot_lenh("lệnh x", argv, cwd=tmp_path, env=moi_truong_kiem(os.environ),
                         log=tmp_path / "log/kiem/g-1-1.log", boc=lambda a: a, **kw)


def _da_chet(pid: int, trong: float = 3.0) -> bool:
    het = time.monotonic() + trong
    while time.monotonic() < het:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


def test_pass_tom_tat_3_dong_cuoi_va_digest(tmp_path):
    import hashlib
    kq = _chay(tmp_path, [PY, "-c", "print('a\\nb\\n\\nc\\nd')"])
    log = (tmp_path / "log/kiem/g-1-1.log").read_bytes()
    assert kq.ket_qua == "pass" and kq.ma_thoat == 0 and kq.tom_tat == "b\nc\nd"
    assert kq.digest_log == "sha256:" + hashlib.sha256(log).hexdigest()
    assert kq.sang_lenh_kiem() == {"lenh": "lệnh x", "ket_qua": "pass", "tom_tat": "b\nc\nd",
                                   "digest_log": kq.digest_log}


def test_ma_thoat_khac_0_la_fail(tmp_path):
    kq = _chay(tmp_path, [PY, "-c", "import sys; print('2 failed'); sys.exit(3)"])
    assert kq.ket_qua == "fail" and kq.ma_thoat == 3 and kq.tom_tat == "2 failed"


def test_khong_khop_thi_khong_chay(tmp_path):
    kq = _chay(tmp_path, None)
    assert kq.ket_qua == "fail" and kq.ma_thoat is None and "không khớp" in kq.tom_tat


def test_loi_khoi_chay_la_fail(tmp_path):
    kq = _chay(tmp_path, [str(tmp_path / "khong-co-chuong-trinh")])
    assert kq.ket_qua == "fail" and "lỗi khởi chạy" in kq.tom_tat


def test_qua_han_kill_ca_nhom_ke_ca_con_bo_qua_sigterm(tmp_path):
    ma = ("import signal, subprocess, sys, time\n"
          "c = subprocess.Popen([sys.executable, '-c', 'import signal, time; "
          "signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'])\n"
          "open('con.pid', 'w').write(str(c.pid)); print('bắt đầu', flush=True); time.sleep(60)\n")
    bat_dau = time.monotonic()
    kq = _chay(tmp_path, [PY, "-c", ma], thoi_gian_cho=1.0, cho_kill=0.5)
    assert kq.ket_qua == "fail" and kq.het_gio and time.monotonic() - bat_dau < 10
    assert "quá hạn" in kq.tom_tat
    assert _da_chet(int((tmp_path / "con.pid").read_text()))


def test_lenh_xong_nhung_con_giu_file_van_bi_kill(tmp_path):
    ma = ("import subprocess, sys\n"
          "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
          "open('con.pid', 'w').write(str(c.pid)); print('xong')\n")
    kq = _chay(tmp_path, [PY, "-c", ma])
    assert kq.ket_qua == "pass" and _da_chet(int((tmp_path / "con.pid").read_text()))


def test_moi_truong_toi_thieu_va_boc_principal(tmp_path):
    env = moi_truong_kiem({"PATH": "/usr/bin", "HOME": "/h", "TRAM_THO_TOKEN": "bi-mat", "AWS_X": "y"},
                          {"X": "1"})
    from tram.kiem.toolchain import bien_kiem
    assert env == {**bien_kiem("/h"), "HOME": "/h", "APP_ENV": "testing", "GIT_CONFIG_COUNT": "1",
                   "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": "/dev/null", "X": "1"}
    goi = []
    kq = chay_mot_lenh("l", [PY, "-c", "import os; print(os.environ.get('APP_ENV'))"], cwd=tmp_path,
                       env=moi_truong_kiem(os.environ), log=tmp_path / "l.log", thoi_gian_cho=20,
                       boc=lambda a: goi.append(a) or a)
    assert goi and kq.tom_tat == "testing"
    with pytest.raises(TypeError):
        chay_mot_lenh("l", ["true"], cwd=tmp_path, env={}, log=tmp_path / "x.log", thoi_gian_cho=1)
