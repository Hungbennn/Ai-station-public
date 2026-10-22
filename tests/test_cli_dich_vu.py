import os
import plistlib
import subprocess
from pathlib import Path

import pytest

from tram.chu import cai_dat
from tram.cli import main


def test_tram_api_chi_nghe_localhost(monkeypatch):
    import uvicorn
    goi = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: goi.update(kw, app=app))
    assert main(["api"]) == 0
    assert goi["host"] == "127.0.0.1" and goi["port"] == 7700 and goi["app"].title == "tram-api"
    assert goi["server_header"] is False                    # không lộ phiên bản server (spec 2 §4 mục 6)


def test_tram_api_khong_co_tuy_chon_host():
    with pytest.raises(SystemExit):
        main(["api", "--host", "0.0.0.0"])


def test_sao_luu_cli(tram_home_tam, capsys):
    from tram.su_kien.kho import mo_kho
    mo_kho().ghi("hr", "x", {})
    assert main(["chu", "sao-luu", "--giu", "3"]) == 0
    assert len(list((tram_home_tam / "sao-luu").glob("su-kien-*.db"))) == 1
    assert "Đã sao lưu" in capsys.readouterr().out


def test_bao_tin_chua_cau_hinh_thoat_0(capsys):
    assert main(["bao-tin", "--mot-lan"]) == 0 and "Chưa cấu hình" in capsys.readouterr().out


def test_ke_hoach_cai_dat_co_bon_dich_vu(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(cai_dat, "_canh_bao", lambda: [])
    kh = cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["api", "bao-tin", "sao-luu", "quet"])
    la = tmp_path / "Library/LaunchAgents"
    assert sorted(p.name for p in kh.tep if p.parent == la) == ["vn.tram.api.plist", "vn.tram.bao-tin.plist",
                                                                 "vn.tram.quet.plist", "vn.tram.sao-luu.plist"]
    api = plistlib.loads(kh.tep[la / "vn.tram.api.plist"])
    assert api["ProgramArguments"] == ["/u", "run", "--project", "/r", "tram", "api"]
    assert api["KeepAlive"] == {"SuccessfulExit": False} and api["RunAtLoad"] is True
    sl = plistlib.loads(kh.tep[la / "vn.tram.sao-luu.plist"])
    assert sl["StartCalendarInterval"] == {"Hour": 3, "Minute": 15}
    assert sl["ProgramArguments"][-3:] == ["tram", "chu", "sao-luu"]
    assert ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(la / "vn.tram.bao-tin.plist")] in kh.lenh
    assert "api.telegram.org" in cai_dat.in_ke_hoach(kh)


def test_canh_bao_telegram_cau_hinh_tailscale(monkeypatch):
    def chay_gia(lenh, **k):
        if lenh[0] == "security":
            return subprocess.CompletedProcess(lenh, 44, "", "")
        return subprocess.CompletedProcess(lenh, 0, "", "")

    monkeypatch.setattr(cai_dat.subprocess, "run", chay_gia)
    cb = "\n".join(cai_dat._canh_bao())
    assert "tram-telegram-bot-token" in cb and "cau-hinh.yaml" in cb and "tailscale serve" in cb
    assert f"launchctl kickstart -k gui/{os.getuid()}/vn.tram.bao-tin" in cb   # bao-tin thoát 0 → launchd không bật lại
