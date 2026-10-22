"""Thư mục và khoá tiến trình của memory service (spec 1b §9: chỉ MỘT tiến trình mở kho — M7a)."""
import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from tram.duong_dan import tram_home


def thu_muc_nho() -> Path:
    p = tram_home() / "nho"
    p.mkdir(parents=True, exist_ok=True)
    return p


@contextmanager
def khoa_dich_vu(thu_muc: Path) -> Iterator[bool]:
    """flock `<thu_muc>/.khoa`: True nếu giữ được; False khi bản khác đang chạy (không chờ)."""
    thu_muc.mkdir(parents=True, exist_ok=True)
    with open(thu_muc / ".khoa", "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
