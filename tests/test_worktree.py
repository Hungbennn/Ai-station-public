from datetime import datetime, timezone

import pytest

from git_gia import git, ghi, tao_repo
from tram.tho.worktree import chuan_bi_worktree, duong_dan_worktree

LUC = datetime(2026, 10, 13, 3, 4, 5, tzinfo=timezone.utc)


@pytest.fixture
def kho(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    nguon = tao_repo(tmp_path / "nguon")
    ghi(nguon, {"a.txt": "1"})
    origin = tmp_path / "origin.git"
    git(tmp_path, "clone", "-q", "--bare", str(nguon), str(origin))
    k = tmp_path / "kho"
    git(tmp_path, "clone", "-q", str(origin), str(k))
    (k / ".git/hooks/post-checkout").write_text("#!/bin/sh\ntouch HOOK_DA_CHAY\n")
    (k / ".git/hooks/post-checkout").chmod(0o755)
    return k, nguon, origin


def _chuan_bi(k, wt, cha, luot=1):
    return chuan_bi_worktree(k, wt, nhanh="tram/hr-1", cha=cha, bead_id="hr-1", luot=luot, bay_gio=LUC)


def test_tao_moi_o_cha_tren_nhanh_tram_hook_tat_va_tram_bi_loai(kho, tmp_path):
    k, nguon, _ = kho
    cha = git(k, "rev-parse", "HEAD")
    wt = tmp_path / "wt/hr/hr-1"
    kq = _chuan_bi(k, wt, cha[:7])
    assert kq.nhanh_rac is None and git(wt, "rev-parse", "HEAD") == cha
    assert git(wt, "rev-parse", "--abbrev-ref", "HEAD") == "tram/hr-1"
    assert not (k / "HOOK_DA_CHAY").exists() and not (wt / "HOOK_DA_CHAY").exists()
    (wt / ".tram/goi.md").write_text("gói")
    assert git(wt, "status", "--porcelain") == ""


def test_co_thay_doi_thi_commit_rac_roi_ve_cha(kho, tmp_path):
    k, _, _ = kho
    cha = git(k, "rev-parse", "HEAD")
    wt = tmp_path / "wt"
    _chuan_bi(k, wt, cha)
    (wt / "a.txt").write_text("sửa dở")
    (wt / "moi.txt").write_text("mới")
    kq = _chuan_bi(k, wt, cha, luot=2)
    assert kq.nhanh_rac == "rac/hr-1-20261013T030405Z"
    assert git(wt, "log", "-1", "--format=%s", kq.nhanh_rac) == "wip: rác lượt trước"
    assert git(wt, "show", f"{kq.nhanh_rac}:a.txt") == "sửa dở"
    assert git(wt, "rev-parse", "HEAD") == cha and git(wt, "status", "--porcelain") == ""


def test_head_khac_cha_khong_phai_to_tien_thi_giu_rac(kho, tmp_path):
    k, _, _ = kho
    cha = git(k, "rev-parse", "HEAD")
    wt = tmp_path / "wt"
    _chuan_bi(k, wt, cha)
    lam = ghi(wt, {"b.txt": "agent"}, "agent commit")
    kq = _chuan_bi(k, wt, cha, luot=2)
    assert git(wt, "rev-parse", kq.nhanh_rac) == lam and git(wt, "rev-parse", "HEAD") == cha


def test_head_la_to_tien_cua_cha_moi_thi_tien_len_khong_rac(kho, tmp_path):
    k, nguon, origin = kho
    cha1 = git(k, "rev-parse", "HEAD")
    wt = tmp_path / "wt"
    _chuan_bi(k, wt, cha1)
    cha2 = ghi(nguon, {"c.txt": "2"}, "trạm công bố")
    git(nguon, "push", "-q", str(origin), "HEAD:main")
    kq = _chuan_bi(k, wt, cha2, luot=2)          # cha2 chỉ có sau fetch
    assert kq.nhanh_rac is None and git(wt, "rev-parse", "HEAD") == cha2


def test_doi_luot_xoa_tien_do_va_goi(kho, tmp_path):
    k, _, _ = kho
    cha = git(k, "rev-parse", "HEAD")
    wt = tmp_path / "wt"
    _chuan_bi(k, wt, cha, luot=3)
    for ten in ("tien-do.md", "goi.md", "khac.md"):
        (wt / ".tram" / ten).write_text("x")
    _chuan_bi(k, wt, cha, luot=3)
    assert (wt / ".tram/tien-do.md").exists()
    _chuan_bi(k, wt, cha, luot=4)
    assert not (wt / ".tram/tien-do.md").exists() and not (wt / ".tram/goi.md").exists()
    assert (wt / ".tram/khac.md").exists() and (wt / ".tram/luot").read_text() == "4\n"


def test_duong_dan_worktree():
    from pathlib import Path
    assert duong_dan_worktree(Path("/w"), "hr-codex", "tram/hr-6xe1") == Path("/w/hr-codex/hr-6xe1")
    assert duong_dan_worktree(Path("/w"), "hr", "tram/spec-hr-1") == Path("/w/hr/spec-hr-1")
    for nhanh, du_an in (("main", "hr"), ("tram/../x", "hr"), ("tram/", "hr"), ("feature/x", "hr"),
                         ("tram/a", "../hr"), ("tram/-x", "hr")):
        with pytest.raises(ValueError):
            duong_dan_worktree(Path("/w"), du_an, nhanh)
