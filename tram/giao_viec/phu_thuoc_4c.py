"""Phụ thuộc ngoài của lát 4c gom một chỗ cho `BoGiaoViec.p4c` (spec 4 §3 hàng 4c): `gh` (mở PR, xác minh merge),
gitnexus (cờ đỏ, luồng lớp 1), recall memory (lớp 5). Mặc định mọi thứ TẮT (None) — hành vi 4a/4b giữ nguyên.
Bật thật = nối ở nơi tram-api dựng `BoGiaoViec` sau cổng (S7 cho `gh`, spike GN cho gitnexus) — xem plan 4c."""
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.prompt import boc_khong_tin_cay
from tram.giao_viec.gh import GhCli, repo_github_cua
from tram.giao_viec.gitnexus import GitnexusCli, LoiGitnexus
from tram.giao_viec.lop_5 import NhoLai
from tram.nho.khach import tao_nho_lai

KY_TU_LUONG = 4000


@dataclass(frozen=True)
class PhuThuoc4c:
    gh: GhCli | None = None
    github_repo: Callable[[Path], str | None] = repo_github_cua
    gitnexus: GitnexusCli | None = None
    nho_lai: NhoLai | None = None


def luong_lien_quan(gn: GitnexusCli | None, du_an: DuAn, bead: Bead) -> str:
    """Lớp 1, phần 4c: luồng liên quan tới bead theo index gitnexus của dự án; lỗi/chưa cấu hình → rỗng."""
    if gn is None or not du_an.gitnexus_repo:
        return ""
    try:
        ds = gn.luong(f"{bead.title}\n{bead.description or ''}", du_an.gitnexus_repo)
    except LoiGitnexus:
        return ""
    van = "\n".join(f"- {ten}: {', '.join(tep) or '(không rõ file)'}" for ten, tep in ds)[:KY_TU_LUONG]
    return boc_khong_tin_cay(van) if van else ""


def tao_phu_thuoc_4c(*, github: bool, gitnexus: bool, memory: bool = False, which=shutil.which,
                     chay=subprocess.run) -> PhuThuoc4c:
    """Dựng cho tram-api. `github`/`gitnexus` do người nối bật SAU cổng; recall bật khi có `tram-nho-token`."""
    return PhuThuoc4c(gh=GhCli() if github and which("gh") else None,
                      gitnexus=GitnexusCli() if gitnexus and which("gitnexus") else None,
                      nho_lai=tao_nho_lai(chay=chay) if memory else None)
