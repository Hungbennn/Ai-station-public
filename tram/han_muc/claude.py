"""Bộ đọc hạn mức của Claude Code (spec 3 §8.1, §7.8): `rate_limit_event` trong `claude -p --output-format
stream-json`, cộng nguồn lùi regex trên văn bản kết quả.

CHỜ SPIKE S1 — HÌNH DẠNG CHƯA XÁC MINH KHI CHẠY THẬT. Theo spike hạn mức 12/10 và tài liệu Agent SDK:
`{"type": "rate_limit_event", "rate_limit_info": {"status": "allowed|allowed_warning|rejected", "resetsAt": <giây
epoch>, "rateLimitType": "five_hour|seven_day|…", "utilization": <?>}}` (nhận cả dạng phẳng). Chưa biết
`utilization` là tỷ lệ 0–1 hay phần trăm → `thang=None` (mặc định tới khi S1 chốt) KHÔNG đọc số này: cửa sổ là
`chua_biet`, trừ `rejected` (= 100%) và `allowed_warning` (= chạm ngưỡng ngừng — phía an toàn của H4)."""
import re
from datetime import datetime, timezone
from typing import Literal

from tram.han_muc.mo_hinh import CuaSo, HanMuc

LOAI = {"five_hour": "5h", "seven_day": "tuan"}       # loại khác giữ tên gốc — không ánh xạ theo thời lượng
MAU_HET = re.compile(r"usage limit reached|hit your (usage )?limit|rate[ _-]?limit(ed)?\b|\b429\b", re.I)
MAU_GAN_HET = re.compile(r"approaching (your )?(usage|rate) limit", re.I)
MAU_DANG_NHAP = re.compile(r"invalid api key|please run /login|not logged in|authentication_failed", re.I)


def chuoi_gio(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gio(v: object) -> str | None:
    """`resetsAt`: giây epoch (mili giây nếu quá lớn) hoặc chuỗi ISO; sai dạng → None."""
    try:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return chuoi_gio(datetime.fromtimestamp(v / 1000 if v > 1e12 else v, timezone.utc))
        if isinstance(v, str):
            return chuoi_gio(datetime.fromisoformat(v.replace("Z", "+00:00")))
    except (ValueError, OverflowError, OSError):
        return None
    return None


def _ten(loai: object) -> str | None:
    if not isinstance(loai, str) or not loai:
        return None
    return LOAI.get(loai) or re.sub(r"[^A-Za-z0-9_.:-]", "-", loai)[:48]


def _van_ban(dong: dict) -> str:
    v = dong.get("result")
    return v if isinstance(v, str) else ""


class NguonHanMucClaude:
    """Thoả `NguonHanMuc` (tram/han_muc/nguon.py). `thang`: cách hiểu `utilization` — chốt ở S1."""

    def __init__(self, *, thang: Literal["ti_le", "phan_tram"] | None = None, ngung: float = 90.0):
        self.thang, self.ngung = thang, ngung

    def _phan_tram(self, info: dict) -> float | None:
        status, u = info.get("status"), info.get("utilization")
        if status == "rejected":
            return 100.0
        so = None
        if self.thang and isinstance(u, (int, float)) and not isinstance(u, bool):
            so = min(100.0, max(0.0, float(u) * (100 if self.thang == "ti_le" else 1)))
        if status == "allowed_warning":
            return max(so or 0.0, self.ngung)
        return so

    def doc_dong(self, dong: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
        doc = chuoi_gio(bay_gio)
        if dong.get("type") == "result" and MAU_GAN_HET.search(_van_ban(dong)):
            return HanMuc(khe_id=khe_id, nguon="regex", cua_so=[
                CuaSo(loai="regex", trang_thai="biet", phan_tram=self.ngung, doc_luc=doc)])
        if dong.get("type") != "rate_limit_event":
            return None
        info = dong.get("rate_limit_info") if isinstance(dong.get("rate_limit_info"), dict) else dong
        if (loai := _ten(info.get("rateLimitType"))) is None:
            return None
        pt, reset = self._phan_tram(info), _gio(info.get("resetsAt"))
        cs = (CuaSo(loai=loai, trang_thai="biet", phan_tram=pt, reset_luc=reset, doc_luc=doc) if pt is not None
              else CuaSo(loai=loai, trang_thai="chua_biet", reset_luc=reset, doc_luc=doc))
        return HanMuc(khe_id=khe_id, nguon="stream", cua_so=[cs])

    def het_han_muc(self, dong: dict) -> bool:
        if dong.get("type") == "rate_limit_event":
            info = dong.get("rate_limit_info") if isinstance(dong.get("rate_limit_info"), dict) else dong
            return info.get("status") == "rejected"
        if dong.get("type") == "assistant":
            return dong.get("error") == "rate_limit"
        return dong.get("type") == "result" and bool(dong.get("is_error")) and bool(MAU_HET.search(_van_ban(dong)))

    def chua_dang_nhap(self, dong: dict) -> bool:
        if dong.get("type") == "assistant":
            return dong.get("error") == "authentication_failed"
        return dong.get("type") == "result" and bool(dong.get("is_error")) and bool(
            MAU_DANG_NHAP.search(_van_ban(dong)))

    def reset_luc(self, dong: dict) -> str | None:
        """Giờ reset của cửa sổ vừa bị chặn (`rejected`) — để cầu dao ngắt đúng tới đó (§8.3)."""
        if dong.get("type") != "rate_limit_event":
            return None
        info = dong.get("rate_limit_info") if isinstance(dong.get("rate_limit_info"), dict) else dong
        return _gio(info.get("resetsAt")) if info.get("status") == "rejected" else None
