"""Luật cứng cho phạm vi KHÔNG thuộc `/du-an/*` (`/vai/*`, `/chung`) — spec 1b §6.2 bước 3, §8.

Ký ức ở đây đến tay agent của MỌI dự án, nên xét với danh sách `module` + `tu_khoa_khach` của mọi dự án đã `them`.
Chạm luật → từ chối (`nho.tu_choi`), không có chuyện "ép về nghiep-vu" vì không có dự án nào để ép về."""
import re
from collections.abc import Callable, Iterable

from tram.nho.luat import LuatDuAn, luat_cua_du_an


def luat_moi_du_an(cac_ten: Iterable[str], luat_cua: Callable[[str], LuatDuAn] = luat_cua_du_an) -> LuatDuAn:
    """Hợp luật của mọi dự án (giữ thứ tự gặp đầu, bỏ trùng). Một `du-an/<ten>.yaml` hỏng → lỗi nổi lên: người gọi
    phải từ chối, không được xét với danh sách thiếu."""
    module: dict[str, None] = {}
    khach: dict[str, None] = {}
    for ten in cac_ten:
        l = luat_cua(ten)
        module.update(dict.fromkeys(l.module))
        khach.update(dict.fromkeys(l.tu_khoa_khach))
    return LuatDuAn(tuple(module), tuple(khach))


def ten_du_an_trong(noi_dung: str, cac_ten: Iterable[str]) -> list[str]:
    """Tên dự án (trọn từ, không phân biệt hoa thường) trong nội dung thăng cấp — `/chung`, `/vai` không được lộ
    dự án nguồn (spec 1b §7 không trả `nguon` vì lý do này)."""
    thap = noi_dung.lower()
    return [f"tên dự án ({t})" for t in cac_ten
            if t and re.search(rf"(?<![\w-]){re.escape(t.lower())}(?![\w-])", thap)]
