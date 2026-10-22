"""Khoá `bat_ghi` của du-an/<ten>.yaml (lát 1a-2, D31; spec 0+1a §4.7, §8 mục 4 "Bật ghi").

`bat_ghi: false` — bản nháp do `tram du-an them` sinh: trạm chỉ đọc và quét thử dự án. `tram quet --ghi` bỏ qua,
bộ giao việc không giao, tram-api từ chối thao tác ghi trên bead. Thiếu khoá = `false` (bs-2bd.1.22, Đại ca chốt
17/10, INV-005: công tắc lớn mặc định tắt); 17/10 chỉ có `du-an/hr-codex.yaml`, đã khai rõ `false` (D40). Bật ghi:
Đại ca sửa tay thành `bat_ghi: true` — không có lệnh riêng.
"""
from pathlib import Path

import yaml

from tram.duong_dan import goc_repo

KHOA = "bat_ghi"


def bat_ghi(ten: str, *, thu_muc: Path | None = None) -> bool:
    """Đọc riêng khoá này (không qua `nap_du_an`); giá trị khác true/false → `ValueError` — nơi gọi coi như lỗi."""
    raw = yaml.safe_load(((thu_muc or goc_repo() / "du-an") / f"{ten}.yaml").read_text(encoding="utf-8"))
    gia_tri = raw.get(KHOA, False)
    if not isinstance(gia_tri, bool):
        raise ValueError(f"{KHOA} trong du-an/{ten}.yaml phải là true hoặc false, không phải {gia_tri!r}")
    return gia_tri
