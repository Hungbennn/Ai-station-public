"""Remote dự án giả + kho kiểm của trạm cho test (CHỈ DÙNG TRONG TEST): repo bare cục bộ, không mạng."""
from dataclasses import dataclass
from pathlib import Path

from git_gia import ghi, git, tao_repo

GOC = {"AGENTS.md": "# Quy ước dự án\n", "CLAUDE.md": "Đọc AGENTS.md\n", "src/tom_tat.py": "x = 1\n",
       "kiem.sh": "exit 0\n", "docs/handovers/.keep": ""}


@dataclass
class KhoGia:
    origin: Path       # remote dự án (bare)
    dev: Path          # repo để test tạo commit rồi push
    kho: Path          # kho kiểm của trạm (clone của origin)
    main: str          # SHA nhánh chính ban đầu

    def day(self, nhanh: str, tep: dict, msg: str = "c", tu: str | None = None) -> str:
        """Commit `tep` lên `nhanh` (bắt đầu từ `tu` nếu có) rồi push lên origin; trả SHA."""
        git(self.dev, "checkout", "-q", "-B", nhanh, tu or "HEAD")
        sha = ghi(self.dev, tep, msg)
        git(self.dev, "push", "-q", "-f", "origin", f"HEAD:refs/heads/{nhanh}")
        return sha


def dung_kho(tmp_path: Path) -> KhoGia:
    origin = tao_repo(tmp_path / "origin.git", bare=True)
    dev = tao_repo(tmp_path / "dev")
    main = ghi(dev, GOC, "goc")
    git(dev, "remote", "add", "origin", str(origin))
    git(dev, "push", "-q", "origin", "HEAD:refs/heads/main")
    git(tmp_path, "clone", "-q", str(origin), str(tmp_path / "kho-kiem"))
    return KhoGia(origin, dev, tmp_path / "kho-kiem", main)
