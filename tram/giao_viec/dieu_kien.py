"""Bead đủ điều kiện (spec 4 §5.1 — luật cứng, G3): phần đọc được từ snapshot beads của dự án.
Điều kiện 5–7 (phiếu hiệu lực, ngân sách, khoá chống trùng) cần kho — bộ chọn kiểm sau (`ung_vien`), phần 3 kiểm
lại trong giao dịch cấp phiếu."""
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.luat_cung import bi_chan_boi
from tram.giao_viec.tieu_chi import tach_tieu_chi

LOAI_GIAO = frozenset({"bug", "task", "chore", "spike"})
NHAN_CAM = frozenset({"cot:cho-review", "can-spec", "cho-duyet-spec", "theo-plan"})
NHAN_COT_1 = "cot:ai-lam"
ASSIGNEE = "tram/giao-viec"


def can_moi_truong_kiem(bead: Bead) -> bool:
    """Phiếu chạy mã dự án (§5.1 điều kiện 9): code của bug/task/chore và qc; spike tài liệu thì không."""
    return bead.issue_type != "spike"


def ly_do_khong_giao(bead: Bead, theo_id: dict[str, Bead], san_sang: set[str], du_an: DuAn,
                     spec_da_merge: frozenset[str] = frozenset()) -> str | None:
    """None = đủ điều kiện nhận bước kế tiếp (lần đầu nếu `open`, bước sau nếu `in_progress`)."""
    cot = [n for n in bead.labels if n.startswith("cot:")]
    if len(cot) > 1:
        return "nhan-lech"                       # #8 — dashboard hiện "nhãn lệch"
    if cot != [NHAN_COT_1]:
        return "khong-o-cot-1"
    if NHAN_CAM & set(bead.labels):
        return "nhan-luong"
    if bead.issue_type not in LOAI_GIAO:
        return "loai-khong-giao"                 # feature/epic/decision/story/milestone (§4)
    if not tach_tieu_chi(bead.acceptance_criteria):
        return "thieu-tieu-chi"                  # "thiếu tiêu chí máy đọc được" (§5.1 điều kiện 4)
    if bead.parent and ((cha := theo_id.get(bead.parent)) is None
                        or ("theo-plan" in cha.labels and cha.id not in spec_da_merge)):
        return "cho-merge-spec"                  # điều kiện 8: commit spec đã duyệt chưa vào nhánh chính (4b)
    if bead.status == "open":
        if bead.id not in san_sang:
            return "bi-chan"                     # không nằm trong `bd ready`
    elif bead.status == "in_progress":
        if bead.assignee != ASSIGNEE:
            return "nguoi-khac-nhan"
        if bi_chan_boi(bead, theo_id):
            return "bi-chan"                     # gồm escalation mở; thiếu trong snapshot → chặn
    else:
        return "trang-thai"
    if can_moi_truong_kiem(bead) and du_an.moi_truong_kiem is None:
        return "thieu-moi-truong-kiem"           # điều kiện 9 — tick tạo escalation một lần
    return None
