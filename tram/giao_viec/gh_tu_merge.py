"""Phần `gh` của tự merge (change `tu-merge-tu-deploy`, design D-2, D-3; D93): dạng DUY NHẤT của lệnh merge và đọc
CI từ `statusCheckRollup` của `gh pr view`. Hàm thuần — `gh.py` gọi.

Lệnh merge chỉ có một dạng: `gh pr merge <so> --repo <owner/repo> --merge --match-head-commit <sha>` — merge commit
thường (xác minh merge hiện có không chứng minh được squash/rebase), GitHub từ chối nếu đầu PR đã khác commit đã kiểm.
Không bao giờ thêm cờ khác (quyền quản trị, gộp dồn, tự động, xoá nhánh)."""
import re

SHA_RE = re.compile(r"[0-9a-f]{40}")
REPO_RE = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")


def dang_merge(repo: str, so: int, commit: str) -> list[str] | None:
    """Đối số sau `gh pr merge` — None khi tham số không hợp lệ (không chạy gì)."""
    if not REPO_RE.fullmatch(repo) or type(so) is not int or so <= 0 or not SHA_RE.fullmatch(commit):
        return None
    return [str(so), "--repo", repo, "--merge", "--match-head-commit", commit]


def la_dang_merge(args: tuple[str, ...]) -> bool:
    """Chặn ở cửa `GhCli._gh`: đối số của `merge` phải đúng y dạng `dang_merge` sinh ra."""
    return (len(args) == 6 and args[0].isdigit() and args[0] == str(int(args[0]))
            and dang_merge(args[2], int(args[0]), args[5]) == list(args))
