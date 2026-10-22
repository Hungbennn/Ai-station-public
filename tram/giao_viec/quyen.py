"""Phiên bản file quyền theo vai (spec 3 §7.2; spec 4 §5.1 điều kiện 7) — thành phần `phien_ban_quyen` của
`khoa_chong_trung`. File `vai/quyen/<vai>.json` của repo trạm do 3a-2 tạo (đường dẫn theo spec 3 §7.2). Phiên bản =
băm NỘI DUNG file: mọi thay đổi quyền đổi khoá, không phụ thuộc định dạng file (chưa chốt tới S4). Chưa có file
(trước 3a-2) → "0" như 4a-1; `tram giao kiem` báo ĐỎ trường hợp này."""
import hashlib
from pathlib import Path

from tram.duong_dan import goc_repo

KHONG_CO = "0"


def phien_ban_quyen(vai: str, *, goc: Path | None = None) -> str:
    p = (goc or goc_repo() / "vai" / "quyen") / f"{vai}.json"
    if not p.is_file():
        return KHONG_CO
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()[:16]
