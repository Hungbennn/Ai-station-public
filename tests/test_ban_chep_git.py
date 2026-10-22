"""D40 (b): bản chép kiểm là repo git MỘT commit do `tram-kiem` tự dựng sau `tar -x` — cây đúng cây commit gốc, không
lịch sử/remote của kho thật; hook, filter, template ở cấu hình global/system/biến môi trường không chạy; git lỗi thì
fail-closed như tar. `git` THẬT dưới user đang test (`boc` đồng nhất thay `sudo -u tram-kiem`) trong `tmp_path`."""
import os
import subprocess

import pytest

from git_gia import CO, MOI_TRUONG, git
from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import ban_chep, chay, m  # noqa: F401 — fixture `m` dùng chung
from tram.giao_viec.ban_chep import LoiBanChep, chep_ban
from tram.giao_viec.git_kiem import fetch

RONG = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"           # cây rỗng của git


def nhap(kho, *a: str, vao: str) -> str:
    return subprocess.run(["git", *CO, "-C", str(kho), *a], input=vao, capture_output=True, text=True,
                          env=MOI_TRUONG, check=True).stdout.strip()


def chep(tmp_path, k, sha):
    fetch(k.kho)
    wt = tmp_path / "kiem" / "g-1-ab"
    chep_ban(k.kho, sha, wt, boc=lambda a: a)
    return wt


def test_ban_chep_la_repo_mot_commit_cay_dung_commit_goc_khong_lich_su(tmp_path):
    k = dung_kho(tmp_path)
    k.day("tram/hr-1", {"bo-qua.log": "y", "src/a.py": "x = 1\n"}, tu=k.main)
    sha = k.day("tram/hr-1", {".gitignore": "*.log\n"})               # bo-qua.log vẫn được theo dõi dù bị ignore
    wt = chep(tmp_path, k, sha)
    assert (wt / ".git").is_dir() and git(wt, "rev-list", "--all", "--count") == "1"
    assert git(wt, "rev-parse", "HEAD^{tree}") == git(k.kho, "rev-parse", f"{sha}^{{tree}}")
    assert git(wt, "log", "-1", "--format=%s %an") == "kiem tram-kiem" and git(wt, "status", "--porcelain") == ""
    assert git(wt, "remote") == "" and not (wt / ".git" / "objects" / "info" / "alternates").exists()
    assert all(subprocess.run(["git", "-C", str(wt), "cat-file", "-e", f"{c}^{{commit}}"], env=MOI_TRUONG,
                              capture_output=True).returncode != 0 for c in (sha, k.main))


def test_hook_filter_template_cua_cau_hinh_ngoai_khong_chay(tmp_path, monkeypatch):
    dau, mau, cfg = tmp_path / "DA_CHAY", tmp_path / "mau", tmp_path / "gitconfig"
    moc = f"#!/bin/sh\ntouch {dau}\n"
    k = dung_kho(tmp_path)
    for p in (k.dev / ".husky" / "pre-commit", k.dev / ".husky" / "post-commit", mau / "hooks" / "post-commit"):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(moc)
        p.chmod(0o755)
    sha = k.day("tram/hr-1", {".gitattributes": "* filter=x\n*.bin filter=lfs\n", "a.bin": "z", "a.txt": "a"},
                tu=k.main)
    cfg.write_text(f'[core]\n\thooksPath = .husky\n[init]\n\ttemplateDir = {mau}\n'
                   f'[filter "lfs"]\n\tclean = touch {dau}; cat\n\tsmudge = cat\n\trequired = true\n')
    for bien, gt in {"GIT_CONFIG_GLOBAL": cfg, "GIT_CONFIG_SYSTEM": cfg, "GIT_TEMPLATE_DIR": mau, "GIT_CONFIG_COUNT": 2,
                     "GIT_CONFIG_KEY_0": "filter.x.clean", "GIT_CONFIG_VALUE_0": f"touch {dau}; cat",
                     "GIT_CONFIG_KEY_1": "filter.x.smudge", "GIT_CONFIG_VALUE_1": "cat"}.items():
        monkeypatch.setenv(bien, str(gt))                    # cấu hình "của tram-kiem" mà trạm không kiểm soát
    wt = chep(tmp_path, k, sha)
    assert (wt / ".git").is_dir() and not dau.exists() and not (wt / ".git" / "hooks").exists()
    assert git(wt, "rev-parse", "HEAD^{tree}") == git(k.kho, "rev-parse", f"{sha}^{{tree}}")


@pytest.mark.parametrize("buoc", ["init", "add", "commit"])
def test_git_loi_thi_fail_closed_nhu_tar(m, buoc):
    boc = lambda a: ["/usr/bin/false"] if buoc in a else a
    with pytest.raises(LoiBanChep, match=f"git {buoc}"):
        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, boc=boc)
    assert not (m[2] / "DA_CHAY").exists() and ban_chep(m) == []


def test_ban_chep_rong_van_la_repo_mot_commit_cay_rong(tmp_path):
    k = dung_kho(tmp_path)
    wt = chep(tmp_path, k, git(k.kho, "commit-tree", RONG, "-m", "rong"))
    assert os.listdir(wt) == [".git"] and git(wt, "rev-parse", "HEAD^{tree}") == RONG
    assert git(wt, "rev-list", "--all", "--count") == "1"


def test_commit_chua_git_thi_khong_dung_repo_len_do(tmp_path):
    k = dung_kho(tmp_path)
    b = nhap(k.kho, "hash-object", "-w", "--stdin", vao=f"[core]\n\tfsmonitor = touch {tmp_path}/DA_CHAY\n")
    t = nhap(k.kho, "mktree", vao=f"100644 blob {b}\tconfig\n")
    t = nhap(k.kho, "mktree", vao=f"040000 tree {t}\t.git\n100644 blob {b}\ta.txt\n")     # git không tự tạo được
    with pytest.raises(LoiBanChep, match="git archive"):
        chep(tmp_path, k, git(k.kho, "commit-tree", t, "-m", "x"))
    assert not (tmp_path / "kiem" / "g-1-ab" / ".git").exists() and not (tmp_path / "DA_CHAY").exists()
