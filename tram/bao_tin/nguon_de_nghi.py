"""Nguồn tin của "agent tự cập nhật việc" (spec cong-tac-de-nghi-viec, design D-9, D86). Chỉ `de_nghi.dot_ghi` (trạm
ghi xong cả đợt việc mới của MỘT lần vào cột 3) sinh tin: một tin gộp `viec_moi_agent` — tên dự án, số việc, mã việc,
link; KHÔNG tiêu đề, mô tả hay chữ nào của agent. Tiến độ không bao giờ có tin; "bị chặn" dùng tin escalation sẵn có
(một tin mỗi lần báo) — không thêm tin thứ hai."""
from tram.bao_tin.tin import ID_AN_TOAN, Tin

TIEN_TO = "de_nghi."


def tin_de_nghi(sk) -> list[Tin]:
    if sk.loai != "de_nghi.dot_ghi":
        return []
    moi = [m for m in sk.du_lieu.get("bead_moi") or [] if isinstance(m, str) and ID_AN_TOAN.fullmatch(m)]
    return [Tin("viec_moi_agent", sk.du_an, m) for m in moi]
