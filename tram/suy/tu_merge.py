"""Việc chờ Đại ca của tự merge (spec `tu-merge` "Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao") — tính lúc đọc
từ sự kiện, không gọi GitHub hay Beads. Mỗi bead lấy sự kiện MỚI NHẤT trong nhóm dưới đây: `tu_merge.cho` (lý do do
trạm ghi khi lý do đổi), `tu_merge.loi`, `pr.khong_xac_minh` → bead đang chờ; các loại còn lại (gửi lệnh, xong, PR
đã merge, trả về, Đại ca kéo cột, bead đóng) → không còn chờ vì tự merge. Tiêu đề bead chỉ ghép lúc đọc cho
dashboard (`tieu_de_bead`, từ bộ đệm Beads của tram-api) — không bao giờ nằm trong sự kiện (INV-001). Logic nằm ở
đây; `suy/tu_dong.py` và `api/tuyen_tu_dong.py` (file chung với TM-1, TM-3) chỉ thêm dòng gọi."""
import json
import sqlite3
from collections.abc import Callable

from tram.beads.bd import LoiBd
from tram.giao_viec.tu_merge_xet import MUC, NHAN

TieuDe = Callable[[], dict[str, str]]

CHO = {"tu_merge.loi": ["tu_merge_loi"], "pr.khong_xac_minh": ["pr_khong_xac_minh"]}
LOAI = ("tu_merge.cho", "tu_merge.bat_dau", "tu_merge.xong", "tu_merge.loi", "pr.da_merge", "pr.khong_xac_minh",
        "cot.tra_ve", "cot.dai_ca_sua", "bead.dong")


def cho_dai_ca(db: sqlite3.Connection, du_an: str, tieu_de: TieuDe = dict) -> list[dict]:
    """Mới → cũ: `{bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}`; `muc` = loi (luôn chờ) | tat (đang chờ CI) |
    can_nguoi. `tieu_de()` (đọc Beads) chỉ gọi khi có việc chờ; thiếu → chuỗi rỗng."""
    cuoi = {}
    for bead_id, loai, luc, du_lieu in db.execute(
            f"SELECT bead_id, loai, luc, du_lieu FROM su_kien WHERE du_an = ? AND bead_id IS NOT NULL"
            f" AND loai IN ({','.join('?' * len(LOAI))}) ORDER BY id", (du_an, *LOAI)):
        cuoi[bead_id] = (loai, luc, du_lieu)
    ra = []
    for bead_id, (loai, luc, du_lieu) in cuoi.items():
        ma = json.loads(du_lieu).get("ly_do") if loai == "tu_merge.cho" else CHO.get(loai)
        if isinstance(ma, list) and ma:
            ra.append({"bead_id": bead_id, "luc": luc, "ly_do": [
                {"ma": m, "nhan": NHAN.get(m, m), "muc": MUC.get(m, "can_nguoi")} for m in ma if isinstance(m, str)]})
    ten = tieu_de() if ra else {}
    return sorted(({**c, "tieu_de": ten.get(c["bead_id"], "")} for c in ra), key=lambda x: x["luc"], reverse=True)


def tieu_de_bead(bo_dem, du_an: str) -> TieuDe:
    """Hàm đọc tiêu đề cho `cho_dai_ca` — chỉ chạy khi có việc chờ; Beads lỗi → rỗng (dashboard vẫn hiện lý do)."""
    def doc() -> dict[str, str]:
        try:
            return {b.id: b.title for b in bo_dem.lay(du_an)}
        except LoiBd:
            return {}
    return doc
