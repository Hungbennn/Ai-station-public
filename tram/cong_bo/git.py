"""Lệnh Git của TRẠM khi công bố (spec 3 §6.4, §6.6): chạy trong kho của tài khoản trạm (`~/.tram/kho-kiem/<dự án>`
— dùng chung với kiểm lại của phần 4), danh sách đối số, hook tắt, không hỏi mật khẩu, mỗi lệnh có timeout. Ref công
bố chỉ đổi bằng compare-and-swap (`--force-with-lease=<ref>:<sha mong đợi>`; mong đợi rỗng = ref chưa được có).
Kết quả push: `ok` | `tu_choi` (remote từ chối: lease sai, branch protection) | `khong_ro` (timeout, mất mạng — có thể
remote ĐÃ nhận: phải đối soát bằng SHA, §6.6)."""
import os
import subprocess
from pathlib import Path

GIT = ("git", "-c", "core.hooksPath=/dev/null")
TU_CHOI = ("[rejected]", "[remote rejected]", "stale info")


class LoiGit(RuntimeError):
    pass


def _git(kho: Path, *args: str, timeout: float, check: bool = True) -> subprocess.CompletedProcess:
    try:
        return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, text=True, timeout=timeout,
                              check=check, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    except subprocess.TimeoutExpired as e:
        raise LoiGit(f"git {args[0]} quá {timeout:g} s") from e
    except subprocess.CalledProcessError as e:
        raise LoiGit(f"git {args[0]} lỗi: {(e.stderr or '').strip()[:200]}") from e


def fetch_ve(kho: Path, nguon: str, ref: str, dich: str, *, timeout: float, safe: Path | None = None) -> str | None:
    """`git fetch <nguon> +<ref>:<dich>`; trả SHA của `dich`, None khi nguồn không có ref hoặc lỗi."""
    co = ["-c", f"safe.directory={safe}"] if safe else []
    try:
        _git(kho, *co, "fetch", "--no-tags", "--quiet", nguon, f"+{ref}:{dich}", timeout=timeout)
        return _git(kho, "rev-parse", "--verify", "--quiet", f"{dich}^{{commit}}", timeout=timeout).stdout.strip()
    except LoiGit:
        return None


def la_hau_due(kho: Path, goc: str, commit: str, *, timeout: float = 30) -> bool:
    """`commit` là `goc` hoặc hậu duệ của nó (spec §6.4 bước 4)."""
    try:
        return _git(kho, "merge-base", "--is-ancestor", goc, commit, timeout=timeout, check=False).returncode == 0
    except LoiGit:
        return False


def sha_remote(kho: Path, nhanh: str, *, timeout: float) -> str | None:
    """SHA của `refs/heads/<nhanh>` trên origin; None = chưa có. Không gọi được → LoiGit (không đoán)."""
    ra = _git(kho, "ls-remote", "--heads", "origin", f"refs/heads/{nhanh}", timeout=timeout).stdout.split()
    return ra[0] if ra else None


def cac_ref_remote(kho: Path, mau: str, *, timeout: float) -> list[tuple[str, str]]:
    """[(sha, tên nhánh)] trên origin khớp `refs/heads/<mau>`. Không gọi được → LoiGit."""
    dong = _git(kho, "ls-remote", "--heads", "origin", f"refs/heads/{mau}", timeout=timeout).stdout.splitlines()
    return [(sha, ref.removeprefix("refs/heads/")) for sha, ref in (d.split("\t", 1) for d in dong if "\t" in d)]


def _day(kho: Path, nhanh: str, sha_cu: str | None, nguon: str, *, timeout: float) -> str:
    try:
        kq = _git(kho, "push", "--porcelain", f"--force-with-lease=refs/heads/{nhanh}:{sha_cu or ''}", "origin",
                  f"{nguon}:refs/heads/{nhanh}", timeout=timeout, check=False)
    except LoiGit:
        return "khong_ro"
    if kq.returncode == 0:
        return "ok"
    return "tu_choi" if any(x in kq.stdout + kq.stderr for x in TU_CHOI) else "khong_ro"


def day_cas(kho: Path, commit: str, nhanh: str, sha_cu: str | None, *, timeout: float) -> str:
    """Đặt `refs/heads/<nhanh>` trên origin = `commit` CHỈ KHI nó đang là `sha_cu` (None = chưa có)."""
    return _day(kho, nhanh, sha_cu, commit, timeout=timeout)


def xoa_cas(kho: Path, nhanh: str, sha_cu: str, *, timeout: float) -> str:
    """Xoá `refs/heads/<nhanh>` trên origin CHỈ KHI nó đang là `sha_cu`."""
    return _day(kho, nhanh, sha_cu, "", timeout=timeout)
