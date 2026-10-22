"""Khoá `cach_ly:` trong `~/.tram/cau-hinh.yaml` (spec 3 §7.3, spec 2 §4 mục 2b). CƠ CHẾ CHƯA CHỐT — chờ spike S6:
- `kenh_ghi`: `header` (lát 2a — header Tailscale trên TCP localhost, GIẢ ĐƯỢC: chưa đạt điều kiện trước 3a) hay
  `unix-socket` (API ghi của dashboard chỉ nhận yêu cầu qua Unix socket trong thư mục chỉ tài khoản trạm vào được);
- `tram_kiem`: principal kiểm lại của trạm (`user:<tên>` | `sandbox:<tên>`, §7.3 mục 5) — NGUỒN DUY NHẤT từ lát 3c,
  đọc qua `tram.cau_hinh.principal_kiem.doc_principal_kiem` (không đọc thẳng trường này);
- `db_nghiep_vu`: `host:cổng` mà kiểm chứng âm H9 phải thấy bị chặn."""
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from tram.duong_dan import tram_home

KENH = ("header", "unix-socket")
DIA_CHI_RE = re.compile(r"[A-Za-z0-9.-]{1,253}:\d{1,5}")


@dataclass(frozen=True)
class CauHinhCachLy:
    kenh_ghi: str = "header"
    socket: Path | None = None              # mặc định ~/.tram/api/api.sock (thư mục 0700)
    tram_kiem: str | None = None
    db_nghiep_vu: tuple[str, ...] = ()

    @property
    def duong_socket(self) -> Path:
        return self.socket or tram_home() / "api" / "api.sock"


def nap_cau_hinh_cach_ly(duong_dan: Path | None = None) -> CauHinhCachLy:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    c = (raw.get("cach_ly") or {}) if isinstance(raw, dict) else None
    if not isinstance(c, dict) or set(c) - {"kenh_ghi", "socket", "tram_kiem", "db_nghiep_vu"}:
        raise ValueError("cach_ly phải là bảng {kenh_ghi, socket, tram_kiem, db_nghiep_vu}")
    kenh = c.get("kenh_ghi", "header")
    if kenh not in KENH:
        raise ValueError(f"cach_ly.kenh_ghi phải là một trong {KENH}")
    sock = Path(str(c["socket"])).expanduser() if c.get("socket") else None
    if sock is not None and (not sock.is_absolute() or len(str(sock)) > 100):
        raise ValueError("cach_ly.socket phải là đường dẫn tuyệt đối ≤ 100 ký tự (giới hạn sun_path)")
    db = c.get("db_nghiep_vu") or []
    if not isinstance(db, list) or not all(isinstance(x, str) and DIA_CHI_RE.fullmatch(x) for x in db):
        raise ValueError("cach_ly.db_nghiep_vu là danh sách 'host:cổng'")
    tk = c.get("tram_kiem")
    return CauHinhCachLy(kenh, sock, None if tk is None else str(tk), tuple(db))
