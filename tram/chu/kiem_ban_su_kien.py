"""Đọc và kiểm bản khôi phục `su-kien.db` (bs-2bd.1.17, bước 1–2 của `khoi_phuc_su_kien`).

Đọc QUA FD vào BỘ NHỚ (thư mục mở theo chuỗi cha được tin, file `O_NOFOLLOW`; file `.db` thường, một liên kết cứng,
khác inode kho). `ban_ap` dựng ĐÚNG bản sẽ được chép vào kho rồi kiểm chính bản đó: `integrity_check`; phiên bản ≤ mã;
bản GỐC phải có sẵn bảng tối thiểu (`TOI_THIEU`) — SQLite hợp lệ mà rỗng thì từ chối; nâng lên `PHIEN_BAN` và tạo các
bảng còn thiếu bằng `LUOC_DO` (IF NOT EXISTS — đúng việc mã làm khi mở kho); rồi so CẤU TRÚC với kho mới tinh của mã:
`cau_truc_su_kien.cau_truc` (câu CREATE chuẩn hoá — CHECK, UNIQUE, cột và WHERE của chỉ mục —, cột từng bảng, chỉ mục
kể cả autoindex) — phải trùng khớp. Thông báo lỗi không chép đường dẫn."""
import os
import sqlite3
import stat
from pathlib import Path

from tram.chu.cau_truc_su_kien import bo_nho, cau_truc, luoc_do
from tram.su_kien import thu_muc_an_toan
from tram.su_kien.phien_ban import PHIEN_BAN, ap_buoc, phien_ban

_DOC = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
TOI_THIEU = ("su_kien",)


class LoiKhoiPhuc(RuntimeError):
    pass


def doc_ban(ten: str, thu_muc: Path, kho: Path) -> bytes:
    """Byte của bản `ten` (đã kiểm định danh) trong `thu_muc`; bản lạ → `LoiKhoiPhuc`."""
    if "/" in ten or not ten.endswith(".db"):
        raise LoiKhoiPhuc("Bản khôi phục phải là tên file .db nằm thẳng trong ~/.tram/sao-luu")
    try:
        dfd, _ = thu_muc_an_toan.mo_thu_muc(thu_muc)
        try:
            fd = os.open(ten, _DOC, dir_fd=dfd)
        finally:
            os.close(dfd)
        with open(fd, "rb") as f:
            st, khac = os.fstat(fd), os.stat(kho) if kho.exists() else None
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or (khac and khac.st_ino == st.st_ino):
                raise LoiKhoiPhuc("Bản khôi phục phải là file thường riêng (không liên kết, không phải chính kho)")
            return f.read()
    except (OSError, thu_muc_an_toan.LoiDuongDan):
        raise LoiKhoiPhuc("Không mở được bản khôi phục (không có, là liên kết mềm, hay thư mục sao lưu lạ)") from None


def ban_ap(du_lieu: bytes) -> sqlite3.Connection:
    """Bản trong bộ nhớ ĐÚNG như sẽ chép vào kho, đã kiểm; người gọi đóng. Hỏng/lạ/sai cấu trúc → `LoiKhoiPhuc`."""
    mau, db = sqlite3.connect(":memory:"), None
    try:
        db = bo_nho(du_lieu)
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise LoiKhoiPhuc("Bản khôi phục hỏng (integrity_check)")
        v = phien_ban(db)
        if v > PHIEN_BAN:
            raise LoiKhoiPhuc(f"Bản khôi phục ở phiên bản cấu trúc {v}, mã này chỉ hiểu tới {PHIEN_BAN}")
        if not set(TOI_THIEU) <= {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}:
            raise LoiKhoiPhuc("Bản khôi phục không đúng cấu trúc kho sự kiện (thiếu bảng tối thiểu) — không dùng")
        ap_buoc(db)
        db.executescript(luoc_do())
        mau.executescript(luoc_do())
        if cau_truc(db) != cau_truc(mau) or db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise LoiKhoiPhuc("Bản khôi phục không đúng cấu trúc kho sự kiện mà mã này hiểu — không dùng")
        return db
    except BaseException as e:
        if db is not None:
            db.close()
        if isinstance(e, sqlite3.Error):
            raise LoiKhoiPhuc("Bản khôi phục không đọc được như SQLite") from None
        raise
    finally:
        mau.close()


def kiem_ban(du_lieu: bytes) -> None:
    """Xem trước ở CLI: bản không dùng được → `LoiKhoiPhuc`."""
    ban_ap(du_lieu).close()
