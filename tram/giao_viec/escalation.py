"""Escalation (spec 4 §9 — điểm dừng #3): một bead `decision` nhãn `tram:escalation` CHẶN bead gốc (`blocks`).
Luật cứng 1a xếp decision mở vào cột 2. Trạm là bên duy nhất ghi beads (`--actor tram/giao-viec`).

ID thao tác bền = băm tất định của (dự án, bead gốc, lý do, nguồn) — phát lại cùng nguồn ra cùng ID; dấu ID nằm
trong mô tả/notes nên kết quả không rõ (crash, timeout) được ĐỐI SOÁT trước khi tạo lại (spec 3 §6.6)."""
import hashlib
from datetime import datetime

from tram.beads.mo_hinh import Bead
from tram.cham_cot.luat_cung import LOAI_CHAN
from tram.giao_viec.su_kien import da_co, ghi_mot_lan
from tram.phieu.kho import KhoPhieu
from tram.nho.bi_mat import quet

NHAN = "tram:escalation"
LY_DO = ("agent-bi", "can-thao-tac-nguy-hiem", "agent-can-hoi", "het-ngan-sach", "nhanh-bi-day",
         "thieu-moi-truong-kiem", "dong-file-cau-hinh", "qc-doi-ma", "spec-tra-ve-nhieu", "phieu-thieu",
         "cay-khac-nguon")
LY_DO_BI = {"sai-model": "agent-bi", "agent": "agent-bi", "thieu-moi-truong-kiem": "thieu-moi-truong-kiem",
            "nhanh-bi-day-ngoai-luong": "nhanh-bi-day"}          # bao.bi khác (khe-tat, estop…) → giao lại
LY_DO_HOI = {"thao_tac_nguy_hiem": "can-thao-tac-nguy-hiem", "can_quyet_dinh": "agent-can-hoi"}
CAU_HOI = {"het-ngan-sach": "Bead đã dùng hết ngân sách chu kỳ. Làm tiếp, đổi hướng hay dừng?",
           "thieu-moi-truong-kiem": "Dự án chưa có `moi_truong_kiem` (hoặc file không đọc được). Đặt rồi trả lời.",
           "dong-file-cau-hinh": "Diff chạm đường dẫn cấm. Trả lời 'hoàn tác', hoặc thêm ngoại lệ cụ thể rồi trả lời.",
           "qc-doi-ma": "Khe QC đã đổi file ngoài docs/handovers/. QC không được công nhận.",
           "cay-khac-nguon": "Bản chép kiểm không dựng lại được đúng cây git của commit (CRLF/text, ident, encoding, "
                             "trùng tên hoa-thường, submodule hoặc filter của kho kiểm). Sửa repo rồi trả lời."}


def ma_escalation(du_an: str, bead_id: str, ly_do: str, nguon: str) -> str:
    return "esc-" + hashlib.sha256(f"{du_an}:{bead_id}:{ly_do}:{nguon}".encode()).hexdigest()[:20]


def _dau(ma: str) -> str:
    return f"<!-- ma_thao_tac: {ma} -->"


def _la_esc_mo(b: Bead, bead_goc: str, ly_do: str) -> bool:
    dong = b.description.splitlines()
    return (b.issue_type == "decision" and NHAN in b.labels and b.status != "closed"
            and f"bead_goc: {bead_goc}" in dong and f"ly_do: {ly_do}" in dong)


def tao_escalation(bd, kho: KhoPhieu, du_an: str, bead: Bead, *, ly_do: str, cau_hoi: str, giao_id: str | None,
                   nguon: str, luc: datetime) -> str | None:
    """Tạo (hoặc gộp vào escalation mở cùng `ly_do` của bead gốc) rồi chặn bead gốc. Trả id escalation;
    None khi nguồn này đã xử lý xong trước đó."""
    if ly_do not in LY_DO:
        raise ValueError(f"ly_do escalation lạ: {ly_do}")
    ma = ma_escalation(du_an, bead.id, ly_do, nguon)
    if da_co(kho, du_an, "escalation.tao", {"ma_thao_tac": ma}):
        return None
    cau_hoi = cau_hoi or CAU_HOI.get(ly_do, "")
    if quet([cau_hoi]):
        cau_hoi = "Nội dung có dấu hiệu bí mật đã được ẩn; Đại ca xem lại yêu cầu."
    cau_hoi = " ".join(cau_hoi.split())[:2000]
    beads = bd.tat_ca()
    esc = next((b for b in beads if b.issue_type == "decision" and NHAN in b.labels
                and f"bead_goc: {bead.id}" in b.description.splitlines()
                and f"ly_do: {ly_do}" in b.description.splitlines()
                and (_dau(ma) in b.description.splitlines() or _dau(ma) in b.notes.splitlines())), None)
    if esc is None and (esc := next((b for b in beads if _la_esc_mo(b, bead.id, ly_do)), None)) is not None:
        bd.cap_nhat_nhan(esc.id, ghi_chu=f"[tram/giao-viec] Thêm: {cau_hoi}\n{_dau(ma)}")              # trùng
    esc_id = esc.id if esc else bd.tao(
        f"Bí: {bead.title}"[:200], loai="decision", nhan=[NHAN],
        mo_ta=f"ly_do: {ly_do}\nbead_goc: {bead.id}\ngiao_id: {giao_id or '-'}\n\n{cau_hoi}\n\n{_dau(ma)}")
    goc = next((b for b in beads if b.id == bead.id), bead)
    if esc_id not in [p.depends_on_id for p in goc.phu_thuoc if p.loai == LOAI_CHAN]:
        bd.them_phu_thuoc(bead.id, esc_id)               # bead gốc phụ thuộc escalation → không được giao
    ghi_mot_lan(kho, du_an, "escalation.tao", {"escalation_id": esc_id, "bead_goc": bead.id, "giao_id": giao_id,
                                               "ly_do": ly_do, "ma_thao_tac": ma},
                bead_id=bead.id, luc=luc, khoa=("ma_thao_tac",))
    return esc_id
