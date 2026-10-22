"""Làm sạch chuỗi trước khi trả cho trình duyệt (spec 2 §4 mục 4 — bài học ruflo)."""
import unicodedata

LOAI_BO = {"Cc", "Cf", "Cs", "Co"}   # điều khiển, định dạng (bidi, zero-width, soft hyphen), surrogate, dùng riêng
GIU = {"\n", "\t"}


def lam_sach(s: str | None, toi_da: int = 500) -> str:
    if not s:
        return ""
    sach = "".join(c for c in str(s) if c in GIU or unicodedata.category(c) not in LOAI_BO)
    return sach if len(sach) <= toi_da else sach[: toi_da - 1] + "…"


def co_ky_tu_an(s: str) -> bool:
    """Có ký tự điều khiển/định dạng/surrogate/dùng riêng (kể cả xuống dòng) —
    dùng cho chuỗi phải nguyên vẹn như URL."""
    return any(unicodedata.category(c) in LOAI_BO for c in s)
