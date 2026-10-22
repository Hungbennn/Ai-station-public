"""Repo Git tạm cho test (CHỈ DÙNG TRONG TEST): không mạng, hook tắt, bỏ cấu hình git toàn cục của máy."""
import os
import subprocess
from pathlib import Path

CO = ["-c", "core.hooksPath=/dev/null", "-c", "user.name=tram-test", "-c", "user.email=test@tram.local",
      "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]
MOI_TRUONG = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *CO, "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env=MOI_TRUONG).stdout.strip()


def tao_repo(p: Path, *, bare: bool = False) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    git(p, "init", "-q", *(["--bare"] if bare else []))
    return p


def ghi(repo: Path, tep: dict[str, str | None], msg: str = "c") -> str:
    """Ghi (None = xoá) rồi commit mọi thay đổi; trả SHA mới."""
    for ten, noi_dung in tep.items():
        if noi_dung is None:
            git(repo, "rm", "-q", ten)
            continue
        f = repo / ten
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(noi_dung, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", msg)
    return git(repo, "rev-parse", "HEAD")
