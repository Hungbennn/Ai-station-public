"""Ghi một sự kiện TRONG giao dịch của người gọi (không tự commit) — để cấp/kết thúc phiếu, sự kiện, yêu cầu chấm lại
và công việc chờ nằm chung MỘT giao dịch SQLite (spec 3 §6.6). Cùng cột, cùng cách mã hoá như `KhoSuKien.ghi`."""
import json
import sqlite3


def ghi_trong_giao_dich(db: sqlite3.Connection, du_an: str, loai: str, du_lieu: dict, *, bead_id: str | None = None,
                        tac_nhan: str, luc: str, token_vao: int | None = None, token_ra: int | None = None,
                        mo_hinh: str | None = None, thoi_gian_ms: int | None = None) -> int:
    cur = db.execute(
        "INSERT INTO su_kien (luc, du_an, bead_id, loai, tac_nhan, du_lieu, token_vao, token_ra, mo_hinh,"
        " thoi_gian_ms) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (luc, du_an, bead_id, loai, tac_nhan, json.dumps(du_lieu, ensure_ascii=False, sort_keys=True),
         token_vao, token_ra, mo_hinh, thoi_gian_ms))
    return cur.lastrowid
