"""Lỗi của lớp `bd` (bs-2bd.1.20: dời khỏi `bd.py` để `doc_ds.py` dùng mà không vòng import)."""


class LoiBd(RuntimeError):
    pass


class KhongThayBead(LoiBd):
    """Bead không có trong `bd list` của dự án."""
