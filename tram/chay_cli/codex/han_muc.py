"""Bộ đọc hạn mức Codex (spec 3 §8.1, lát 3b) — HÌNH DẠNG CHƯA XÁC MINH, chờ spike S5.

Nguồn chính: `codex app-server` → `account/rateLimits/read`, kết quả `{"rateLimits": {"<tên>": {usedPercent,
windowDurationMins, resetsAt}}}` (spike hạn mức 12/10). Nguồn lùi: dòng `token_count` của
`$CODEX_HOME/sessions/**/rollout-*.jsonl`, `rate_limits.<tên>.{used_percent, window_minutes, resets_at}`.
Tên cửa sổ theo THỜI LƯỢNG (`ten_cua_so`: 300 → 5h, 10080 → tuan), không theo primary/secondary. `resets_at` nhận giây
epoch hoặc chuỗi ISO. Trường thiếu/sai → bỏ cửa sổ đó (thành chưa biết ở `lam_moi`), KHÔNG giả 0%.
`codex exec --json` không mang hạn mức (theo hiểu biết hiện tại) — chỉ dùng thông điệp lỗi để phát hiện hết hạn mức."""
import re
from datetime import datetime, timezone

from tram.han_muc.mo_hinh import CuaSo, HanMuc, ten_cua_so

MAU_HET = re.compile(r"usage limit|rate limit|too many requests|\b429\b|quota", re.I)
MAU_CHUA_DANG_NHAP = re.compile(r"not logged in|log ?in again|unauthorized|\b401\b", re.I)


def _chuoi(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gio(x) -> str | None:
    try:
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            return _chuoi(datetime.fromtimestamp(x / 1000 if x > 1e12 else x, timezone.utc))
        if isinstance(x, str):
            d = datetime.fromisoformat(x.replace("Z", "+00:00"))
            return _chuoi(d if d.tzinfo else d.replace(tzinfo=timezone.utc))
    except (ValueError, OverflowError, OSError):
        pass
    return None


def _so(x) -> float | None:
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _cac_cua_so(bang, k_pt: str, k_phut: str, k_reset: str, doc_luc: str) -> list[CuaSo]:
    ra: dict[str, CuaSo] = {}
    for ten, d in (bang.items() if isinstance(bang, dict) else []):
        if not isinstance(d, dict):
            continue
        pt, phut = _so(d.get(k_pt)), _so(d.get(k_phut))
        if pt is None or not 0 <= pt <= 100 or phut is None or phut < 1 or phut != int(phut):
            continue
        loai = ten_cua_so(int(phut), str(ten)[:32])
        ra.setdefault(loai, CuaSo(loai=loai, trang_thai="biet", phan_tram=pt, reset_luc=_gio(d.get(k_reset)),
                                  doc_luc=doc_luc))
    return list(ra.values())


def han_muc_app_server(ket_qua: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
    cs = _cac_cua_so(ket_qua.get("rateLimits"), "usedPercent", "windowDurationMins", "resetsAt", _chuoi(bay_gio))
    return HanMuc(khe_id=khe_id, cua_so=cs, nguon="app-server") if cs else None


def han_muc_rollout(dong: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
    p = dong.get("payload")
    if not isinstance(p, dict) or p.get("type") != "token_count":
        return None
    luc = _gio(dong.get("timestamp")) or _chuoi(bay_gio)
    cs = _cac_cua_so(p.get("rate_limits"), "used_percent", "window_minutes", "resets_at", luc)
    return HanMuc(khe_id=khe_id, cua_so=cs, nguon="log") if cs else None


def thong_diep_loi(dong: dict) -> str | None:
    """Thông điệp của sự kiện lỗi `codex exec --json` (`error`, `turn.failed`), cắt 300 ký tự; không phải lỗi → None."""
    if dong.get("type") == "error":
        m = dong.get("message")
    elif dong.get("type") == "turn.failed" and isinstance(dong.get("error"), dict):
        m = dong["error"].get("message")
    else:
        return None
    return m[:300] if isinstance(m, str) and m else None


class NguonHanMucCodex:
    """`NguonHanMuc` cho khe Codex: đọc dòng rollout (nguồn lùi); dòng exec chỉ dùng để phát hiện hết hạn mức."""

    def doc_dong(self, dong: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
        return han_muc_rollout(dong, khe_id=khe_id, bay_gio=bay_gio)

    def het_han_muc(self, dong: dict) -> bool:
        m = thong_diep_loi(dong)
        return bool(m and MAU_HET.search(m))
