"""Kiểm danh tính lần chạy trong giao dịch nhận sự kiện (G35), trước khi ghi sự kiện."""
from tram.phieu.kho import KhoPhieu
from tram.phieu.mo_hinh import Phieu


class LanChaySai(ValueError):
    """422: lần chạy ngoài phiếu, lặp bằng request_id mới hoặc kết thúc chưa bắt đầu."""


def kiem_lan_chay(kho: KhoPhieu, p: Phieu, loai: str, d: dict) -> None:
    if loai == "chay.don_rac":
        return
    lan = d["lan"]
    if lan > p.ngan_sach.so_lan_chay:
        raise LanChaySai("Lần chạy vượt ngân sách phiếu")
    bat = kho.db.execute("SELECT 1 FROM lan_chay WHERE giao_id = ? AND lan = ?",
                         (p.giao_id, lan)).fetchone() is not None
    if loai == "chay.bat_dau":
        if bat:
            raise LanChaySai("Lần chạy đã bắt đầu; retry phải giữ request_id")
        return
    xong = kho.db.execute(
        "SELECT 1 FROM su_kien WHERE loai = 'chay.xong'"
        " AND json_extract(du_lieu, '$.giao_id') = ? AND json_extract(du_lieu, '$.lan') = ?",
        (p.giao_id, lan)).fetchone() is not None
    if not bat or xong:
        raise LanChaySai("Lần chạy chưa bắt đầu hoặc đã kết thúc")
