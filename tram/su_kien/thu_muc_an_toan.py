"""Mở thư mục theo CHUỖI CHA ĐƯỢC TIN (bs-2bd.1.3, .1.4) — dùng cho bản sao lưu (`ban_sao`) và kho SQLite (`ket_noi`).

Đi từ `/` xuống: mỗi thành phần mở bằng fd TƯƠNG ĐỐI fd cha (`O_NOFOLLOW|O_DIRECTORY`), đối chiếu (dev, inode) với
lstat vừa đọc; mỗi thư mục trên chuỗi chỉ root hoặc người chạy sửa được (chủ là root/người chạy; nhóm/người khác ghi
được thì chỉ chấp nhận thư mục sticky của root). Liên kết mềm trên đường chỉ đi theo khi do root tạo trong thư mục của
root mà người khác không ghi được (`/var`, `/tmp` của macOS); liên kết người dùng tạo → `LoiDuongDan`. `tao=True`:
thành phần thiếu được tạo 700 tương đối fd cha. Kết quả: fd thư mục đích + đường CHUẨN (không còn liên kết) — người
khác không thay được thành phần nào trên đường đó, nên mở lại theo tên (SQLite chỉ nhận tên) vẫn trúng thư mục đã
kiểm, trừ khi chính root/người chạy thay. Thông báo lỗi không chép đường dẫn."""
import os
import stat
from pathlib import Path

_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
LIEN_KET_TOI_DA = 16


class LoiDuongDan(RuntimeError):
    pass


def tin_duoc(st: os.stat_result) -> bool:
    """Chỉ root hoặc người chạy đổi được nội dung thư mục này."""
    if st.st_uid not in (0, os.getuid()):
        return False
    return not st.st_mode & 0o022 or bool(st.st_mode & stat.S_ISVTX and st.st_uid == 0)


def _lien_ket_he_thong(ls: os.stat_result, cha: os.stat_result) -> bool:
    return ls.st_uid == 0 and cha.st_uid == 0 and not cha.st_mode & 0o022


def mo_thu_muc(p: Path, *, tao: bool = False) -> tuple[int, str]:
    """(fd, đường chuẩn) của thư mục `p`. Người gọi đóng fd. Chuỗi cha không tin được → `LoiDuongDan`."""
    phan, lan = list(Path(os.path.abspath(p)).parts[1:]), 0
    fd, duong = os.open("/", _DIR), "/"
    try:
        if not tin_duoc(os.fstat(fd)):
            raise LoiDuongDan("thư mục gốc không tin được")
        while phan:
            ten = phan.pop(0)
            try:
                ls = os.stat(ten, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                if not tao:
                    raise
                os.mkdir(ten, 0o700, dir_fd=fd)
                ls = os.stat(ten, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISLNK(ls.st_mode):
                lan += 1
                if lan > LIEN_KET_TOI_DA or not _lien_ket_he_thong(ls, os.fstat(fd)):
                    raise LoiDuongDan("đường có liên kết mềm không do hệ thống tạo — không đi theo")
                moi = os.path.normpath(os.path.join(duong, os.readlink(ten, dir_fd=fd)))
                phan = list(Path(moi).parts[1:]) + phan
                os.close(fd)
                fd, duong = os.open("/", _DIR), "/"
                continue
            con = os.open(ten, _DIR, dir_fd=fd)
            os.close(fd)
            fd, duong = con, os.path.join(duong, ten)
            st = os.fstat(fd)
            if (st.st_dev, st.st_ino) != (ls.st_dev, ls.st_ino) or not tin_duoc(st):
                raise LoiDuongDan("thư mục trên đường bị đổi giữa chừng hoặc người khác sửa được — không dùng")
        return fd, duong
    except LoiDuongDan:
        os.close(fd)
        raise
    except OSError:
        os.close(fd)
        raise LoiDuongDan("không mở được thư mục trên đường (không có, không phải thư mục, hay liên kết)") from None
