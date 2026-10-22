"""Khoá `usage:` trong `~/.tram/cau-hinh.yaml` cho màn Usage (spec 2 §5.4, §8; plan 2b G4, G5). Không chứa bí mật.

    usage:
      ccusage: /Users/<tài khoản trạm>/.tram/ccusage/node_modules/.bin/ccusage   # tuyệt đối — bản cài cố định
      ccusage_phien_ban: "x.y.z"                     # bắt buộc đi kèm; `--version` lệch thì KHÔNG chạy (Q15)
      gia_usd_moi_trieu_token:                       # tuỳ chọn; mô hình thiếu giá → chi phí "chưa có giá"
        claude-sonnet-5-5: {vao: 3, ra: 15, cache_doc: 0.3, cache_ghi: 3.75}

Thiếu cả khoá → Usage chỉ có số liệu từ sự kiện trạm, không chạy ccusage, không có chi phí."""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tram.duong_dan import tram_home

PHIEN_BAN_RE = re.compile(r"\d+\.\d+\.\d+")
MO_HINH_RE = re.compile(r"[A-Za-z0-9._:-]{1,100}")
LOAI_GIA = ("vao", "ra", "cache_doc", "cache_ghi")
KHOA = {"ccusage", "ccusage_phien_ban", "gia_usd_moi_trieu_token"}


@dataclass(frozen=True)
class CauHinhUsage:
    ccusage: Path | None = None
    ccusage_phien_ban: str | None = None
    gia: dict[str, dict[str, float]] = field(default_factory=dict)   # mô hình → {vao, ra, cache_doc, cache_ghi}


def _so(v) -> bool:
    return not isinstance(v, bool) and isinstance(v, (int, float)) and 0 <= v <= 1000


def _gia(raw) -> dict[str, dict[str, float]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("usage.gia_usd_moi_trieu_token phải là bảng mô hình → giá")
    ra = {}
    for mh, g in raw.items():
        if not (isinstance(mh, str) and MO_HINH_RE.fullmatch(mh) and isinstance(g, dict)
                and not set(g) - set(LOAI_GIA) and {"vao", "ra"} <= set(g) and all(_so(v) for v in g.values())):
            raise ValueError(f"usage.gia_usd_moi_trieu_token.{mh}: cần {{vao, ra[, cache_doc, cache_ghi]}}"
                             " là số 0–1000")
        ra[mh] = {k: float(g.get(k, 0)) for k in LOAI_GIA}
    return ra


def nap_cau_hinh_usage(duong_dan: Path | None = None) -> CauHinhUsage:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    u = raw.get("usage") if isinstance(raw, dict) else None
    if u is None:
        return CauHinhUsage()
    if not isinstance(u, dict) or set(u) - KHOA:
        raise ValueError(f"usage phải là bảng với các khoá {sorted(KHOA)}")
    lenh, pb = u.get("ccusage"), u.get("ccusage_phien_ban")
    if (lenh is None) != (pb is None):
        raise ValueError("usage.ccusage và usage.ccusage_phien_ban phải đi cùng nhau")
    if lenh is not None:
        if not isinstance(lenh, str) or not Path(lenh).is_absolute() or ".." in Path(lenh).parts:
            raise ValueError("usage.ccusage phải là đường dẫn tuyệt đối tới bản cài cố định")
        if not isinstance(pb, str) or not PHIEN_BAN_RE.fullmatch(pb):
            raise ValueError("usage.ccusage_phien_ban phải là chuỗi 'x.y.z' (khoá chính xác — spec 2 §8)")
    return CauHinhUsage(Path(lenh) if lenh else None, pb, _gia(u.get("gia_usd_moi_trieu_token")))
