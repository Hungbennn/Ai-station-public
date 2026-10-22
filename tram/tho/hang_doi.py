"""Hàng đợi báo cáo của phiếu (spec 3 §7.4), phía TIẾN TRÌNH QUẢN LÝ: đọc file `tram bao` ghi, KIỂM LẠI cấu trúc
(agent có thể ghi thẳng vào file), bỏ mọi id agent ghi, tự gắn `khe_id`/`giao_id`/`luot` của phiếu, sinh `request_id`
tất định theo vị trí dòng (bền mà không cần lưu riêng); bỏ mọi dòng ghi sau `xong` đầu tiên."""
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from tram.ban_giao.cau_truc import LoiCauTruc, kiem_cau_truc
from tram.de_nghi.loc import LOAI_DE_NGHI, loc
from tram.tho.bao import GIOI_HAN_NOI_DUNG, LOAI, LOAI_HOI

KHOA_DONG = {"loai", "noi_dung", "commit", "ban_giao", "loai_hoi", "viec_moi"}
ID_CUA_AGENT = {"khe_id", "giao_id", "luot", "request_id", "bead_id", "du_an"}   # agent ghi → bỏ, không tin (D82)
SHA_RE = re.compile(r"[0-9a-f]{7,40}")


@dataclass(frozen=True)
class DongHangDoi:
    so: int                  # số thứ tự dòng (0-based)
    than: dict | None        # thân `POST /api/tho/bao` đã gắn phiếu; None khi dòng hỏng
    loi: str | None = None


def request_id_cho(giao_id: str, luot: int, so: int) -> str:
    return "r-" + hashlib.sha256(f"{giao_id}:{luot}:{so}".encode()).hexdigest()[:32]


def kiem_dong(tho: str) -> dict:
    try:
        d = json.loads(tho)
    except ValueError:
        raise LoiCauTruc("dòng không phải JSON") from None
    if not isinstance(d, dict):
        raise LoiCauTruc("dòng phải là JSON object")
    d = {k: v for k, v in d.items() if k not in ID_CUA_AGENT}
    if set(d) - KHOA_DONG or d.get("loai") not in LOAI:
        raise LoiCauTruc(f"dòng có khoá lạ hoặc loại sai: {sorted(set(d) - KHOA_DONG)} {d.get('loai')!r}")
    if "viec_moi" in d and d["loai"] != "viec_moi":
        raise LoiCauTruc("dòng có khoá lạ: viec_moi chỉ đi với loại viec_moi")
    if d["loai"] in LOAI_DE_NGHI and (loi := loc(d["loai"], d)) is not None:
        raise LoiCauTruc(f"đề nghị bị từ chối: {loi.ly_do}")                     # TC: lọc lại (design D-3)
    if not isinstance(d.get("noi_dung", ""), str) or len(d.get("noi_dung", "")) > GIOI_HAN_NOI_DUNG:
        raise LoiCauTruc("noi_dung sai kiểu hoặc dài quá")
    if d.get("commit") is not None and not (isinstance(d["commit"], str) and SHA_RE.fullmatch(d["commit"])):
        raise LoiCauTruc("commit không phải SHA")
    if (d["loai"] == "can_hoi") != (d.get("loai_hoi") in LOAI_HOI) or (d["loai"] == "can_hoi" and "ban_giao" in d):
        raise LoiCauTruc("can_hoi cần loai_hoi hợp lệ, không kèm bàn giao; loại khác không có loai_hoi")
    if d["loai"] == "xong" and "ban_giao" not in d:
        raise LoiCauTruc("xong phải kèm bàn giao")
    if "ban_giao" in d:
        kiem_cau_truc(d["ban_giao"], can_chinh_thuc=d["loai"] == "xong")
    return d


def xu_ly_hang_doi(p: Path, *, khe_id: str, giao_id: str, luot: int, tu_dong: int = 0
                   ) -> tuple[list[DongHangDoi], int]:
    """Các dòng TRỌN VẸN (kết thúc bằng xuống dòng) từ `tu_dong`; trả (dòng, vị trí đọc kế tiếp). Gặp `xong` hợp lệ
    → dừng, mọi dòng sau bị bỏ (vị trí kế tiếp = cuối file)."""
    if not p.exists():
        return [], tu_dong
    dong = p.read_text(encoding="utf-8").split("\n")[:-1]
    ra = []
    for so in range(tu_dong, len(dong)):
        try:
            d = kiem_dong(dong[so])
        except LoiCauTruc as e:
            ra.append(DongHangDoi(so, None, str(e)))
            continue
        if "ban_giao" in d:
            d["ban_giao"] = {**d["ban_giao"], "luot": luot}
        ra.append(DongHangDoi(so, {**d, "khe_id": khe_id, "giao_id": giao_id, "luot": luot,
                                   "noi_dung": d.get("noi_dung", ""), "commit": d.get("commit"),
                                   "request_id": request_id_cho(giao_id, luot, so)}))
        if d["loai"] == "xong":
            return ra, len(dong)
    return ra, len(dong)
