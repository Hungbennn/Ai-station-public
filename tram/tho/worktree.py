"""Kho + worktree của phiếu trên máy thợ (spec 3 §7.1). Tiến trình quản lý chạy (không phải agent); hook Git tắt.

Worktree đã có: HEAD = `cha`, sạch → dùng lại; có thay đổi chưa commit → commit `wip: rác lượt trước`; HEAD không phải
tổ tiên của `cha` → giữ ở nhánh cục bộ `rac/<bead>-<thời điểm>` (không push) rồi đưa về `cha`; HEAD là tổ tiên của
`cha` → đưa về `cha`. `luot` đổi → xoá `.tram/tien-do.md`, `.tram/goi.md`."""
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

GIT = ("git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false")
DANH_TINH = ("-c", "user.name=tram-tho", "-c", "user.email=tram-tho@localhost")
TEN_NHANH = re.compile(r"tram/[A-Za-z0-9][A-Za-z0-9._-]{0,63}(/[A-Za-z0-9][A-Za-z0-9._-]{0,63})?")
XOA_KHI_DOI_LUOT = ("tien-do.md", "goi.md")


@dataclass(frozen=True)
class KetQuaChuanBi:
    worktree: Path
    nhanh_rac: str | None        # có → thợ gửi `chay.don_rac {giao_id, nhanh_rac}`


def duong_dan_worktree(goc: Path, du_an: str, nhanh: str) -> Path:
    """`~/tram/worktrees/<du-an>/<repo.nhanh bỏ tiền tố tram/>`. Thợ từ chối nhánh ngoài `tram/` (Q7)."""
    if not TEN_NHANH.fullmatch(nhanh) or ".." in nhanh or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", du_an):
        raise ValueError(f"Nhánh {nhanh!r} / dự án {du_an!r} không hợp lệ (nhánh phải bắt đầu bằng tram/)")
    return goc / du_an / nhanh.removeprefix("tram/")


def _git(cwd: Path, *args: str, chay=subprocess.run, kiem: bool = True) -> subprocess.CompletedProcess:
    return chay([*GIT, "-C", str(cwd), *args], capture_output=True, text=True, check=kiem)


def _them_exclude(kho: Path, chay) -> None:
    chung = Path(_git(kho, "rev-parse", "--git-common-dir", chay=chay).stdout.strip())
    p = (chung if chung.is_absolute() else kho / chung) / "info" / "exclude"
    p.parent.mkdir(parents=True, exist_ok=True)
    cu = p.read_text(encoding="utf-8") if p.exists() else ""
    if ".tram/" not in cu.splitlines():
        p.write_text(cu + ("" if cu.endswith("\n") or not cu else "\n") + ".tram/\n", encoding="utf-8")


def _doi_luot(wt: Path, luot: int) -> None:
    d = wt / ".tram"
    d.mkdir(exist_ok=True)
    moc = d / "luot"
    if not moc.exists() or moc.read_text().strip() != str(luot):
        for ten in XOA_KHI_DOI_LUOT:
            (d / ten).unlink(missing_ok=True)
        moc.write_text(f"{luot}\n")


def _don(wt: Path, nhanh: str, cha: str, rac: str, chay) -> str | None:
    if _git(wt, "status", "--porcelain", chay=chay).stdout.strip():
        co_ten = _git(wt, "config", "user.email", chay=chay, kiem=False).stdout.strip()
        _git(wt, "add", "-A", chay=chay)
        _git(wt, *(() if co_ten else DANH_TINH), "commit", "-q", "-m", "wip: rác lượt trước", chay=chay)
    head = _git(wt, "rev-parse", "HEAD", chay=chay).stdout.strip()
    giu = head != cha and _git(wt, "merge-base", "--is-ancestor", head, cha, chay=chay, kiem=False).returncode != 0
    if giu:
        _git(wt, "branch", rac, head, chay=chay)
    _git(wt, "checkout", "-q", "-B", nhanh, cha, chay=chay)
    return rac if giu else None


def chuan_bi_worktree(kho: Path, wt: Path, *, nhanh: str, cha: str, bead_id: str, luot: int, bay_gio: datetime,
                      chay=subprocess.run) -> KetQuaChuanBi:
    _git(kho, "fetch", "-q", "origin", chay=chay)
    _them_exclude(kho, chay)
    cha = _git(kho, "rev-parse", "--verify", f"{cha}^{{commit}}", chay=chay).stdout.strip()
    rac = None
    if wt.exists():
        rac = _don(wt, nhanh, cha, f"rac/{bead_id}-{bay_gio:%Y%m%dT%H%M%SZ}", chay)
    else:
        wt.parent.mkdir(parents=True, exist_ok=True)
        _git(kho, "worktree", "add", "-q", "-B", nhanh, str(wt), cha, chay=chay)
    _doi_luot(wt, luot)
    return KetQuaChuanBi(wt, rac)
