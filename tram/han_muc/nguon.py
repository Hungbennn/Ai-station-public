"""Giao diện bộ đọc hạn mức của một CLI (spec 3 §8.1) — CHƯA CÓ BẢN THẬT.

Claude: `rate_limit_event` trong stream-json — chờ spike S1 (#5 chưa duyệt): `utilization` là tỷ lệ hay %, đủ cửa
sổ hay không, `rateLimitType` gồm gì. Codex: `codex app-server` (lát 3b, spike S5). Không đánh dấu sẵn sàng bằng
fixture giả; bản giả chỉ ở `tests/tho_gia.py`."""
from datetime import datetime
from typing import Protocol, runtime_checkable

from tram.han_muc.mo_hinh import HanMuc


@runtime_checkable
class NguonHanMuc(Protocol):
    def doc_dong(self, dong: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
        """Một dòng stream/log → số đo đã chuẩn hoá (`ten_cua_so`), hoặc None nếu dòng không mang hạn mức."""

    def het_han_muc(self, dong: dict) -> bool:
        """Dòng báo đã hết hạn mức / 429 (`rejected`, mẫu chữ của nguồn lùi) → cầu dao."""
