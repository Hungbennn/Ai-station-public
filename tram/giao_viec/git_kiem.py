"""Kho kiểm của trạm (spec 4 §6.2 bước 1, §11 lớp 1): một bản clone repo dự án do TÀI KHOẢN TRẠM giữ ở
`~/.tram/kho-kiem/<du_an>`, `origin` = remote dự án. Mọi lệnh git: danh sách đối số, hook tắt, không hỏi mật khẩu.
Tạo kho kiểm (clone từ GitHub) và trao quyền ghi cho principal `tram-kiem` là việc chờ cổng (S6, S7)."""
import os
import shutil
import subprocess
from pathlib import Path

from tram.duong_dan import tram_home

GIT = ("git", "-c", "core.hooksPath=/dev/null")
MODE_FILE_THUONG = (b"100644", b"100755")


def kho_kiem(ten_du_an: str) -> Path:
    return tram_home() / "kho-kiem" / ten_du_an


def _git(kho: Path, *args: str, check: bool = True, timeout: float | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, check=check, timeout=timeout,
                          env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


def fetch(kho: Path, *, thoi_gian_cho: float = 120.0) -> None:
    """Quá `thoi_gian_cho` giây → `subprocess.TimeoutExpired` (vòng tick đếm lỗi dự án đó, dự án khác chạy tiếp)."""
    _git(kho, "fetch", "--quiet", "--prune", "origin", timeout=thoi_gian_cho)


def sha_cua(kho: Path, ref: str) -> str | None:
    kq = _git(kho, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
    return kq.stdout.decode().strip() or None if kq.returncode == 0 else None


def la_to_tien(kho: Path, a: str, b: str) -> bool:
    """`a` là tổ tiên (hoặc chính là) `b`. Commit không có trong kho → False."""
    return _git(kho, "merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def doc_file(kho: Path, ref: str, duong: str, gioi_han: int = 200_000) -> str | None:
    """Nội dung file THƯỜNG `duong` tại `ref` (không symlink/submodule — git không đi qua symlink); cắt
    `gioi_han` ký tự. Không có → None."""
    kq = _git(kho, "ls-tree", "-z", ref, "--", duong, check=False)
    dong = [x for x in kq.stdout.split(b"\0") if x] if kq.returncode == 0 else []
    if len(dong) != 1:
        return None
    dau, _ = dong[0].split(b"\t", 1)
    mode, loai, sha = dau.split(b" ")
    if loai != b"blob" or mode not in MODE_FILE_THUONG:
        return None
    return _git(kho, "cat-file", "blob", sha.decode()).stdout.decode("utf-8", "replace")[:gioi_han]


def diff_theo_file(kho: Path, a: str, b: str) -> list[tuple[str, str]]:
    """`git diff a..b` tách theo file: [(đường dẫn, đoạn diff)] — cho lớp 4 của phiếu QC (§11)."""
    tho = _git(kho, "diff", "--no-ext-diff", "--no-color", f"{a}..{b}").stdout.decode("utf-8", "replace")
    ra = []
    for doan in tho.split("diff --git ")[1:]:
        dau = doan.split("\n", 1)[0]
        ra.append((dau.split(" b/", 1)[-1], "diff --git " + doan))
    return ra


def tao_worktree(kho: Path, dich: Path, commit: str) -> Path:
    """Xoá worktree kiểm cũ cùng chỗ rồi `git worktree add --detach <dich> <commit>`."""
    xoa_worktree(kho, dich)
    dich.parent.mkdir(parents=True, exist_ok=True)
    _git(kho, "worktree", "add", "--detach", "--quiet", str(dich), commit)
    return dich


def xoa_worktree(kho: Path, dich: Path) -> None:
    _git(kho, "worktree", "remove", "--force", str(dich), check=False)
    shutil.rmtree(dich, ignore_errors=True)
    _git(kho, "worktree", "prune", check=False)
