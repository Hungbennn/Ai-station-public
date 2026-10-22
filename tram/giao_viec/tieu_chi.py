"""Nội dung phiếu suy từ bead (spec 4 §5.1 điều kiện 4, §5.1 điều kiện 7, §6.1): tiêu chí máy đọc được +
digest, lệnh bắt buộc, khoá chống trùng."""
import hashlib
import json
import re
from collections.abc import Iterable

from tram.cau_hinh.lenh import khop_bat_ky

DAU_DONG = re.compile(r"^(?:[-*](?:\s+|$)|\d+[.)]\s*)")
MA_NOI_DONG = re.compile(r"`([^`\n]+)`")


def tach_tieu_chi(acceptance: str) -> list[str]:
    """Tách dòng; bỏ khoảng trắng đầu cuối, đầu dòng `- `, `* `, `1.`; gộp khoảng trắng; bỏ dòng rỗng."""
    ra = []
    for dong in (acceptance or "").splitlines():
        dong = " ".join(DAU_DONG.sub("", dong.strip()).split())
        if dong:
            ra.append(dong)
    return ra


def digest_tieu_chi(tieu_chi: list[str]) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(tieu_chi, ensure_ascii=False).encode()).hexdigest()


def lenh_trong_design(design: str) -> list[str]:
    """Ứng viên lệnh trong `design`: từng dòng (bỏ đầu dòng và `$ `) và từng đoạn mã `…` trong dòng."""
    ra = []
    for dong in (design or "").splitlines():
        ra += [m.strip() for m in MA_NOI_DONG.findall(dong)]
        ra.append(DAU_DONG.sub("", dong.strip()).removeprefix("$ ").strip().strip("`").strip())
    return [x for x in ra if x]


def lenh_bat_buoc(mac_dinh: Iterable[str], design: str, lenh_cho_phep: Iterable[str]) -> list[str]:
    """`lenh_kiem_mac_dinh` cộng lệnh nêu trong `design` khớp `lenh_cho_phep` (§6.1) — không trùng, giữ thứ tự."""
    mau = list(lenh_cho_phep)
    them = [l for l in lenh_trong_design(design) if khop_bat_ky(l, mau) is not None]
    return list(dict.fromkeys([*mac_dinh, *them]))


def khoa_chong_trung(du_an: str, cha: str, bead_id: str, buoc: str, phien_ban_vai: str,
                     phien_ban_quyen: str) -> str:
    """`sha256(du_an, cha, bead_id, buoc, phien_ban_vai, phien_ban_quyen)` (§5.1 điều kiện 7)."""
    tho = json.dumps([du_an, cha, bead_id, buoc, phien_ban_vai, phien_ban_quyen], ensure_ascii=False)
    return "sha256:" + hashlib.sha256(tho.encode()).hexdigest()
