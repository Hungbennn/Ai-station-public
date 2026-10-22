"""Vòng tick — bước GitHub của lát 4c (spec 4 §6.4 mục 4, §6.5, §7.3), chạy SAU khi đẩy pipeline: bead đang ở cột
3 → mở PR / điền `pr` / tự merge khi dự án bật (TM-2, design D-1) / xác minh merge rồi đóng; feature `theo-plan` →
mở PR cho commit spec đã duyệt, rồi tự gộp PR đó khi dự án bật (D95, design D-11).
Không chạy khi estop (ghi GitHub + beads), khi `p4c.gh` chưa nối, hoặc remote kho kiểm không phải github.com.
`gh` lỗi ở một bead → đếm `loi_gh`, bead khác chạy tiếp; vòng sau làm lại (mọi bước idempotent)."""
from collections import Counter
from datetime import datetime
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.gh import LoiGh
from tram.giao_viec.pr import NHAN_REVIEW, NHAN_THEO_PLAN, mo_pr_bead, mo_pr_spec
from tram.giao_viec.pr_merge import kiem_merge
from tram.giao_viec.su_kien import su_kien_bead
from tram.giao_viec.tu_merge import tu_merge_spec, xet_tu_merge
from tram.phieu.kho import KhoPhieu


def buoc_github(bo, kho: KhoPhieu, da: DuAn, bd, beads: list, kg: Path | None, luc: datetime) -> dict[str, int]:
    gh = bo.p4c.gh
    if gh is None or kg is None or (repo := bo.p4c.github_repo(kg)) is None:
        return {}
    dem = Counter()
    for b in beads:
        if b.status == "closed" or not {NHAN_REVIEW, NHAN_THEO_PLAN} & set(b.labels):
            continue
        ds = su_kien_bead(kho, da.ten, b.id)
        try:
            if NHAN_REVIEW in b.labels:
                k = (mo_pr_bead(gh, repo, kho, kg, da, bd, b, ds, luc)
                     or xet_tu_merge(gh, repo, kho, kg, da, bd, b, ds, luc)
                     or kiem_merge(gh, repo, kho, kg, da, bd, b, ds, luc))
            else:
                k = (mo_pr_spec(gh, repo, kho, kg, da, b, ds, luc)
                     or tu_merge_spec(gh, repo, kho, kg, da, bd, b, ds, luc))
        except LoiGh:
            k = "loi_gh"
        if k:
            dem[k] += 1
    return dict(dem)
