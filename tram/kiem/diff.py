"""Danh sách file đổi từ gốc nhánh (spec 4 §6.2 bước 0): `git merge-base` rồi `git diff --name-status -z
--find-renames` — đọc tách bằng NUL, lấy CẢ tên cũ và tên mới của rename/copy. Hook Git tắt."""
import os
import subprocess
from collections.abc import Iterable
from pathlib import Path

from tram.kiem.duong_dan_cam import duong_dan_cham_cam

GIT = ("git", "-c", "core.hooksPath=/dev/null")


def _git(repo: Path, *args: str, chay=subprocess.run) -> bytes:
    return chay([*GIT, "-C", str(repo), *args], capture_output=True, check=True, timeout=60).stdout


def goc_nhanh(repo: Path, nhanh_chinh: str, commit: str, *, chay=subprocess.run) -> str:
    """`nhanh_chinh` là ref đầy đủ người gọi chọn, vd `origin/main`."""
    return _git(repo, "merge-base", nhanh_chinh, commit, chay=chay).decode().strip()


def tep_doi(repo: Path, goc: str, commit: str, *, chay=subprocess.run) -> list[str]:
    tho = _git(repo, "diff", "--no-ext-diff", "--name-status", "-z", "--find-renames", f"{goc}..{commit}",
               chay=chay)
    phan = [os.fsdecode(x) for x in tho.split(b"\0") if x]
    ra, i = [], 0
    while i < len(phan):
        so_ten = 2 if phan[i][:1] in ("R", "C") else 1
        ra += phan[i + 1:i + 1 + so_ten]
        i += 1 + so_ten
    return ra


def diff_cham_cam(repo: Path, nhanh_chinh: str, commit: str, *, them: Iterable[str] = (),
                  cho_phep: Iterable[str] = (), bat_buoc: Iterable[str] = (), chay=subprocess.run) -> list[str]:
    goc = goc_nhanh(repo, nhanh_chinh, commit, chay=chay)
    return duong_dan_cham_cam(tep_doi(repo, goc, commit, chay=chay), them=them, cho_phep=cho_phep,
                               bat_buoc=bat_buoc)
