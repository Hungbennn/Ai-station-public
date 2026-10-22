"""Đọc khối bàn giao trong notes kèm danh sách lỗi — dashboard cần phân biệt 'không có' và 'hỏng' (spec 2 §12.5)."""
import re

from pydantic import ValidationError

from tram.ban_giao.schema import GIOI_HAN_BYTE, KHOI_RE, BanGiao
from tram.suy.lam_sach import co_ky_tu_an

DAU = "<!-- ban-giao -->"
PR_HTTPS = re.compile(r"https://[^\s<>\"']+")


def doc_khoi_ban_giao_co_loi(notes: str | None) -> tuple[BanGiao | None, list[str]]:
    notes = notes or ""
    khop = KHOI_RE.findall(notes)
    if not khop:
        return (None, ["Khối bàn giao thiếu dấu đóng hoặc không phải một JSON object"]) if DAU in notes else (None, [])
    tho = khop[-1]
    if len(tho.encode()) > GIOI_HAN_BYTE:
        return None, ["Khối bàn giao vượt 64 KB"]
    try:
        return BanGiao.model_validate_json(tho), []
    except ValidationError as e:
        return None, [f"{'.'.join(str(x) for x in l['loc']) or 'khoi'}: {l['msg']}" for l in e.errors()][:10]


def tom_tat_ban_giao(notes: str | None) -> dict | None:
    bg, loi = doc_khoi_ban_giao_co_loi(notes)
    if bg is None and not loi:
        return None
    pr = bg.pr if bg is not None else None
    if pr is not None and co_ky_tu_an(pr):
        loi, pr = loi + ["pr có ký tự điều khiển"], None
    if pr is not None and not PR_HTTPS.fullmatch(pr):
        loi, pr = loi + ["pr không phải URL https — không hiện link"], None
    return {"pr": pr, "nhanh": bg.nhanh if bg else None, "commit": bg.commit if bg else None,
            "file_ban_giao": bg.file_ban_giao if bg else None, "loi": loi}
