"""Khoá `cong_bo:` trong `~/.tram/cau-hinh.yaml` (spec 3 §6.4). Ba giá trị: `ref-tam` (thợ push ref tạm lên GitHub,
trạm fetch từ origin rồi CAS ref công bố), `kho-tho` (thợ không có credential GitHub; trạm fetch thẳng từ kho cục bộ
của tài khoản quản lý thợ — chỉ máy B) và `lai` (D4: máy trong `kho_tho` dùng kho-tho, máy từ xa đã xác thực dùng
ref-tam; tên giá trị `lai` còn chờ chốt trước ghép, D4 chính thức khi S7 đạt). Không tự bật nguồn — không khai
`phuong_an` (mặc định) → trạm KHÔNG công bố gì: `/api/tho/da-push` trả 503 `chua-chot-phuong-an`."""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tram.duong_dan import tram_home

PHUONG_AN = ("ref-tam", "kho-tho", "lai")
MAY_RE = re.compile(r"[A-Za-z0-9-]{1,32}")


@dataclass(frozen=True)
class CauHinhCongBo:
    phuong_an: str | None = None
    kho_tho: dict[str, Path] = field(default_factory=dict)    # may_id → gốc kho thợ (~<quản lý>/tram/kho)
    thoi_gian_cho_giay: int = 60                               # mỗi lệnh fetch/push/ls-remote
    giu_toi_thieu_phut: int = 2                                # han_giu còn ít hơn → chưa công bố, thợ gửi lại


def nap_cau_hinh_cong_bo(duong_dan: Path | None = None) -> CauHinhCongBo:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    cb = (raw.get("cong_bo") or {}) if isinstance(raw, dict) else None
    if not isinstance(cb, dict) or set(cb) - {"phuong_an", "kho_tho", "thoi_gian_cho_giay", "giu_toi_thieu_phut"}:
        raise ValueError("cong_bo phải là bảng {phuong_an, kho_tho, thoi_gian_cho_giay, giu_toi_thieu_phut}")
    pa = cb.get("phuong_an")
    if pa is not None and pa not in PHUONG_AN:
        raise ValueError(f"cong_bo.phuong_an phải là một trong {PHUONG_AN} (Đại ca chốt sau S7)")
    kho = cb.get("kho_tho") or {}
    if not isinstance(kho, dict) or not all(isinstance(k, str) and MAY_RE.fullmatch(k) and isinstance(v, str)
                                            and Path(v).expanduser().is_absolute() for k, v in kho.items()):
        raise ValueError("cong_bo.kho_tho: {may_id: đường dẫn tuyệt đối}")
    if pa in ("kho-tho", "lai") and not kho:
        raise ValueError("phương án kho-tho/lai cần cong_bo.kho_tho")
    so = {k: cb.get(k, d) for k, d in (("thoi_gian_cho_giay", 60), ("giu_toi_thieu_phut", 2))}
    if any(isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 600 for v in so.values()):
        raise ValueError("thoi_gian_cho_giay, giu_toi_thieu_phut là số nguyên 1–600")
    return CauHinhCongBo(pa, {k: Path(v).expanduser() for k, v in kho.items()}, **so)
