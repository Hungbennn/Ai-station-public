"""V2-4 (dot7-Q03) + B01 (vòng 1): chứng cứ TỪNG probe — thiếu/trùng/hỏng dấu là chưa chứng minh, mã ≠ 0 không tự là
"bị chặn"; lý do chỉ là mã HỮU HẠN do bộ phân loại sinh, byte stdout/stderr của lệnh không bao giờ ra log/kết quả.
Khối shell chỉ chạy lệnh GIẢ (`exit N`, `echo`) bằng `/bin/sh` của user test trong tmp_path — không lệnh lịch nào."""
import subprocess

import pytest

from tram.giao_viec.chung_cu_probe import LY_DO, boc_probe, doc_probe, ly_do, muc_lich


@pytest.mark.parametrize("s", ["kich-ban-bat-dau\n", "probe:cron:bat-dau\n",
    "probe:cron:ket:126\n", "probe:cron:bat-dau\nprobe:cron:ket:x\n",
    "probe:cron:bat-dau\nprobe:cron:ket:1\nprobe:cron:ket:1\n",
    "probe:cron:ket:1\nprobe:cron:bat-dau\n", "probe:cron:bat-dau\nprobe:cron:ket:256\n",
    "probe:cron:bat-dau\nprobe:cron:ket:-1\n", "probe:cron:bat-dau\nprobe:cron:ket:1 \n"])
def test_thieu_hong_trung_khong_phai_bi_chan(s):
    assert doc_probe(s, "cron") is None
    assert muc_lich(s, "cron")[0] is False


def test_co_ma_nhung_khong_tu_ket_luan_seatbelt():
    assert doc_probe("probe:cron:bat-dau\nprobe:cron:ket:126\n", "cron") == 126
    assert doc_probe("probe:cron:bat-dau\nprobe:cron:ket:0\n", "cron") == 0
    assert muc_lich("probe:at:bat-dau\nly-do:at:eperm\nprobe:at:ket:126\n", "at") == (
        None, "lệnh thất bại (mã 126, lý do eperm — Operation not permitted) — chờ biên bản OS + đối chứng dương ở G4")
    assert muc_lich("probe:at:bat-dau\nprobe:at:ket:0\n", "at") == (False, "CÀI ĐƯỢC — hồ sơ không chặn")


@pytest.mark.parametrize("dong", ["ly-do:at:Operation not permitted BIMAT\n", "ly-do:at:eperm\nly-do:at:eperm\n", "",
                                  "ly-do:at:eperm BIMAT\n", "ly-do:at:\n"])
def test_dong_ly_do_la_hay_trung_thanh_khong_ro_khong_chep(dong):
    log = f"probe:at:bat-dau\n{dong}probe:at:ket:1\n"
    assert ly_do(log, "at") == "khong-ro" and "BIMAT" not in muc_lich(log, "at")[1]


def _chay(tmp_path, kb: str, tmpdir=True) -> str:
    env = {"PATH": "/usr/bin:/bin", **({"TMPDIR": str(tmp_path)} if tmpdir else {})}
    return subprocess.run(["/bin/sh", "-c", kb + "\nwait\n"], capture_output=True, text=True, env=env, timeout=10,
                          cwd=tmp_path).stdout


def test_khoi_probe_khong_chep_stdout_stderr_tho(tmp_path):
    log = _chay(tmp_path, boc_probe("cron", "echo BIMAT_OUT; echo BIMAT_ERR >&2; echo probe:cron:ket:0 >&2; exit 7"))
    assert doc_probe(log, "cron") == 7                          # đầu ra của lệnh không giả được dòng dấu
    assert "BIMAT" not in log and ly_do(log, "cron") == "khac" and "BIMAT" not in muc_lich(log, "cron")[1]
    assert not (tmp_path / "probe-cron").exists()               # tệp đầu ra thô bị xoá ngay trong khối
    assert doc_probe(_chay(tmp_path, boc_probe("at", "true")), "at") == 0


@pytest.mark.parametrize("lenh, ma", [("echo 'crontab: tmp: Operation not permitted' >&2; exit 1", "eperm"),
                                      ("echo 'at: Permission denied' >&2; exit 1", "eacces"),
                                      ("/khong/co/lenh-nay", "khong-thay"), ("exit 1", "trong"),
                                      ("echo 'Permission denied; Operation not permitted'; exit 1", "eperm")])
def test_phan_loai_ly_do_huu_han(tmp_path, lenh, ma):
    log = _chay(tmp_path, boc_probe("at", lenh))
    assert ly_do(log, "at") == ma and ma in LY_DO and doc_probe(log, "at") != 0


def test_khong_co_tmpdir_thi_khong_co_ket(tmp_path):
    log = _chay(tmp_path, boc_probe("submit", "exit 1"), tmpdir=False)
    assert "probe:submit:bat-dau" in log and doc_probe(log, "submit") is None


@pytest.mark.parametrize("ten", ["", "Cron", "cr on", "cron;rm", "a" * 17])
def test_ten_nguon_sai_dang(ten):
    with pytest.raises(ValueError):
        boc_probe(ten, "true")
