"""Giao diện cho phần 4 (spec 3 §6.6, §11): công việc chờ xử lý bền sau khi phiếu hết hiệu lực, và quyết toán
ngân sách của từng phiếu. Phần 4 lấy, xử lý, rồi đánh dấu xong; restart giữa chừng thì lấy lại được."""
import json
from dataclasses import dataclass
from datetime import datetime

from tram.phieu.kho import KhoPhieu, chuoi_gio


@dataclass(frozen=True)
class CongViecCho:
    id: int
    giao_id: str
    du_an: str
    bead_id: str
    ket_thuc: str           # 'xong' | 'bi' | 'het_han_muc' | 'thu_hoi'
    su_kien_id: int
    luc: str


def cong_viec_cho(kho: KhoPhieu, gioi_han: int = 50) -> list[CongViecCho]:
    return [CongViecCho(*h) for h in kho.db.execute(
        "SELECT id, giao_id, du_an, bead_id, ket_thuc, su_kien_id, luc FROM cong_viec_cho WHERE xong_luc IS NULL"
        " ORDER BY id LIMIT ?", (gioi_han,))]


def danh_dau_xong_viec(kho: KhoPhieu, id: int, luc: datetime) -> None:
    with kho.giao_dich() as db:
        db.execute("UPDATE cong_viec_cho SET xong_luc = ? WHERE id = ? AND xong_luc IS NULL", (chuoi_gio(luc), id))


def doc_quyet_toan(kho: KhoPhieu, giao_id: str) -> dict | None:
    h = kho.db.execute("SELECT quyet_toan FROM giu_ngan_sach WHERE giao_id = ?", (giao_id,)).fetchone()
    return json.loads(h[0]) if h and h[0] else None
