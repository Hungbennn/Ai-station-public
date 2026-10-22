"""Cờ đỏ theo gitnexus `detect_changes` (spec 4 §6.4 mục 3, lát 4c; kiến trúc §3 "tầng kiểm"): file của symbol
bị đổi VÀ của các luồng thực thi bị ảnh hưởng khớp `duong_dan` của bất kỳ hàng rào nào → cờ đỏ. Bổ sung, không
thay, cờ đỏ theo đường dẫn file của 4a. Chạy trên worktree tách rời của kho kiểm tại commit cần xét (không chạm
repo làm việc của Đại ca), xoá worktree sau khi xong. Không chắc (lỗi, partial, truncated) → vẫn gắn cờ đỏ
(`gitnexus-loi`): cờ đỏ chỉ là cảnh báo cho Đại ca, im lặng khi không biết mới là sai."""
import fnmatch
import subprocess
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.duong_dan import tram_home
from tram.giao_viec.git_kiem import tao_worktree, xoa_worktree
from tram.giao_viec.gitnexus import GitnexusCli, LoiGitnexus
from tram.kiem.diff import goc_nhanh


def khop_hang_rao(du_an: DuAn, tep: frozenset[str]) -> bool:
    return any(fnmatch.fnmatch(p, g) for rao in du_an.hang_rao.values() for g in rao.duong_dan for p in tep)


def co_do_gitnexus(gn: GitnexusCli | None, kho_git: Path, du_an: DuAn, commit: str) -> tuple[str, ...]:
    """() = không cờ (hoặc dự án chưa cấu hình gitnexus); ("gitnexus",) = chạm hàng rào; ("gitnexus-loi",)."""
    if gn is None or not du_an.gitnexus_repo:
        return ()
    wt = tram_home() / "gitnexus" / du_an.ten / commit[:12]
    try:
        goc = goc_nhanh(kho_git, f"origin/{du_an.nhanh_chinh}", commit)
        tao_worktree(kho_git, wt, commit)
        kq = gn.thay_doi(wt, goc, du_an.gitnexus_repo)
    except (LoiGitnexus, subprocess.CalledProcessError, OSError):
        return ("gitnexus-loi",)
    finally:
        xoa_worktree(kho_git, wt)
    if kq.khong_chac:
        return ("gitnexus-loi",)
    return ("gitnexus",) if khop_hang_rao(du_an, kq.tep) else ()
