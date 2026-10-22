"""Vòng tick bước 4 (spec 4 §10): feature `theo-plan`. Commit spec đã duyệt (`spec.duyet`) chưa vào nhánh chính sau
24 giờ → `spec.cho_merge {feature, commit}` (Telegram nhắc; một lần mỗi commit). Mọi con đã đóng → `feature.xong
{feature}` (một lần mỗi feature) — Phê duyệt "Feature xong, chờ đóng"; trạm KHÔNG tự đóng feature (#16).
Chỉ ghi sự kiện nên chạy cả khi estop. Điều kiện 8 (con chờ merge) tính lúc chọn việc (`spec_merge`)."""
from datetime import datetime, timedelta
from pathlib import Path

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.duong_dan import doc_luc
from tram.giao_viec.git_kiem import la_to_tien
from tram.giao_viec.su_kien import ghi_mot_lan, moi_nhat, su_kien_bead
from tram.phieu.kho import KhoPhieu

CHO_MERGE = timedelta(hours=24)


def _nhac_merge(kho: KhoPhieu, da: DuAn, b: Bead, kho_git: Path | None, luc: datetime) -> bool:
    duyet = moi_nhat(su_kien_bead(kho, da.ten, b.id), "spec.duyet")
    if duyet is None or kho_git is None or luc - doc_luc(duyet.luc) < CHO_MERGE:
        return False
    c = duyet.du_lieu["commit"]
    if la_to_tien(kho_git, c, f"origin/{da.nhanh_chinh}"):
        return False
    return ghi_mot_lan(kho, da.ten, "spec.cho_merge", {"feature": b.id, "commit": c}, bead_id=b.id, luc=luc,
                       khoa=("feature", "commit")) is not None


def buoc_theo_plan(kho: KhoPhieu, da: DuAn, beads: list[Bead], kho_git: Path | None, luc: datetime) -> dict[str, int]:
    dem = {"spec_cho_merge": 0, "feature_xong": 0}
    for b in beads:
        if b.issue_type != "feature" or "theo-plan" not in b.labels or b.status == "closed":
            continue
        dem["spec_cho_merge"] += _nhac_merge(kho, da, b, kho_git, luc)
        con = [x for x in beads if x.parent == b.id]
        if kho_git is None and con and all(x.status == "closed" for x in con):
            dem["feature_xong"] += ghi_mot_lan(kho, da.ten, "feature.xong", {"feature": b.id}, bead_id=b.id,
                                               luc=luc, khoa=("feature",)) is not None
    return {k: v for k, v in dem.items() if v}
