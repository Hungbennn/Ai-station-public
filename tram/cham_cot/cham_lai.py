"""Yêu cầu chấm lại khi decision mà bead phụ thuộc `blocks` được đóng, mở lại, đổi `close_reason`
hoặc biến mất khỏi snapshot (spec 0+1a §5.6). Không dựa vào `updated_at` của bead gốc."""
from tram.beads.mo_hinh import Bead
from tram.cham_cot.bo_qua import ly_do_bo_qua_co_dinh
from tram.cham_cot.luat_cung import LOAI_CHAN

_CHUA_CO = [False, ""]  # decision chưa từng thấy = coi như đang mở, chưa có lời đáp


def anh_decision(beads: list[Bead]) -> dict[str, list]:
    """{id: [đã_đóng, close_reason]} của mọi bead decision trong snapshot."""
    return {b.id: [b.status == "closed", b.close_reason] for b in beads if b.issue_type == "decision"}


def decision_doi(truoc: dict[str, list] | None, sau: dict[str, list]) -> list[str]:
    """ID decision đổi giữa hai ảnh. Chưa có ảnh trước (lượt đầu) → [] — chỉ khởi tạo."""
    if truoc is None:
        return []
    return sorted(i for i in set(truoc) | set(sau) if truoc.get(i, _CHUA_CO) != sau.get(i))


def yeu_cau_tu_decision(beads: list[Bead], doi: list[str]) -> list[tuple[str, dict]]:
    """(bead_id, {"decision_ids": [...]}) cho mỗi bead không thuộc diện bỏ qua cố định (cùng luật với
    bộ quét — 4a thêm điều kiện ở một chỗ) phụ thuộc `blocks` vào ít nhất một decision đã đổi.
    `nguon` do kho chèn khi ghi."""
    tap = set(doi)
    return [(b.id, {"decision_ids": sorted(chung)})
            for b in beads
            if ly_do_bo_qua_co_dinh(b) is None
            and (chung := tap & {p.depends_on_id for p in b.phu_thuoc if p.loai == LOAI_CHAN})]


def phat_hien_decision_doi(kho, du_an_ten: str, beads: list[Bead]) -> int:
    """So ảnh decision với lượt trước, tạo yêu cầu bền, lưu ảnh mới — một giao dịch. Trả số yêu cầu."""
    sau = anh_decision(beads)
    truoc = kho.yeu_cau.doc_anh_decision(du_an_ten)
    yeu_cau = yeu_cau_tu_decision(beads, decision_doi(truoc, sau))
    if truoc != sau:
        kho.yeu_cau.luu_anh_decision(du_an_ten, sau, yeu_cau)
    return len(yeu_cau)
