"""Git chuẩn bị/dọn deploy: tất cả lời gọi có hạn và thu hồi nhóm P1, không lưu output."""
import os
import shutil
from pathlib import Path

from tram.deploy.lenh import HAN
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import kill_cuc_bo


def _git(repo, *args, check=True):
    return chay_gioi_han(["git", "-c", "core.hooksPath=/dev/null", "-C", str(repo), *args],
                         kill=kill_cuc_bo, timeout=HAN["git"], capture_output=True, check=check,
                         env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


def sha_cua(repo, ref):
    kq = _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
    return kq.stdout.decode().strip() if kq.returncode == 0 else None


def la_to_tien(repo, a, b):
    return _git(repo, "merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def tao_worktree(repo: Path, dich: Path, commit: str):
    xoa_worktree(repo, dich)
    dich.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "--detach", "--quiet", str(dich), commit)


def xoa_worktree(repo: Path, dich: Path):
    try:
        _git(repo, "worktree", "remove", "--force", str(dich), check=False)
    finally:
        shutil.rmtree(dich, ignore_errors=True)
    _git(repo, "worktree", "prune", check=False)


def dinh_hien_tai(repo, nhanh):
    kq = _git(repo, "ls-remote", "--exit-code", "origin", f"refs/heads/{nhanh}")
    dong = kq.stdout.decode().splitlines()
    return dong[0].split()[0] if len(dong) == 1 else None
