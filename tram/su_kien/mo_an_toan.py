"""Mở kho SQLite giữ định danh tới lúc SQLite dùng (bs-2bd.1.4) — `ket_noi.mo_ket_noi` và khôi phục (bs-2bd.1.17).

`chi_chu` (TRƯỚC khi SQLite mở): thư mục chứa kho theo chuỗi cha được tin (`thu_muc_an_toan`), thuộc người chạy; kho,
`-wal`, `-shm` mở tương đối fd đó — liên kết mềm/cứng, khác chủ, không phải file thường → từ chối trước khi chmod/ghi;
tạo kho 600; siết 600 trên fd. `mo_da_kiem`: `sqlite3.connect` theo đường CHUẨN rồi đối chiếu lại định danh thư mục
cha và file kho trước câu lệnh đầu tiên. Thông báo lỗi không chép đường dẫn."""
import os
import sqlite3
import stat
from pathlib import Path

from tram.su_kien import thu_muc_an_toan


class LoiQuyenKho(RuntimeError):
    pass


_TEP = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK


def _dd(st: os.stat_result) -> tuple[int, int]:
    return st.st_dev, st.st_ino


def _mo(ten: str, dfd: int, tao: bool) -> int | None:
    """fd mở `O_NOFOLLOW` tương đối `dfd`; None khi không có. Đo 18/10 trên macOS: nhiều luồng/tiến trình cùng
    `O_CREAT|O_NOFOLLOW` một tên mới có thể nhận ENOENT (185/200 lần với hai luồng) — tạo thì thử lại."""
    for _ in range(10 if tao else 1):
        try:
            return os.open(ten, _TEP | (os.O_CREAT if tao else 0), 0o600, dir_fd=dfd)
        except FileNotFoundError:
            continue
        except OSError:
            raise LoiQuyenKho("kho SQLite là liên kết mềm hoặc không mở được — không mở") from None
    if tao:
        raise LoiQuyenKho("không tạo được kho SQLite — không mở")
    return None


def chi_chu(duong_dan: Path) -> tuple[str, tuple[int, int], tuple[int, int]]:
    """bs-2bd.1.4, TRƯỚC khi SQLite mở. Thư mục chứa kho mở theo chuỗi cha được tin (`thu_muc_an_toan`) và phải thuộc
    người chạy; kho/-wal/-shm mở TƯƠNG ĐỐI fd đó (`O_NOFOLLOW`): liên kết mềm, không phải file thường, khác chủ, có liên
    kết cứng → `LoiQuyenKho` TRƯỚC khi chmod/ghi gì. Kho chưa có → tạo 600 (SQLite tạo -wal/-shm theo quyền file kho);
    rộng quyền → `fchmod` 600 trên fd. Trả (đường chuẩn, định danh thư mục cha, định danh file kho) cho `mo_da_kiem`."""
    try:
        dfd, cha = thu_muc_an_toan.mo_thu_muc(duong_dan.parent)
    except thu_muc_an_toan.LoiDuongDan as e:
        raise LoiQuyenKho(f"thư mục chứa kho SQLite không dùng được: {e} — không mở") from None
    try:
        st_cha, dd_kho = os.fstat(dfd), (0, 0)
        if st_cha.st_uid != os.getuid():
            raise LoiQuyenKho("thư mục chứa kho SQLite không thuộc tài khoản này — không mở")
        for duoi in ("", "-wal", "-shm"):
            fd = _mo(duong_dan.name + duoi, dfd, not duoi)
            if fd is None:
                continue
            try:
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid():
                    raise LoiQuyenKho("kho SQLite không phải file thường của tài khoản này — không mở")
                if st.st_nlink > 1:                  # 0: -wal/-shm vừa bị kết nối khác đóng xoá — không phải liên kết
                    raise LoiQuyenKho("kho SQLite có liên kết cứng — không đổi quyền, không mở")
                if stat.S_IMODE(st.st_mode) & 0o077:
                    os.fchmod(fd, 0o600)
                dd_kho = dd_kho if duoi else _dd(st)
            finally:
                os.close(fd)
        return os.path.join(cha, duong_dan.name), _dd(st_cha), dd_kho
    finally:
        os.close(dfd)


def mo_da_kiem(duong_dan: Path, **kw) -> sqlite3.Connection:
    """`chi_chu` → `sqlite3.connect` theo đường CHUẨN (SQLite chỉ nhận tên; nó mở file ngay lúc connect) → đối chiếu
    lại: thư mục cha và file kho theo tên vẫn đúng định danh đã kiểm. Lệch → đóng, `LoiQuyenKho`, chưa chạy câu lệnh
    nào. Chuỗi cha chỉ root/người chạy sửa được, nên ngoài khoảng đối chiếu chỉ chính họ thay được kho."""
    duong, dd_cha, dd_kho = chi_chu(duong_dan)
    db = sqlite3.connect(duong, **kw)
    try:
        lech = _dd(os.stat(os.path.dirname(duong))) != dd_cha or _dd(os.stat(duong, follow_symlinks=False)) != dd_kho
    except OSError:
        lech = True
    if lech:
        db.close()
        raise LoiQuyenKho("kho SQLite bị thay giữa lúc kiểm và lúc mở — không dùng")
    return db
