import plistlib
import subprocess
from pathlib import Path

import pytest

from tram.chu import cai_dat
from tram.chu.cai_dat import KeHoach, in_ke_hoach, lap_ke_hoach, thuc_hien
from tram.chu.trang_thai import trang_thai
from tram.chu.launchd import NHAN_QUET, tao_plist
from tram.su_kien.kho import KhoSuKien


@pytest.fixture(autouse=True)
def khong_cham_he_thong(monkeypatch):
    """Chặn mọi lời gọi hệ thống thật (launchctl, security, pmset) trong file test này."""
    def cam(*a, **k):
        raise AssertionError(f"test gọi subprocess.run thật: {a}")
    monkeypatch.setattr(subprocess, "run", cam)


def test_plist_dung_noi_dung():
    p = plistlib.loads(tao_plist(uv="/opt/homebrew/bin/uv", repo=Path("/r"), log=Path("/l/q.log")))
    assert p["Label"] == NHAN_QUET
    assert p["ProgramArguments"] == ["/opt/homebrew/bin/uv", "run", "--project", "/r", "tram", "quet", "--ghi"]
    assert p["StartInterval"] == 120 and p["RunAtLoad"] is True
    assert p["StandardOutPath"] == "/l/q.log" and p["WorkingDirectory"] == "/r"


def test_plist_path_co_local_bin_truoc_homebrew(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    p = plistlib.loads(tao_plist(uv="/u", repo=Path("/r"), log=Path("/l/q.log")))
    path = p["EnvironmentVariables"]["PATH"].split(":")
    local_bin = str(tmp_path / ".local/bin")
    assert local_bin in path and "/opt/homebrew/bin" in path
    assert path.index(local_bin) < path.index("/opt/homebrew/bin")


def test_ke_hoach_liet_ke_moi_thay_doi(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(cai_dat, "_canh_bao", lambda: ["Cảnh báo giả"])
    kh = lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["quet"])
    van_ban = in_ke_hoach(kh)
    assert "LaunchAgents/vn.tram.quet.plist" in van_ban
    assert "launchctl" in van_ban and "Cảnh báo" in van_ban and "Cảnh báo giả" in van_ban
    assert isinstance(kh.canh_bao, list)
    assert all(str(p).startswith(str(tmp_path)) for p in kh.tep)


def test_canh_bao_tu_ket_qua_gia(monkeypatch):
    def chay_gia(lenh, **k):
        if lenh[0] == "security":
            return subprocess.CompletedProcess(lenh, 44, "", "")
        return subprocess.CompletedProcess(lenh, 0, " sleep                1\n disksleep 10\n", "")
    monkeypatch.setattr(cai_dat.subprocess, "run", chay_gia)
    monkeypatch.setattr(cai_dat.shutil, "which", lambda ten: None)
    monkeypatch.setattr(cai_dat, "Path", lambda *a: Path("/khong-co-dau"))
    cb = "\n".join(cai_dat._canh_bao())
    assert "Tailscale" in cb and "Keychain" in cb and "ngủ" in cb and "`bd`" in cb


def test_thuc_hien_ghi_tep_va_chay_lenh(tmp_path):
    goi = []
    tep = tmp_path / "a" / "x.plist"
    thuc_hien(KeHoach({tep: b"abc"}, [["echo", "1"]], []), chay=lambda c, check: goi.append(c))
    assert tep.read_bytes() == b"abc" and goi == [["echo", "1"]]


def test_trang_thai(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "quet.xong", {"da_cham": 3, "loi": 0})
    s = trang_thai(k)
    assert "estop: tắt" in s and "hr" in s


def test_trang_thai_bo_du_an_noi_bo(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("_tram", "estop.bat", {"ly_do": "thử"}, tac_nhan="dai-ca")
    k.ghi("hr", "quet.xong", {"da_cham": 1, "loi": 0})
    s = trang_thai(k)
    assert "hr" in s and "_tram" not in s and "estop:" in s


def _kh_gia(**k):
    return KeHoach({}, [["launchctl", "bootstrap"]], [])


def test_cli_cai_dat_dong_y(monkeypatch):
    from tram.cli import main
    goi = []
    monkeypatch.setattr(cai_dat, "lap_ke_hoach", _kh_gia)
    monkeypatch.setattr(cai_dat, "thuc_hien", lambda kh: goi.append(kh))
    assert main(["chu", "cai-dat", "--dich-vu", "api", "--dong-y"]) == 0 and len(goi) == 1


def test_cli_cai_dat_khong_dong_y(monkeypatch):
    from tram.cli import main
    goi = []
    monkeypatch.setattr(cai_dat, "lap_ke_hoach", _kh_gia)
    monkeypatch.setattr(cai_dat, "thuc_hien", lambda kh: goi.append(kh))
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    assert main(["chu", "cai-dat", "--dich-vu", "api"]) == 1 and goi == []


def test_cli_trang_thai(capsys):
    from tram.cli import main
    assert main(["chu", "trang-thai"]) == 0
    assert "estop: tắt" in capsys.readouterr().out
