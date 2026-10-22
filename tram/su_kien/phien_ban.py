"""Số phiên bản cấu trúc của `~/.tram/su-kien.db` (bs-2bd.1.3) — `PRAGMA user_version`.

v0 = kho viết trước lát này. v1 = cấu trúc hiện hành (các bảng do `LUOC_DO` từng module tạo, `IF NOT EXISTS`): bước
0→1 không đổi bảng, chỉ đóng dấu (đã đối chiếu git: chưa bảng nào đổi cột kể từ lúc tạo). Từ v2, mỗi lần đổi cấu
trúc là MỘT mục `BUOC[v]` (câu SQL rời — không `executescript`, nó tự COMMIT) và tăng `PHIEN_BAN`.

Nhiều tiến trình cùng mở kho (điều phối): đọc nhanh không khoá — bằng mã thì xong, mới hơn mã thì từ chối, không ghi.
Còn lại: `BEGIN IMMEDIATE` (khoá ghi; kho bận quá busy_timeout của kết nối → `LoiPhienBan`, chưa đổi gì) → ĐỌC LẠI
trong khoá (người khác vừa nâng: bằng → thôi, không sao lưu; cao hơn mã → từ chối) → chụp bản trước nâng qua MỘT kết
nối đọc thứ hai NGAY TRONG KHOÁ (không ai ghi chen; chụp có hạn — `ban_sao.chup`) → ghi bản độc quyền 600
(`truoc-nang-v<cũ>-v<mới>-<lúc>.db`) → áp bước → `user_version` → COMMIT. Lỗi ở bất kỳ bước nào → ROLLBACK, kho y
nguyên, `LoiPhienBan`; bản sao đã ghi xong được giữ (đúng là kho trước nâng). Người ghi khác chờ trong lúc nâng.
Đường lui khi quay về mã cũ: khôi phục bản `truoc-nang-*` bằng `tram chu khoi-phuc-su-kien`. Thông báo lỗi không chép
đường dẫn hay câu SQL."""
import sqlite3
from collections.abc import Callable
from pathlib import Path

from tram.duong_dan import bay_gio
from tram.su_kien import ban_sao

PHIEN_BAN = 1
BUOC: dict[int, tuple[str, ...]] = {1: ()}       # v0 → v1: đóng dấu cấu trúc hiện hành


class LoiPhienBan(RuntimeError):
    pass


def phien_ban(db: sqlite3.Connection) -> int:
    return db.execute("PRAGMA user_version").fetchone()[0]


def _kiem(cu: int, moi: int, buoc: dict[int, tuple[str, ...]]) -> None:
    if cu > moi:
        raise LoiPhienBan(f"su-kien.db ở phiên bản cấu trúc {cu}, mã này chỉ hiểu tới {moi} — không mở")
    if any(v not in buoc for v in range(cu + 1, moi + 1)):
        raise LoiPhienBan(f"thiếu bước nâng cấu trúc từ {cu} lên {moi}")


def ap_buoc(db: sqlite3.Connection, *, buoc: dict[int, tuple[str, ...]] = BUOC, moi: int = PHIEN_BAN) -> None:
    """Trong giao dịch người gọi đang mở: áp các bước từ phiên bản hiện tại lên `moi` (khôi phục dùng để kiểm bản)."""
    cu = phien_ban(db)
    _kiem(cu, moi, buoc)
    for v in range(cu + 1, moi + 1):
        for cau in buoc[v]:
            db.execute(cau)
    if cu < moi:
        db.execute(f"PRAGMA user_version = {int(moi)}")


def _chup_tu_ket_noi_khac(db: sqlite3.Connection, chup: Callable[[sqlite3.Connection], bytes]) -> bytes:
    """Kết nối đang giữ khoá ghi không backup được chính nó (SQLite trả BUSY mãi) — đọc qua kết nối thứ hai."""
    src = sqlite3.connect(db.execute("PRAGMA database_list").fetchone()[2])
    try:
        return chup(src)
    finally:
        src.close()


def _hoan_tac(db: sqlite3.Connection) -> None:
    if db.in_transaction:                            # vài lỗi SQLite đã tự ROLLBACK
        db.execute("ROLLBACK")


def nang_cap(db: sqlite3.Connection, *, thu_muc_sao_luu: Path, buoc: dict[int, tuple[str, ...]] = BUOC,
             moi: int = PHIEN_BAN, luc: str | None = None, chup=ban_sao.chup) -> Path | None:
    """Đưa kho lên `moi`. Trả đường bản sao lưu vừa tạo (None: không cần nâng, kho rỗng, hay người khác vừa nâng)."""
    cu = phien_ban(db)
    _kiem(cu, moi, buoc)
    if cu == moi:
        return None
    try:
        db.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError:
        raise LoiPhienBan("su-kien.db đang bị tiến trình khác khoá ghi — chưa nâng cấu trúc, thử lại sau") from None
    ban = None
    try:
        cu = phien_ban(db)                           # trong khoá: tiến trình khác có thể vừa nâng xong
        _kiem(cu, moi, buoc)
        if cu < moi and db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' LIMIT 1").fetchone():
            nhan = (luc or bay_gio()).replace("-", "").replace(":", "")
            ban = ban_sao.ghi_doc_quyen(thu_muc_sao_luu, f"truoc-nang-v{cu}-v{moi}-{nhan}",
                                        _chup_tu_ket_noi_khac(db, chup))
        ap_buoc(db, buoc=buoc, moi=moi)
        db.execute("COMMIT")
    except LoiPhienBan:
        _hoan_tac(db)
        raise
    except (sqlite3.Error, ban_sao.LoiBanSao, OSError):
        _hoan_tac(db)
        raise LoiPhienBan(f"nâng cấu trúc su-kien.db lên {moi} lỗi — đã hoàn tác, kho giữ nguyên") from None
    return ban
