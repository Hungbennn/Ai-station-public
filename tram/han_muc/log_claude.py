"""Gộp số đo hạn mức theo cửa sổ, và nguồn lùi đọc log `projects/**/*.jsonl` trong `CLAUDE_CONFIG_DIR` của khe
(spec 3 §8.1) — log chỉ có `rate_limit_info` khi ĐÃ bị chặn. CHỜ SPIKE S1 (dạng dòng log) và S6 (tiến trình quản lý
có quyền đọc thư mục cấu hình của principal hay không). Không bao giờ đọc file đăng nhập."""
import json
from datetime import datetime
from pathlib import Path

from tram.han_muc.mo_hinh import HanMuc
from tram.han_muc.nguon import NguonHanMuc


def gop_han_muc(cu: HanMuc | None, moi: HanMuc | None) -> HanMuc | None:
    """Mỗi sự kiện có thể chỉ mang MỘT cửa sổ (S1 chốt): cửa sổ mới thay cửa sổ cùng loại, cửa sổ khác giữ nguyên."""
    if moi is None or cu is None or cu.khe_id != moi.khe_id:
        return moi or cu
    theo_loai = {c.loai: c for c in cu.cua_so} | {c.loai: c for c in moi.cua_so}
    return HanMuc(khe_id=moi.khe_id, cua_so=list(theo_loai.values())[:8], nguon=moi.nguon)


def _tim(x: object, khoa: str) -> list[dict]:
    if isinstance(x, dict):
        ra = [x[khoa]] if isinstance(x.get(khoa), dict) else []
        return ra + [y for v in x.values() for y in _tim(v, khoa)]
    if isinstance(x, list):
        return [y for v in x for y in _tim(v, khoa)]
    return []


def doc_log_claude(thu_muc: Path, *, khe_id: str, bay_gio: datetime, nguon: NguonHanMuc,
                   so_dong: int = 400) -> HanMuc | None:
    """Đọc `so_dong` dòng cuối của file log mới nhất; mỗi `rate_limit_info` tìm thấy coi như một `rate_limit_event`."""
    try:
        cac = sorted((thu_muc / "projects").glob("**/*.jsonl"), key=lambda p: p.stat().st_mtime)
        dong = cac[-1].read_text(encoding="utf-8", errors="replace").splitlines()[-so_dong:] if cac else []
    except OSError:
        return None
    hm = None
    for d in dong:
        try:
            obj = json.loads(d)
        except ValueError:
            continue
        for info in _tim(obj, "rate_limit_info"):
            moi = nguon.doc_dong({"type": "rate_limit_event", "rate_limit_info": info}, khe_id=khe_id,
                                 bay_gio=bay_gio)
            hm = gop_han_muc(hm, moi)
    return None if hm is None else HanMuc(khe_id=khe_id, cua_so=hm.cua_so, nguon="log")
