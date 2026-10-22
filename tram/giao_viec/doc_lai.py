"""Đọc lại Beads NGAY TRƯỚC cấp phiếu (spec 4 §5.1 "giới hạn nhất quán"; 4a-1 G3 — Đại ca đã chấp nhận rủi ro còn lại).

Snapshot dùng để chọn có thể cũ (bộ đệm ≤ 30 s; `bd list` đọc trước khi dựng gói). Trước khi trả đề xuất cho phần 3,
bộ chọn đọc lại danh sách (`bd list` — dạng JSON đã spike) và HUỶ nếu bead được chọn đã đổi nội dung có ý nghĩa
(nhãn, tiêu chí, mô tả, design, loại, phụ thuộc, cha, ưu tiên), đổi trạng thái/người nhận ngoài dự kiến, hoặc không
còn đủ điều kiện §5.1 trên bản mới (gồm "bị chặn" tính trên trạng thái MỚI của bead chặn). `updated_at`, `notes`
không tính. Thay đổi SAU lần đọc cuối tới lúc phần 3 cấp xong vẫn là rủi ro còn lại — không có giao dịch xuyên
Beads/SQLite, không gọi `bd` khi giữ khoá SQLite (3a-1 G11)."""
import hashlib
import json

from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.luat_cung import bi_chan_boi, kiem, quyet_dinh_da_chot
from tram.giao_viec.dieu_kien import ASSIGNEE, ly_do_khong_giao
from tram.giao_viec.feature import ly_do_khong_giao_spec


def dau_bead(b: Bead) -> str:
    noi_dung = [b.title, b.description, b.acceptance_criteria, b.design, b.issue_type, sorted(b.labels),
                sorted([p.depends_on_id, p.loai] for p in b.phu_thuoc), b.parent, b.priority]
    return hashlib.sha256(json.dumps(noi_dung, ensure_ascii=False).encode()).hexdigest()


def con_nguyen(bd, da: DuAn, cu: Bead, *, sau_claim: bool = False, buoc: str = "code",
               da_merge=lambda beads: frozenset(), adr_hop_le=lambda da, b: False) -> bool:
    """True = bead vẫn như snapshot `cu` và vẫn đủ điều kiện. `sau_claim`: vừa `--claim` nên phải là `in_progress`
    với assignee trạm; ngược lại trạng thái/người nhận phải y như snapshot."""
    try:
        theo_id = {b.id: b for b in bd.tat_ca()}
    except LoiBd:
        return False
    moi = theo_id.get(cu.id)
    if moi is None or dau_bead(moi) != dau_bead(cu):
        return False
    if (moi.status, moi.assignee) != (("in_progress", ASSIGNEE) if sau_claim else (cu.status, cu.assignee)):
        return False
    # Regex ADR trong nội dung không chứng minh quyết định đã được duyệt.
    if kiem(moi, da, theo_id).cham and not quyet_dinh_da_chot(moi, theo_id):
        if not adr_hop_le(da, moi):
            return False
    san = {moi.id} if moi.status == "open" and not bi_chan_boi(moi, theo_id) else set()
    if buoc == "spec":
        return not sau_claim and ly_do_khong_giao_spec(moi, san, da.ten) is None
    return ly_do_khong_giao(moi, theo_id, san, da, da_merge(list(theo_id.values()))) is None
