"""Điều kiện 8 (spec 4 §5.1, §7.3): con của feature `theo-plan` chỉ được giao khi commit spec ĐÃ DUYỆT (sự kiện
`spec.duyet`) là tổ tiên của `origin/<nhanh_chinh>` trong kho kiểm của trạm (`git merge-base --is-ancestor`).
Không có kho kiểm hay chưa có `spec.duyet` → coi như chưa merge (fail-closed)."""
from pathlib import Path

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import la_to_tien
from tram.giao_viec.su_kien import SK, moi_nhat, su_kien_bead
from tram.phieu.kho import KhoPhieu


def commit_spec_duyet(ds: list[SK]) -> str | None:
    s = moi_nhat(ds, "spec.duyet")
    return s.du_lieu.get("commit") if s else None


def feature_da_merge(kho: KhoPhieu, da: DuAn, beads: list[Bead], kho_git: Path | None) -> frozenset[str]:
    if kho_git is None:
        return frozenset()
    ra = set()
    for b in beads:
        if b.issue_type != "feature" or "theo-plan" not in b.labels:
            continue
        c = commit_spec_duyet(su_kien_bead(kho, da.ten, b.id))
        if c and la_to_tien(kho_git, c, f"origin/{da.nhanh_chinh}"):
            ra.add(b.id)
    return frozenset(ra)
