"""Luật cứng nghiệp vụ (spec 1b §6.2 bước 3) — tất định, chạy sau LLM, ghi đè LLM.

Chạm luật → ép ký ức về `/du-an/<ten>/nghiep-vu`. Không bảo đảm bắt hết nghiệp vụ (§6.3 "Giới hạn")."""
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from tram.cau_hinh.du_an import nap_du_an

# `(?!\w)` sau đơn vị (không dùng \b vì `₫` không phải chữ): "3 điểm", "2 đường" không khớp; "2 nghìn dòng" khớp nhầm.
# `(?!\s*lệ)`: "2 tỉ lệ" là tỷ lệ, không phải số tiền.
TIEN_RE = re.compile(r"\d[\d.,\s]*\s?(đ|₫|vnđ|vnd|usd|triệu|tr|tỷ|tỉ|nghìn|ngàn|k)(?!\w)(?!\s*lệ)|\$\s?\d")
MODULE_DANG_RE = re.compile(r"Modules/[A-Z][A-Za-z0-9_]*|(?<!\w)[A-Z][A-Za-z0-9_]*Controller(?!\w)")


@dataclass(frozen=True)
class LuatDuAn:
    module: tuple[str, ...] = ()          # khoá `module` trong du-an/<ten>.yaml — trọn từ, phân biệt hoa thường
    tu_khoa_khach: tuple[str, ...] = ()   # khoá `tu_khoa_khach` — tuỳ chọn (#20)


def chuan_hoa(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower()


def _tron_tu(tu: str, van_ban: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(tu)}(?!\w)", van_ban) is not None


def ly_do_nghiep_vu(noi_dung: str, luat: LuatDuAn, *, co_ten_rieng: bool = False) -> list[str]:
    """Danh sách lý do chạm luật (rỗng = không chạm)."""
    nfc = unicodedata.normalize("NFC", noi_dung)
    thap = chuan_hoa(noi_dung)
    ly_do = []
    if m := TIEN_RE.search(thap):
        ly_do.append(f"số tiền ({m.group(0).strip()})")
    mod = [t for t in luat.module if t and _tron_tu(t, nfc)]
    if mod or (m := MODULE_DANG_RE.search(nfc)):
        ly_do.append(f"tên module ({mod[0] if mod else m.group(0)})")
    khach = [t for t in luat.tu_khoa_khach if t.strip() and _tron_tu(chuan_hoa(t.strip()), thap)]
    if khach or co_ten_rieng:
        ly_do.append(f"tên khách ({khach[0] if khach else 'LLM báo có tên riêng'})")
    return ly_do


def luat_cua_du_an(ten: str, *, thu_muc: Path | None = None) -> LuatDuAn:
    """Đọc `module`, `tu_khoa_khach` từ du-an/<ten>.yaml; dự án đã gỡ (không còn file) → chỉ luật chung."""
    try:
        d = nap_du_an(ten, thu_muc=thu_muc)
    except FileNotFoundError:
        return LuatDuAn()
    return LuatDuAn(d.module, d.tu_khoa_khach)
