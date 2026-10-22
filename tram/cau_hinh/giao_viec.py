"""Khoá `giao_viec:` trong `~/.tram/cau-hinh.yaml` (lát 4a-2). `nap_cau_hinh_tram` bỏ qua khoá lạ nên đọc riêng ở
đây — không sửa `tram/cau_hinh/tram.py`. Thiếu khoá → bộ giao việc TẮT: tram-api không phát phiếu, không chạy tick.
Lát 3c: principal kiểm lại khai MỘT chỗ — `cach_ly.tram_kiem` — đọc qua `doc_principal_kiem` (khoá cũ
`giao_viec.principal_kiem` chỉ còn để đối chiếu, xem `tram/cau_hinh/principal_kiem.py`).

    cach_ly:
      tram_kiem: user:tram-kiem      # chờ S6 — user:<tên> | sandbox:<tên>; `tram giao kiem` kiểm khi chạy thật
    giao_viec:
      bat: false                     # true chỉ sau mọi cổng (3a-2, S6, S7) — cần cach_ly.tram_kiem
      chu_ky_giay: 120               # vòng tick (spec 4 §10); ≤ 150 để giữ G5 ≤ 3 phút
      thu_muc_kiem: /Users/Shared/tram-kiem      # gốc bản chép kiểm lại — NGOÀI ~/.tram, đường dẫn THẬT, của tram-kiem
"""
from dataclasses import dataclass
from pathlib import Path

import yaml

from tram.cau_hinh.principal_kiem import doc_principal_kiem
from tram.duong_dan import tram_home
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.quyen_kiem import goc_hop_le

KHOA = {"bat", "chu_ky_giay", "thu_muc_kiem", "principal_kiem", "du_an"}
CHU_KY = (30, 150)


@dataclass(frozen=True)
class CauHinhGiaoViec:
    bat: bool = False
    chu_ky_giay: int = 120
    thu_muc_kiem: Path | None = None
    principal_kiem: PrincipalKiem | None = None
    du_an: tuple[str, ...] = ()


def _thu_muc(raw, pk: PrincipalKiem | None) -> Path | None:
    p = None if raw is None else Path(str(raw)).expanduser()
    if p is not None and not p.is_absolute():
        raise ValueError("giao_viec.thu_muc_kiem phải là đường dẫn tuyệt đối")
    if pk is not None and (p is None or p.resolve().is_relative_to(tram_home().resolve())):
        raise ValueError("giao_viec.thu_muc_kiem phải đặt NGOÀI ~/.tram khi có cach_ly.tram_kiem")
    if pk is not None:
        goc_hop_le(p)                     # 3c: đường dẫn thật, ký tự an toàn (hồ sơ sandbox, lệnh cài)
    return p


def nap_cau_hinh_giao_viec(duong_dan: Path | None = None) -> CauHinhGiaoViec:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    gv = raw.get("giao_viec") if isinstance(raw, dict) else None
    if gv is None:
        return CauHinhGiaoViec()
    if not isinstance(gv, dict) or set(gv) - KHOA:
        raise ValueError(f"giao_viec phải là bảng với các khoá {sorted(KHOA)}")
    bat, chu_ky = gv.get("bat", False), gv.get("chu_ky_giay", 120)
    if not isinstance(bat, bool):
        raise ValueError("giao_viec.bat phải là true/false")
    if isinstance(chu_ky, bool) or not isinstance(chu_ky, int) or not CHU_KY[0] <= chu_ky <= CHU_KY[1]:
        raise ValueError(f"giao_viec.chu_ky_giay phải là số nguyên trong {CHU_KY} (giữ G5 ≤ 3 phút)")
    pk = doc_principal_kiem(p)
    if bat and pk is None:
        raise ValueError("giao_viec.bat cần cach_ly.tram_kiem — kiểm lại không bao giờ chạy dưới quyền tram-api (G4)")
    from tram.cau_hinh.pham_vi_giao import danh_sach
    return CauHinhGiaoViec(bat, chu_ky, _thu_muc(gv.get("thu_muc_kiem"), pk), pk,
                          danh_sach(gv, "du_an"))
