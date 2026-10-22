"""Kết nối SQLite dùng chung cho mọi tiến trình trạm (quét, tram-api, tram-bao-tin) — spec 2 §12.2."""
import sqlite3
import time
from pathlib import Path

from tram.su_kien.mo_an_toan import LoiQuyenKho, chi_chu, mo_da_kiem  # noqa: F401 — bs-2bd.1.4, giữ đường import

THOI_GIAN_CHO_GIAY = 10
LUOC_DO = """
CREATE TABLE IF NOT EXISTS su_kien (
  id INTEGER PRIMARY KEY,
  luc TEXT NOT NULL,
  du_an TEXT NOT NULL,
  bead_id TEXT,
  loai TEXT NOT NULL,
  tac_nhan TEXT NOT NULL,
  du_lieu TEXT NOT NULL,
  token_vao INTEGER, token_ra INTEGER,
  mo_hinh TEXT,
  thoi_gian_ms INTEGER
);
CREATE INDEX IF NOT EXISTS su_kien_bead ON su_kien(du_an, bead_id, loai, id);
CREATE TABLE IF NOT EXISTS moc_quet (du_an TEXT PRIMARY KEY, updated_at TEXT NOT NULL);
"""


def mo_ket_noi(duong_dan: Path) -> sqlite3.Connection:
    """WAL: người đọc không chặn người ghi; busy_timeout: người ghi chờ nhau thay vì lỗi ngay.
    check_same_thread=False: tram-api dùng một kết nối qua threadpool, mỗi lúc một luồng.
    Chuyển sang WAL cần khoá độc quyền — hai tiến trình cùng mở DB mới lần đầu có thể đụng nhau, nên thử lại."""
    db = mo_da_kiem(duong_dan, timeout=THOI_GIAN_CHO_GIAY, check_same_thread=False)
    db.execute(f"PRAGMA busy_timeout={THOI_GIAN_CHO_GIAY * 1000}")
    so_lan = THOI_GIAN_CHO_GIAY * 10
    for lan in range(so_lan):
        try:
            db.execute("PRAGMA journal_mode=WAL")
            break
        except sqlite3.OperationalError:
            if lan == so_lan - 1:
                raise
            time.sleep(0.1)
    return db


def mo_kho_su_kien(duong_dan: Path) -> sqlite3.Connection:
    """Mở `su-kien.db` (mọi kho dùng chung file này): như `mo_ket_noi` + kiểm/nâng phiên bản cấu trúc (bs-2bd.1.3).
    Bản sao lưu trước khi nâng nằm ở `sao-luu/` cạnh kho. Kho mới hơn mã → `LoiPhienBan`, không mở."""
    from tram.su_kien.phien_ban import nang_cap
    db = mo_ket_noi(duong_dan)
    try:
        nang_cap(db, thu_muc_sao_luu=duong_dan.parent / "sao-luu")
    except BaseException:
        db.close()
        raise
    return db
