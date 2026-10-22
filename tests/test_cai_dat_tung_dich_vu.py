"""bs-2bd.1.23: `tram chu cai-dat` chỉ cài dịch vụ Đại ca chọn; không mặc định; `vn.tram.quet --ghi` chỉ khi chọn rõ,
kèm hậu quả từng dự án; không đọc được dự án → không lập kế hoạch, không ghi, không spawn; mỗi lệnh hệ thống có hạn.
Không launchctl thật: chỉ đọc kế hoạch, bộ chạy giả."""
import hashlib
import json
import os
import plistlib
import subprocess
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
import yaml

from tram.chu import cai_dat
from tram.chu.dich_vu_tram import DICH_VU_TRAM, HAN_LENH_GIAY, LoiCaiDat, canh_bao_quet

CANH_BAO_THAT = cai_dat._canh_bao                     # giữ bản thật trước khi fixture thay bằng bản giả


@pytest.fixture(autouse=True)
def khong_cham_he_thong(monkeypatch, tmp_path):
    def cam(*a, **k):
        raise AssertionError(f"test gọi subprocess.run thật: {a}")
    monkeypatch.setattr(subprocess, "run", cam)
    monkeypatch.setattr(cai_dat, "_canh_bao", lambda: ["chung"])
    monkeypatch.setenv("HOME", str(tmp_path))


def test_chi_cai_dich_vu_da_chon_moi_lenh_co_han(tmp_path, tram_home_tam):
    kh = cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["api", "bao-tin"])
    assert sorted(p.name for p in kh.tep if p.suffix == ".plist") == ["vn.tram.api.plist", "vn.tram.bao-tin.plist"]
    la = tmp_path / "Library/LaunchAgents"
    bn = json.loads(kh.tep[tram_home_tam / "dich-vu/vn.tram.api.json"])          # biên nhận sở hữu cho go-dich-vu
    assert bn == {"nhan": "vn.tram.api", "plist": str(la / "vn.tram.api.plist"),
                  "sha256": hashlib.sha256(kh.tep[la / "vn.tram.api.plist"]).hexdigest()}
    nap = [c for c in kh.lenh if c[:2] == ["launchctl", "bootstrap"]]
    assert [Path(c[3]).stem for c in nap] == ["vn.tram.api", "vn.tram.bao-tin"]
    assert not any("quet" in " ".join(c) for c in kh.lenh) and kh.canh_bao == ["chung"]
    api = plistlib.loads(kh.tep[tmp_path / "Library/LaunchAgents/vn.tram.api.plist"])
    assert api["ProgramArguments"][-2:] == ["tram", "api"] and kh.han_lenh == HAN_LENH_GIAY
    goi = []
    cai_dat.thuc_hien(kh, chay=lambda c, check, **k: goi.append(k))
    assert goi and all(k == {"timeout": HAN_LENH_GIAY} for k in goi)


@pytest.mark.parametrize("sai", [[], None, ["nho"], ["api", "la"]])
def test_khong_chon_hay_ten_la_thi_tu_choi(sai):
    with pytest.raises(ValueError, match="dịch vụ"):
        cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=sai)


def test_quet_ghi_chi_khi_chon_ro_va_in_tung_du_an(monkeypatch):
    monkeypatch.setattr("tram.chu.dich_vu_tram._du_an_bat_ghi", lambda: (["hr-codex"], ["ben-station"]))
    kh = cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["quet", "quet"])
    (p,) = (p for p in kh.tep if p.suffix == ".plist")
    assert plistlib.loads(kh.tep[p])["ProgramArguments"][-2:] == ["quet", "--ghi"]
    assert any("GHI nhãn cột" in c and "hr-codex" in c and "chỉ đọc: ben-station" in c for c in kh.canh_bao)
    assert "chưa dự án nào" in canh_bao_quet(du_an_ghi=lambda: ([], []))[0]


@pytest.mark.parametrize("loi", [ValueError("bat_ghi sai kiểu"), OSError("không đọc được"),
                                 yaml.YAMLError("yaml hỏng"), AttributeError("yaml không phải dict")])
def test_khong_doc_duoc_du_an_thi_khong_lap_ke_hoach_khong_ghi_khong_spawn(monkeypatch, tmp_path, capsys, loi):
    def hong():
        raise loi
    monkeypatch.setattr("tram.chu.dich_vu_tram._du_an_bat_ghi", hong)
    with pytest.raises(LoiCaiDat, match="KHÔNG cài vn.tram.quet"):
        cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["api", "quet"])
    from tram.cli import main
    thuc = []
    monkeypatch.setattr(cai_dat, "thuc_hien", lambda kh: thuc.append(kh))
    assert main(["chu", "cai-dat", "--dich-vu", "api", "--dich-vu", "quet", "--dong-y"]) == 2
    assert thuc == [] and not (tmp_path / "Library").exists() and "KHÔNG cài" in capsys.readouterr().out


def test_lenh_qua_han_thi_dung_lenh_sau_khong_chay(tmp_path):
    kh = cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["api", "bao-tin"])
    kh.buoc = []
    goi = []

    def chay(c, check, timeout):
        goi.append(c[:2])
        if c[:2] == ["launchctl", "bootstrap"]:
            raise subprocess.TimeoutExpired(c, timeout)
    with pytest.raises(subprocess.TimeoutExpired):
        cai_dat.thuc_hien(kh, chay=chay)
    assert goi == [["mkdir", "-p"], ["launchctl", "bootout"], ["launchctl", "bootstrap"]]   # bao-tin không chạy


def test_cli_lenh_qua_han_thoat_3_khong_chep_argv(monkeypatch, capsys):
    from tram.cli import main

    def qua_han(kh):
        raise subprocess.TimeoutExpired(["launchctl", "bootstrap", "gui/501", "/bi/mat"], 30)
    monkeypatch.setattr(cai_dat, "thuc_hien", qua_han)
    assert main(["chu", "cai-dat", "--dich-vu", "api", "--dong-y"]) == 3
    out = capsys.readouterr().out
    assert "quá 30 giây" in out and "/bi/mat" not in out


def test_pmset_treo_khong_treo_ke_hoach(monkeypatch):
    goi = []

    def run(argv, **k):
        goi.append((argv[0], k.get("timeout")))
        raise subprocess.TimeoutExpired(argv, k["timeout"])
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(cai_dat, "_thieu_keychain", lambda dv: False)
    assert any("pmset" in c for c in CANH_BAO_THAT()) and goi == [("pmset", 10)]


def test_ke_hoach_siet_quyen_truoc_khi_nap(tram_home_tam):
    kh = cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"), dich_vu=["sao-luu"])
    (mo_ta, ham), = kh.buoc
    assert "700/600" in mo_ta
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    os.chmod(tram_home_tam, 0o755)
    ham()
    assert os.stat(tram_home_tam).st_mode & 0o777 == 0o700


def test_cli_khong_chon_thi_khong_lam_gi(monkeypatch, capsys):
    from tram.cli import main
    goi = []
    monkeypatch.setattr(cai_dat, "thuc_hien", lambda kh: goi.append(kh))
    assert main(["chu", "cai-dat", "--dong-y"]) == 2 and goi == []
    assert "|".join(DICH_VU_TRAM) in capsys.readouterr().out
    assert main(["chu", "cai-dat", "--nho", "--dich-vu", "api", "--dong-y"]) == 2 and goi == []
    assert main(["chu", "cai-dat", "--dich-vu", "api", "--dich-vu", "sao-luu", "--dong-y"]) == 0
    assert sorted(p.name for p in goi[0].tep) == ["vn.tram.api.json", "vn.tram.api.plist", "vn.tram.sao-luu.json",
                                                  "vn.tram.sao-luu.plist"]


def test_nho_moi_lenh_co_han_rieng_theo_loai(monkeypatch, tmp_path):
    """R2-09: nhánh `--nho` cũng có hạn từng lệnh — tải mô hình/brew hạn dài riêng, launchctl/mkdir 30 giây."""
    from tram.chu.cai_dat_nho import HAN_NHO, lap_ke_hoach_nho
    monkeypatch.setattr("tram.chu.cai_dat_nho.shutil.which", lambda ten: None)
    kh = lap_ke_hoach_nho(uv="/u", repo=Path("/r"))
    kh.buoc, goi = [], []
    cai_dat.thuc_hien(kh, chay=lambda c, check, **k: goi.append((tuple(c[:2]), k.get("timeout"))))
    assert dict(goi) == {("mkdir", "-p"): HAN_LENH_GIAY, **HAN_NHO, ("launchctl", "bootout"): HAN_LENH_GIAY,
                         ("launchctl", "bootstrap"): HAN_LENH_GIAY}
    assert HAN_NHO[("ollama", "pull")] > HAN_LENH_GIAY and len(goi) == 6


def test_tao_token_co_han_qua_han_thi_dung_khong_tao_lai():
    from tram.chu.cai_dat_nho import tao_token_nho
    from tram.keychain import HAN_GIAY
    goi, kiem = [], []

    def treo(c, **k):
        goi.append(k.get("timeout"))
        raise subprocess.TimeoutExpired(c, k["timeout"])
    with pytest.raises(subprocess.TimeoutExpired):
        tao_token_nho(co=lambda dv: kiem.append(dv) or False, chay=treo)
    assert goi == [HAN_GIAY] and len(kiem) == 1                          # không thử tạo lại, không kiểm lại


@pytest.mark.parametrize("noi_treo", ["token", "ollama", "launchctl"])
def test_cli_nho_qua_han_dung_lenh_sau_khong_bao_da_cai(monkeypatch, capsys, noi_treo):
    from tram.cli import main
    monkeypatch.setattr("tram.chu.cai_dat_nho.shutil.which", lambda ten: "/x/ollama")
    da_tao, goi = set(), []

    def run(argv, **k):
        goi.append(tuple(argv[:2]))
        assert k.get("timeout"), argv                                    # mọi lời gọi ngoài đều có hạn
        if argv[:2] == ["security", "find-generic-password"]:
            return NS(returncode=0 if argv[3] in da_tao else 44, stdout="")
        if (noi_treo, argv[0]) in (("token", "security"), ("ollama", "ollama")) or \
                (noi_treo, argv[:2]) == ("launchctl", ["launchctl", "bootstrap"]):
            raise subprocess.TimeoutExpired(argv, k["timeout"])
        if argv[:2] == ["security", "-i"]:
            da_tao.add(k["input"].split()[2])
        return NS(returncode=0, stdout="")
    that = cai_dat.thuc_hien
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(cai_dat, "thuc_hien", lambda kh: that(kh, chay=run))
    assert main(["chu", "cai-dat", "--nho", "--dong-y"]) == 3
    out = capsys.readouterr().out
    assert "quá" in out and "Đã cài" not in out
    sau = goi[goi.index(("security", "-i") if noi_treo == "token" else
                        ("ollama", "pull") if noi_treo == "ollama" else ("launchctl", "bootstrap")) + 1:]
    assert sau == []                                                     # lệnh/bước sau không chạy
