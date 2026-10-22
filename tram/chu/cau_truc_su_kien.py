"""Cấu trúc và vân tay của `su-kien.db` (bs-2bd.1.17) — dùng để kiểm bản khôi phục và đối chiếu kho sau khi chép.

`cau_truc`: token CREATE (bỏ chú thích/khoảng trắng ngoài dấu nháy, chỉ hạ chữ token không nháy) — nên CHECK,
UNIQUE, cột và điều kiện WHERE của chỉ mục đều được so —, cột từng bảng (`table_xinfo`), danh sách chỉ mục kể cả
autoindex (unique/origin/partial) và cột từng chỉ mục (`index_xinfo`). `van_tay`: integrity + phiên bản + cấu trúc +
băm toàn bộ dòng mọi bảng theo rowid — hai kho trùng vân tay thì trùng nội dung logic. `bo_nho`: mở byte của một
file SQLite trong bộ nhớ (cờ WAL trong tiêu đề đổi sang nhật ký thường)."""
import hashlib
import re
import sqlite3

from tram.su_kien.phien_ban import phien_ban

_BANG = "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"


def luoc_do() -> str:
    from tram.cong_bo.op import LUOC_DO_OP
    from tram.phieu.luoc_do import LUOC_DO as PHIEU
    from tram.phieu.ma_ghep import LUOC_DO_GHEP
    from tram.su_kien.ket_noi import LUOC_DO as SU_KIEN
    from tram.su_kien.yeu_cau import LUOC_DO as YEU_CAU
    from tram.thao_tac.kho import LUOC_DO as THAO_TAC
    from tram.yeu_cau.so_nhan import LUOC_DO as SO_NHAN
    return SU_KIEN + YEU_CAU + PHIEU + LUOC_DO_GHEP + LUOC_DO_OP + THAO_TAC + SO_NHAN


def _sql(c: str | None) -> tuple[str, ...] | None:
    if c is None:
        return None
    # Chuỗi/định danh có dấu nháy giữ nguyên byte; chỉ bỏ chú thích và hạ chữ ở token ngoài dấu nháy.
    mau = r"\'(?:\'\'|[^\'])*\'|\"(?:\"\"|[^\"])*\"|`(?:``|[^`])*`|\[[^\]]*\]|--[^\n]*|/\*[\s\S]*?\*/|\w+|[^\s]"
    return tuple(t if t[0] in "\'\"`[" else t.lower() for t in re.findall(mau, c)
                 if not t.startswith(("--", "/*")))


def cau_truc(db: sqlite3.Connection) -> list:
    doi = db.execute("SELECT type, name, tbl_name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' "
                     "ORDER BY type, name").fetchall()
    ra = [(t, n, b, _sql(c)) for t, n, b, c in doi]
    for (bang,) in db.execute(_BANG).fetchall():
        ra.append(db.execute("SELECT * FROM pragma_table_xinfo(?)", (bang,)).fetchall())
        cm = sorted(r[1:] for r in db.execute("SELECT * FROM pragma_index_list(?)", (bang,)))
        ra += [cm] + [db.execute("SELECT * FROM pragma_index_xinfo(?)", (r[0],)).fetchall() for r in cm]
    return ra


def van_tay(db: sqlite3.Connection) -> tuple:
    """(integrity, phiên bản, cấu trúc, băm mọi dòng mọi bảng) — hai kho trùng vân tay thì trùng nội dung logic."""
    h = hashlib.sha256()
    for (bang,) in db.execute(_BANG).fetchall():
        h.update(bang.encode() + b"\0")
        for dong in db.execute(f'SELECT * FROM "{bang}" ORDER BY rowid'):
            h.update(repr(dong).encode())
    return db.execute("PRAGMA integrity_check").fetchone()[0], phien_ban(db), cau_truc(db), h.hexdigest()


def bo_nho(du_lieu: bytes) -> sqlite3.Connection:
    anh = bytearray(du_lieu)
    if len(anh) >= 20:
        anh[18] = anh[19] = 1                       # cờ WAL trong tiêu đề: bản trong bộ nhớ dùng nhật ký thường
    db = sqlite3.connect(":memory:", isolation_level=None)
    db.deserialize(bytes(anh))
    return db


def van_tay_anh(du_lieu: bytes) -> tuple:
    db = bo_nho(du_lieu)
    try:
        return van_tay(db)
    finally:
        db.close()
