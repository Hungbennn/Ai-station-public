"""Phạm vi ký ức và vùng cấp (spec 1b §4): so khớp chính xác, cấm so tiền tố chuỗi."""
import re
from collections.abc import Iterable, Sequence

TEN = r"[a-z0-9-]+"
NHANH = ("nghiep-vu", "cach-lam")
NHOM_MAC_DINH = {"du-an": 3, "vai": 1, "chung": 1}
_PHAM_VI = re.compile(rf"/du-an/{TEN}/(nghiep-vu|cach-lam)|/vai/{TEN}|/chung")
_VUNG = re.compile(rf"/du-an/{TEN}(/(nghiep-vu|cach-lam))?|/vai/{TEN}|/chung")
_TEN = re.compile(TEN)


class LoiVungCap(ValueError):
    """Vùng cấp thiếu, rỗng hoặc sai dạng — từ chối cả lời gọi (M2)."""


def la_pham_vi(s: object) -> bool:
    return isinstance(s, str) and _PHAM_VI.fullmatch(s) is not None


def mo_rong(vung_cap: Sequence[str] | None) -> frozenset[str]:
    """`/du-an/X` → {X/nghiep-vu, X/cach-lam}; dạng khác giữ nguyên. Không có "tìm toàn kho"."""
    if not isinstance(vung_cap, (list, tuple)) or not vung_cap:
        raise LoiVungCap("Vùng cấp rỗng hoặc thiếu — không có tìm toàn kho")
    tap: set[str] = set()
    for p in vung_cap:
        if not isinstance(p, str) or _VUNG.fullmatch(p) is None:
            raise LoiVungCap(f"Phần tử vùng cấp không hợp lệ: {str(p)[:80]!r}")
        if p.startswith("/du-an/") and p.count("/") == 2:
            tap.update(f"{p}/{n}" for n in NHANH)
        else:
            tap.add(p)
    return frozenset(tap)


def nhom_cua(pham_vi: str) -> str:
    if pham_vi.startswith("/du-an/"):
        return "du-an"
    return "vai" if pham_vi.startswith("/vai/") else "chung"


def chia_nhom(tap: Iterable[str]) -> dict[str, list[str]]:
    """Tách tập phạm vi theo nhóm hạn mức, giữ thứ tự du-an → vai → chung."""
    nhom: dict[str, list[str]] = {k: [] for k in NHOM_MAC_DINH}
    for p in sorted(tap):
        nhom[nhom_cua(p)].append(p)
    return {k: v for k, v in nhom.items() if v}


def _ten(ten: str) -> str:
    if not isinstance(ten, str) or _TEN.fullmatch(ten) is None:
        raise LoiVungCap(f"Tên không hợp lệ: {str(ten)[:80]!r}")
    return ten


def goc_du_an(ten: str) -> str:
    return f"/du-an/{_ten(ten)}"


def pham_vi_du_an(ten: str, nhanh: str) -> str:
    if nhanh not in NHANH:
        raise LoiVungCap(f"Nhánh không hợp lệ: {nhanh!r}")
    return f"{goc_du_an(ten)}/{nhanh}"


def du_an_cua(pham_vi: str) -> str | None:
    return pham_vi.split("/")[2] if pham_vi.startswith("/du-an/") else None


def vung_cap_cham_cot(ten: str) -> list[str]:
    """Vùng cấp của bộ chấm cột 1a cho dự án `ten` (spec 1b §4)."""
    return [goc_du_an(ten), "/vai/cham-cot", "/chung"]
