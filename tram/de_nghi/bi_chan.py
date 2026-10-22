"""Bị chặn = báo bí / cần hỏi sẵn có (design D-6, D102): escalation (điểm dừng #3) LUÔN tạo như hôm nay; nút con "bị
chặn" chỉ quyết (1) lý do của agent được LỌC trước khi vào escalation (thay / cắt — Scenario "Lý do bị chặn có bí
mật") và (2) vòng tick thêm dòng "bị chặn" vào chính việc đó. Nút tắt → lý do vào escalation như hôm nay (lỗ chung
"lý do bí chưa quét bí mật" sửa riêng ở bead `bs-2bd.1.27`, D111)."""
import sqlite3

from tram.de_nghi.cai_dat import doc_cai_dat
from tram.de_nghi.loc import ly_do_bi_chan
from tram.giao_viec.escalation import LY_DO_BI, LY_DO_HOI, ma_escalation

LY_DO_AGENT = ("agent-bi", "agent-can-hoi", "can-thao-tac-nguy-hiem")


def cau_hoi_esc(db: sqlite3.Connection, du_an: str, ly_do_esc: str, noi_dung: str) -> str:
    if ly_do_esc in LY_DO_AGENT and doc_cai_dat(db, du_an)[0].cho_ghi("bi_chan"):
        return ly_do_bi_chan(noi_dung)
    return noi_dung


def ma_escalation_cua(du_an: str, bead_id: str, loai_bao: str, su_kien_id: int, du_lieu: dict) -> str:
    """Mã thao tác của escalation mà luồng sẵn có (`xu_ly_viec`) tạo cho báo này — để tìm `escalation.tao`."""
    if loai_bao == "bao.bi":
        return ma_escalation(du_an, bead_id, LY_DO_BI["agent"], du_lieu["giao_id"])
    return ma_escalation(du_an, bead_id, LY_DO_HOI.get(du_lieu.get("loai_hoi"), "agent-can-hoi"), f"hoi-{su_kien_id}")
