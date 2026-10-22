"""Kho kiểm từ remote dự án (spec 4 §6.2 bước 1; S7) — remote là repo bare cục bộ, không mạng."""
import subprocess
from pathlib import Path

import pytest

from git_gia import git
from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.bo import kho_kiem_co_san
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.kho_kiem_tao import github_repo, in_ke_hoach, lap_ke_hoach, loi_remote, thuc_hien


def test_github_repo_va_loi_remote(tmp_path):
    assert github_repo("https://github.com/hung/hr-codex.git") == "hung/hr-codex"
    assert github_repo("git@github.com:hung/hr.codex") == "hung/hr.codex"
    assert github_repo("https://gitlab.com/hung/x.git") is None and github_repo(None) is None
    assert loi_remote("https://github.com/hung/x") is None and loi_remote(str(tmp_path)) is None
    assert loi_remote("http://github.com/hung/x") and loi_remote(None) and loi_remote(str(tmp_path / "khong"))


def test_tao_moi_roi_cap_nhat(tmp_path, tram_home_tam):
    k = dung_kho(tmp_path)
    da = DuAn("hr-codex", k.dev, None, {})
    kh = lap_ke_hoach(da)
    assert (kh.co_san, kh.dich, kh.remote) == (False, tram_home_tam / "kho-kiem" / "hr-codex", str(k.origin))
    assert "TẠO MỚI" in in_ke_hoach(kh) and "--no-checkout" in in_ke_hoach(kh)
    assert kho_kiem_co_san(da) is None and thuc_hien(kh, "main") == k.main
    assert kho_kiem_co_san(da) == kh.dich and not (kh.dich / "AGENTS.md").exists()      # không checkout file
    moi = k.day("main", {"src/tom_tat.py": "x = 9\n"}, tu=k.main)
    kh2 = lap_ke_hoach(da)
    assert kh2.co_san and "cập nhật" in in_ke_hoach(kh2) and thuc_hien(kh2, "main") == moi


def test_kho_co_san_tro_remote_khac_thi_tu_choi(tmp_path):
    k = dung_kho(tmp_path)
    da = DuAn("hr-codex", k.dev, None, {})
    thuc_hien(lap_ke_hoach(da), "main")
    khac = tmp_path / "khac.git"
    git(tmp_path, "clone", "-q", "--bare", str(k.origin), str(khac))
    git(k.dev, "remote", "set-url", "origin", str(khac))
    with pytest.raises(ValueError, match="khác remote"):
        lap_ke_hoach(da)


def test_fetch_qua_han_nem_timeout(tmp_path):
    k = dung_kho(tmp_path)
    with pytest.raises(subprocess.TimeoutExpired):
        fetch(k.kho, thoi_gian_cho=0.000001)
    fetch(k.kho)                                                        # mặc định vẫn chạy được
    assert Path(k.kho / ".git").is_dir()
