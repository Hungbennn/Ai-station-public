import plistlib
import re
from pathlib import Path

import pytest

from tram.chu import cai_dat
from tram.chu.cai_dat import KeHoach, in_ke_hoach, thuc_hien
from tram.chu.cai_dat_nho import lap_ke_hoach_nho, tao_token_nho


def test_ke_hoach_nho_liet_ke_du_va_dung_thu_tu(monkeypatch, tmp_path, tram_home_tam):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("tram.chu.cai_dat_nho.shutil.which", lambda ten: None)
    kh = lap_ke_hoach_nho(uv="/u", repo=Path("/r"))
    plist, bien_nhan = kh.tep                                          # bs-2bd.1.17: kèm biên nhận sở hữu
    assert plist == tmp_path / "Library/LaunchAgents/vn.tram.nho.plist"
    assert bien_nhan == tram_home_tam / "dich-vu/vn.tram.nho.json" and str(plist) in kh.tep[bien_nhan].decode()
    p = plistlib.loads(kh.tep[plist])
    assert p["ProgramArguments"] == ["/u", "run", "--project", "/r", "tram", "nho", "chay"]
    assert p["KeepAlive"] == {"SuccessfulExit": False} and p["StandardOutPath"].endswith("log/nho.log")
    lenh = [" ".join(c) for c in kh.lenh]
    assert lenh.index("brew install ollama") < lenh.index("ollama pull bge-m3") < \
        next(i for i, c in enumerate(lenh) if c.startswith("launchctl bootstrap"))
    van_ban = in_ke_hoach(kh)
    assert "CHƯA DUYỆT" in van_ban and "tram-nho-token" in van_ban and "lsof" in van_ban
    assert "Sẽ làm trước các lệnh:" in van_ban and "launchctl kickstart -k gui/" in van_ban


def test_da_co_ollama_thi_khong_brew(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("tram.chu.cai_dat_nho.shutil.which", lambda ten: "/opt/homebrew/bin/ollama")
    assert not any(c[0] == "brew" for c in lap_ke_hoach_nho(uv="/u", repo=Path("/r")).lenh)


def test_tao_token_qua_stdin_chi_khi_chua_co_va_khong_in(capsys):
    goi = []
    assert not tao_token_nho(co=lambda dv: True, chay=lambda *a, **k: goi.append(a))
    co = iter([False, True])                                     # chưa có → tạo → kiểm lại thấy có
    assert tao_token_nho(co=lambda dv: next(co), chay=lambda c, **k: goi.append((c, k)))
    c, k = goi[0]
    assert c == ["security", "-i"] and "-w" not in c                  # G13: token không nằm trong argv
    assert re.fullmatch(r"add-generic-password -s tram-nho-token -a tram -w [0-9a-f]{64}\n", k["input"])
    assert k["text"] is True and k["check"] is True and k["capture_output"] is True
    assert k["input"].split()[-1] not in capsys.readouterr().out


def test_tao_token_loi_lenh_con_thi_bao_loi():
    with pytest.raises(RuntimeError, match="tram-nho-token"):
        tao_token_nho(co=lambda dv: False, chay=lambda c, **k: None)


def test_thuc_hien_chay_buoc_truoc_lenh(tmp_path):
    thu_tu = []
    kh = KeHoach({}, [["launchctl", "bootstrap"]], [], buoc=[("token", lambda: thu_tu.append("token"))])
    thuc_hien(kh, chay=lambda c, check: thu_tu.append(c[0]))
    assert thu_tu == ["token", "launchctl"]


def test_cli_cai_dat_nho_dung_ke_hoach_nho(monkeypatch):
    from tram.cli import main
    goi = []
    monkeypatch.setattr("tram.chu.cai_dat_nho.lap_ke_hoach_nho", lambda **k: KeHoach({}, [["x"]], ["nho"]))
    monkeypatch.setattr(cai_dat, "lap_ke_hoach", lambda **k: KeHoach({}, [["y"]], ["quet"]))
    monkeypatch.setattr(cai_dat, "thuc_hien", lambda kh: goi.append(kh.canh_bao))
    assert main(["chu", "cai-dat", "--nho", "--dong-y"]) == 0
    assert main(["chu", "cai-dat", "--dich-vu", "quet", "--dong-y"]) == 0
    assert goi == [["nho"], ["quet"]]


def test_ke_hoach_nho_tao_ca_token_noi_bo_va_canh_bao_1b2(monkeypatch, tmp_path):
    from tram.api.noi_bo import KEYCHAIN_NOI_BO
    monkeypatch.setenv("HOME", str(tmp_path))
    kh = lap_ke_hoach_nho(uv="/u", repo=Path("/r"))
    (mo_ta_nho, ham_nho), (mo_ta_nb, ham_nb) = kh.buoc
    assert ham_nho is tao_token_nho and "tram-nho-token" in mo_ta_nho
    assert ham_nb.func is tao_token_nho and ham_nb.keywords == {"dich_vu": KEYCHAIN_NOI_BO}
    assert KEYCHAIN_NOI_BO in mo_ta_nb
    van_ban = in_ke_hoach(kh)
    assert "vn.tram.api" in van_ban and "tram chu dat-ma-dai-ca" in van_ban and "/nho" in van_ban


def test_tao_token_noi_bo_qua_stdin():
    goi, co = [], iter([False, True])
    assert tao_token_nho(dich_vu="tram-noi-bo-token", co=lambda dv: goi.append(dv) or next(co),
                         chay=lambda c, **k: goi.append(k["input"]))
    assert goi[0] == goi[2] == "tram-noi-bo-token"
    assert re.fullmatch(r"add-generic-password -s tram-noi-bo-token -a tram -w [0-9a-f]{64}\n", goi[1])
