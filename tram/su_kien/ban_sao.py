"""Bản sao SQLite an toàn (bs-2bd.1.3, dùng lại ở .1.4 và .1.17): chụp CÓ HẠN rồi ghi ĐỘC QUYỀN, quyền 600 từ đầu.

`chup`: online backup của SQLite vào bộ nhớ, từng `SO_TRANG` trang; sau mỗi bước kiểm hạn (đồng hồ thay được trong
test) — quá hạn (kho bận mãi, đĩa chậm, bị ghi liên tục làm backup chạy lại) → `LoiBanSao`, không để lại gì.
`ghi_doc_quyen`: mở thư mục đích bằng fd theo chuỗi cha được tin (`thu_muc_an_toan`: không liên kết mềm ở thành phần
nào trừ liên kết hệ thống, không thư mục người khác sửa được; tạo 700 nếu chưa có; của người khác → từ chối; rộng
quyền → `fchmod` 700), rồi tạo file bằng `O_CREAT|O_EXCL|O_NOFOLLOW` (600) TƯƠNG ĐỐI fd thư mục: không đi theo liên
kết mềm, không ghi đè file/liên kết có sẵn (trùng tên → thêm `-2`, `-3`…), không có lúc nào file rộng quyền. Ghi lỗi
giữa chừng → xoá file dở. Thông báo lỗi không chép đường dẫn."""
import os
import sqlite3
import stat
import time
from collections.abc import Callable
from pathlib import Path

from tram.su_kien import thu_muc_an_toan

HAN_SAO_LUU_GIAY = 60.0
SO_TRANG = 256
_TAO = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW


class LoiBanSao(RuntimeError):
    pass


def chup(db: sqlite3.Connection, *, han: float | None = None, so_trang: int = SO_TRANG,
         dong_ho: Callable[[], float] = time.monotonic) -> bytes:
    """Ảnh nhất quán của `db` dưới dạng byte của một file SQLite."""
    het = dong_ho() + (HAN_SAO_LUU_GIAY if han is None else han)

    def tien_do(trang_thai: int, con_lai: int, tong: int) -> None:
        if dong_ho() > het:
            raise LoiBanSao("sao lưu SQLite quá hạn — bỏ, không ghi bản nào")
    mem = sqlite3.connect(":memory:")
    try:
        db.backup(mem, pages=so_trang, progress=tien_do)
        return mem.serialize()
    except sqlite3.Error:
        raise LoiBanSao("sao lưu SQLite lỗi — không ghi bản nào") from None
    finally:
        mem.close()


def mo_thu_muc(thu_muc: Path) -> int:
    """fd của thư mục 700 thuộc người chạy (tạo nếu chưa có), mở theo chuỗi cha được tin (`thu_muc_an_toan`): liên
    kết mềm ở BẤT KỲ thành phần nào (trừ liên kết hệ thống của root), thư mục người khác sửa được trên đường, không phải
    thư mục, của người khác → `LoiBanSao`. Thành phần thiếu tạo 700 tương đối fd cha. Người gọi đóng fd."""
    try:
        fd, _ = thu_muc_an_toan.mo_thu_muc(thu_muc, tao=True)
    except thu_muc_an_toan.LoiDuongDan as e:
        raise LoiBanSao(f"thư mục sao lưu không dùng được: {e} — không ghi") from None
    st = os.fstat(fd)
    if st.st_uid != os.getuid():
        os.close(fd)
        raise LoiBanSao("thư mục sao lưu không thuộc tài khoản này — không ghi")
    if stat.S_IMODE(st.st_mode) != 0o700:
        os.fchmod(fd, 0o700)
    return fd


def ghi_doc_quyen(thu_muc: Path, ten_goc: str, du_lieu: bytes, *, duoi: str = ".db") -> Path:
    """Ghi `<ten_goc><duoi>` (đã có thì `<ten_goc>-2<duoi>`…) trong `thu_muc`; trả đường file vừa tạo."""
    dfd = mo_thu_muc(thu_muc)
    try:
        for i in range(1, 100):
            ten = f"{ten_goc}{duoi}" if i == 1 else f"{ten_goc}-{i}{duoi}"
            try:
                fd = os.open(ten, _TAO, 0o600, dir_fd=dfd)
            except FileExistsError:
                continue
            with os.fdopen(fd, "wb") as f:
                try:
                    os.fchmod(f.fileno(), 0o600)
                    f.write(du_lieu)
                    f.flush()
                    os.fsync(f.fileno())
                except BaseException:
                    os.unlink(ten, dir_fd=dfd)
                    raise
            return thu_muc / ten
        raise LoiBanSao("quá nhiều bản sao trùng tên — không ghi")
    finally:
        os.close(dfd)
