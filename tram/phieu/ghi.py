"""Thao tác ghi mức thấp của kho phiếu — CHỈ gọi bên trong `KhoPhieu.giao_dich()` (spec 3 §6.6)."""
import sqlite3
from datetime import datetime

from tram.phieu.kho import chuoi_gio
from tram.phieu.mo_hinh import Phieu


def giao_id_moi(db: sqlite3.Connection, luc: datetime) -> str:
    """`g-<YYYYMMDD>-<số tăng dần trong ngày>` — đoán được, KHÔNG dùng làm bằng chứng quyền (§4)."""
    ngay = f"{luc:%Y%m%d}"
    db.execute("INSERT INTO so_giao (ngay, so) VALUES (?, 1) ON CONFLICT(ngay) DO UPDATE SET so = so + 1", (ngay,))
    so = db.execute("SELECT so FROM so_giao WHERE ngay = ?", (ngay,)).fetchone()[0]
    return f"g-{ngay}-{so:04d}"


def tang_luot(db: sqlite3.Connection, du_an: str, bead_id: str) -> int:
    """`luot`: bộ đếm theo bead, bắt đầu 1, tăng mỗi lần phát phiếu cho bead (bất kỳ bước, bất kỳ khe)."""
    db.execute("INSERT INTO luot_bead (du_an, bead_id, luot) VALUES (?, ?, 1)"
               " ON CONFLICT(du_an, bead_id) DO UPDATE SET luot = luot + 1", (du_an, bead_id))
    return db.execute("SELECT luot FROM luot_bead WHERE du_an = ? AND bead_id = ?", (du_an, bead_id)).fetchone()[0]


def them_phieu(db: sqlite3.Connection, p: Phieu, *, may_id: str, cap_luc: datetime) -> None:
    """Lưu phiếu đầy đủ (gồm `ma_giao`) + bản ghi giữ trước ngân sách gắn phiếu."""
    db.execute("INSERT INTO phieu (giao_id, du_an, bead_id, khe_id, may_id, luot, khoa_chong_trung, noi_dung,"
               " trang_thai, han_giu, cap_luc) VALUES (?,?,?,?,?,?,?,?,'hieu_luc',?,?)",
               (p.giao_id, p.du_an, p.bead_id, p.khe_id, may_id, p.luot, p.khoa_chong_trung, p.model_dump_json(),
                p.han_giu, chuoi_gio(cap_luc)))
    ns = p.ngan_sach
    db.execute("INSERT INTO giu_ngan_sach (giao_id, so_lan_chay, phut, token_ra) VALUES (?,?,?,?)",
               (p.giao_id, ns.so_lan_chay, ns.phut, ns.token_ra))


def gia_han(db: sqlite3.Connection, giao_id: str, *, han_giu: datetime, nhip: datetime) -> None:
    db.execute("UPDATE phieu SET han_giu = ?, nhip_cuoi = ? WHERE giao_id = ? AND trang_thai = 'hieu_luc'",
               (chuoi_gio(han_giu), chuoi_gio(nhip), giao_id))


def dat_dung_mem(db: sqlite3.Connection, giao_id: str, ly_do: str) -> None:
    db.execute("UPDATE phieu SET dung_mem = ? WHERE giao_id = ? AND trang_thai = 'hieu_luc'", (ly_do, giao_id))


def danh_dau_ket_thuc(db: sqlite3.Connection, giao_id: str, ket_thuc: str, luc: datetime) -> None:
    cur = db.execute("UPDATE phieu SET trang_thai = 'ket_thuc', ket_thuc = ?, ket_thuc_luc = ?"
                     " WHERE giao_id = ? AND trang_thai = 'hieu_luc'", (ket_thuc, chuoi_gio(luc), giao_id))
    if cur.rowcount != 1:
        raise ValueError(f"Phiếu {giao_id} không còn hiệu lực")
