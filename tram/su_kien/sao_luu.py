"""Sao lưu ~/.tram/su-kien.db bằng online backup của SQLite (cùng API với lệnh `.backup`) — spec 2 §12.2.
bs-2bd.1.4: chụp có hạn, ghi bản độc quyền 600 trong thư mục 700 (`ban_sao`) — không lúc nào bản sao rộng quyền."""
import sqlite3
from pathlib import Path

from tram.duong_dan import bay_gio
from tram.su_kien import ban_sao


def sao_luu(nguon: Path, thu_muc: Path, *, giu: int = 14, luc: str | None = None) -> Path:
    if giu < 1:
        raise ValueError("giu phải ≥ 1")
    if not nguon.is_file():
        raise FileNotFoundError(f"Không thấy {nguon}")
    nhan = (luc or bay_gio()).replace("-", "").replace(":", "")
    src = sqlite3.connect(nguon)
    try:
        du_lieu = ban_sao.chup(src)
    finally:
        src.close()
    dich = ban_sao.ghi_doc_quyen(thu_muc, f"su-kien-{nhan}", du_lieu)
    for cu in sorted(thu_muc.glob("su-kien-*.db"))[:-giu]:
        cu.unlink()
    return dich
