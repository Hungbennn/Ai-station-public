"""Ba repo Git cục bộ cho test công bố (CHỈ DÙNG TRONG TEST): `remote` bare thay GitHub, `tram` = kho kiểm của trạm,
`tho` = kho của tài khoản quản lý thợ. Không mạng, hook tắt."""
from dataclasses import dataclass
from pathlib import Path

from git_gia import git, ghi, tao_repo


@dataclass
class BaKho:
    remote: Path
    tram: Path
    tho: Path
    cha: str


def dung_ba_kho(tmp_path: Path, monkeypatch) -> BaKho:
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    nguon = tao_repo(tmp_path / "nguon")
    cha = ghi(nguon, {"a.txt": "1\n"}, "goc")
    remote = tao_repo(tmp_path / "remote.git", bare=True)
    git(nguon, "push", "-q", str(remote), "HEAD:refs/heads/main")
    tram, tho = tmp_path / "tram" / "kho-kiem" / "hr-codex", tmp_path / "tho" / "kho" / "hr-codex"
    for p in (tram, tho):
        p.parent.mkdir(parents=True, exist_ok=True)
        git(p.parent, "clone", "-q", str(remote), p.name)
    return BaKho(remote, tram, tho, cha)


def commit_tho(b: BaKho, ref_tam: str, tep: dict[str, str], cha: str | None = None) -> str:
    """Thợ làm một commit từ `cha` và đặt nhánh cục bộ `ref_tam` trỏ vào đó (phương án nào cũng có bước này)."""
    git(b.tho, "checkout", "-q", "-B", "lam", cha or b.cha)
    sha = ghi(b.tho, tep, "lam")
    git(b.tho, "branch", "-f", ref_tam, sha)
    return sha
