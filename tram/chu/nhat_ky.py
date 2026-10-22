"""Ghi thêm an toàn cho journal dạng JSONL (lát 3c, R4 review đợt 5) — dùng cho sổ cài đặt máy thợ.
- `khoa(p)`: flock KHÔNG chờ trên file khoá riêng; bận → `DangBan`.
- `cat_duoi(p)`: GỌI DƯỚI KHOÁ, trước mỗi lần nối. Bytes sau "\\n" cuối (bản ghi dở do crash hay short write, kể cả
  UTF-8 dở) được chép nguyên ra `<p>.duoi-hong` (fsync) rồi cắt khỏi `p` (fsync). Dòng hoàn chỉnh không bao giờ bị sửa.
- `ghi_het(p, du)`: ghi ĐỦ bytes (lặp `os.write` — short write không mất phần còn lại) rồi `F_FULLFSYNC` (macOS:
  `fsync` thường không ép xuống đĩa); file mới tạo thì fsync cả thư mục chứa (và thư mục cha) để tên file bền.
- `dong_hoan_chinh(du)`: các dòng kết thúc bằng "\\n" (bytes); đuôi dở bị bỏ khi đọc, chưa giải mã."""
import fcntl
import os
from contextlib import contextmanager
from pathlib import Path


class DangBan(ValueError):
    """Đã có tiến trình khác giữ khoá journal."""


@contextmanager
def khoa(p: Path, thong_bao: str, *, loi: type[DangBan] = DangBan):
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise loi(thong_bao) from None
        yield
    finally:
        os.close(fd)


def dong_bo(fd: int) -> None:
    try:
        fcntl.fcntl(fd, fcntl.F_FULLFSYNC)
    except (AttributeError, OSError):
        os.fsync(fd)


def _dong_bo_thu_muc(p: Path) -> None:
    for d in (p.parent, p.parent.parent, p.parent.parent.parent):
        fd = os.open(d, os.O_RDONLY)
        try:
            dong_bo(fd)
        finally:
            os.close(fd)


def ghi_het(p: Path, du: bytes) -> None:
    moi = not p.exists()
    fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        while du:
            n = os.write(fd, du)
            if n <= 0:
                raise OSError(f"ghi {p}: os.write trả {n}")
            du = du[n:]
        dong_bo(fd)
    finally:
        os.close(fd)
    if moi:
        _dong_bo_thu_muc(p)


def dong_hoan_chinh(du: bytes) -> list[bytes]:
    return du[:du.rfind(b"\n") + 1].split(b"\n")[:-1]


def cat_duoi(p: Path) -> bytes:
    """Trả đuôi dở đã cắt (b"" nếu không có)."""
    du = p.read_bytes() if p.exists() else b""
    cat = du.rfind(b"\n") + 1
    if cat == len(du):
        return b""
    ghi_het(p.with_name(p.name + ".duoi-hong"), du[cat:] + b"\n")
    fd = os.open(p, os.O_WRONLY)
    try:
        os.ftruncate(fd, cat)
        dong_bo(fd)
    finally:
        os.close(fd)
    return du[cat:]
