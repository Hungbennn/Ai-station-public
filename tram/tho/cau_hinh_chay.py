"""Khoá `chay:` của `~/.tram/tho.yaml` — cách `tram tho chay` chạy phiếu (spec 3 §6.4, §7.2, §7.6, §8.3).
`day` PHẢI khớp `cong_bo.phuong_an` của trạm (đề xuất §14, chốt sau S7); không khai → `tram tho chay` không nhận
phiếu. `thang_utilization` chờ S1. Không chứa bí mật."""
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PATH_HE_THONG = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
NHO_RE = re.compile(r"(?:http://(127\.0\.0\.1|localhost):\d{2,5}/mcp|https://[A-Za-z0-9.-]+(?::\d{2,5})?/nho/mcp)")
SO = {"han_chot_dung_mem_phut": (3, 1, 30), "lan_chay_moi_gio": (6, 1, 60), "lan_chay_moi_ngay": (60, 1, 1440),
      "thoi_gian_cho_kiem_giay": (900, 10, 7200)}


def path_mac_dinh() -> str:
    """Thư mục chứa `tram` của venv đang chạy (để agent gọi được `tram bao`) + PATH hệ thống."""
    return f"{Path(sys.executable).parent}:{PATH_HE_THONG}"


@dataclass(frozen=True)
class CauHinhChay:
    day: str | None = None                       # ref-tam | kho-tho
    han_chot_dung_mem_phut: int = 3              # Đại ca chốt 13/10
    lan_chay_moi_gio: int = 6                    # kiểm cục bộ trước mỗi lần spawn (trạm cũng đếm — §8.3)
    lan_chay_moi_ngay: int = 60
    thoi_gian_cho_kiem_giay: int = 900
    nho_url: str | None = None                   # memory MCP (1b-2) — chỉ đặt khi đã bật
    thang_utilization: str | None = None         # ti_le | phan_tram — chờ S1
    path: str = ""                               # PATH của CLI; rỗng → path_mac_dinh()
    thu_muc_tram: Path | None = None             # ~/.tram của tài khoản trạm — để cấm trong sandbox/kiểm chứng âm
    cong_cam: tuple[int, ...] = (7700,)          # cổng tram-api/dashboard — sandbox cấm kết nối

    @property
    def path_cli(self) -> str:
        return self.path or path_mac_dinh()


def doc_cau_hinh_chay(raw: object) -> CauHinhChay:
    raw = raw or {}
    if not isinstance(raw, dict) or set(raw) - set(CauHinhChay.__dataclass_fields__):
        raise ValueError(f"chay: là bảng với các khoá {sorted(CauHinhChay.__dataclass_fields__)}")
    if raw.get("day") not in (None, "ref-tam", "kho-tho"):
        raise ValueError("chay.day là ref-tam hoặc kho-tho (phải khớp cong_bo.phuong_an của trạm)")
    if raw.get("nho_url") is not None and not NHO_RE.fullmatch(str(raw["nho_url"])):
        raise ValueError("chay.nho_url phải là loopback /mcp hoặc HTTPS trạm từ xa /nho/mcp")
    if raw.get("thang_utilization") not in (None, "ti_le", "phan_tram"):
        raise ValueError("chay.thang_utilization là ti_le hoặc phan_tram (chốt ở S1)")
    so = {}
    for k, (md, lo, hi) in SO.items():
        v = raw.get(k, md)
        if isinstance(v, bool) or not isinstance(v, int) or not lo <= v <= hi:
            raise ValueError(f"chay.{k} là số nguyên {lo}–{hi}")
        so[k] = v
    tram = Path(str(raw["thu_muc_tram"])).expanduser() if raw.get("thu_muc_tram") else None
    if tram is not None and not tram.is_absolute():
        raise ValueError("chay.thu_muc_tram phải là đường dẫn tuyệt đối")
    cong = raw.get("cong_cam", [7700])
    if not isinstance(cong, list) or not all(isinstance(c, int) and 0 < c < 65536 for c in cong):
        raise ValueError("chay.cong_cam là danh sách cổng")
    return CauHinhChay(raw.get("day"), nho_url=raw.get("nho_url"), thang_utilization=raw.get("thang_utilization"),
                       path=str(raw.get("path") or ""), thu_muc_tram=tram, cong_cam=tuple(cong), **so)
