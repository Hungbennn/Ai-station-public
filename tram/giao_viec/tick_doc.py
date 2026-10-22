"""Các bước CHỈ GHI SỰ KIỆN của vòng tick (spec 4 §10 bước 2, 3; §8 chu kỳ) — vẫn chạy khi estop."""
import json
from datetime import datetime

from tram.beads.mo_hinh import Bead
from tram.giao_viec.escalation import NHAN
from tram.giao_viec.ngan_sach import mo_chu_ky
from tram.giao_viec.su_kien import da_co, ghi_mot_lan
from tram.phieu.kho import KhoPhieu


def ghi_escalation_dong(kho: KhoPhieu, du_an: str, beads: list[Bead], luc: datetime) -> int:
    """Decision `tram:escalation` đã đóng (dashboard hay `bd` tay) → `escalation.dong` đúng một lần."""
    so = 0
    for b in beads:
        if b.issue_type != "decision" or NHAN not in b.labels or b.status != "closed":
            continue
        h = kho.db.execute("SELECT du_lieu FROM su_kien WHERE du_an = ? AND loai = 'escalation.tao' AND"
                           " json_extract(du_lieu, '$.escalation_id') = ?"
                           " ORDER BY id LIMIT 1", (du_an, b.id)).fetchone()
        if h is None:
            continue                                     # decision không do trạm tạo
        d = json.loads(h[0])
        so += ghi_mot_lan(kho, du_an, "escalation.dong", {**d, "tra_loi": b.close_reason}, bead_id=d["bead_goc"],
                          luc=luc, khoa=("escalation_id",)) is not None
    return so


def ghi_bead_dong(kho: KhoPhieu, du_an: str, beads: list[Bead], luc: datetime) -> int:
    """Bead trạm đã giao việc mà nay đóng → `bead.dong {du_an, bead_id}` (thợ dọn worktree)."""
    da_giao = {r[0] for r in kho.db.execute("SELECT DISTINCT bead_id FROM su_kien WHERE du_an = ? AND"
                                            " loai = 'giao.nhan'", (du_an,))}
    return sum(ghi_mot_lan(kho, du_an, "bead.dong", {"du_an": du_an, "bead_id": b.id}, bead_id=b.id, luc=luc,
                           khoa=("bead_id",)) is not None
               for b in beads if b.status == "closed" and b.id in da_giao)


def mo_chu_ky_con_thieu(kho: KhoPhieu, du_an: str, luc: datetime) -> int:
    """`escalation.dong`, `cot.tra_ve`, `spec.tra_ve` (4b) mở chu kỳ ngân sách mới (#16) — tách khỏi bước ghi nguồn
    để crash giữa hai bước vẫn bù được ở vòng sau."""
    so = 0
    for i, bead_id in kho.db.execute("SELECT id, bead_id FROM su_kien WHERE du_an = ? AND bead_id IS NOT NULL AND"
                                     " loai IN ('escalation.dong', 'cot.tra_ve', 'spec.tra_ve') ORDER BY id",
                                     (du_an,)).fetchall():
        if not da_co(kho, du_an, "ngan_sach.chu_ky_moi", {"bead_id": bead_id, "nguon_su_kien_id": i}):
            so += mo_chu_ky(kho, du_an, bead_id, i, luc)
    return so
