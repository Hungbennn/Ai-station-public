"""`~/.tram/tho.yaml` của tài khoản quản lý thợ (spec 3 §9.1). Không chứa bí mật.
Token B ở file riêng, máy từ xa ở Keychain.

`principal` (tài khoản/sandbox thực thi của khe) chốt sau spike S6: lát 3a-1 chỉ đọc như chuỗi, chưa dùng."""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tram.duong_dan import tram_home
from tram.tho.co_model import models
from tram.tho.cau_hinh_chay import CauHinhChay, doc_cau_hinh_chay

MAY_RE = re.compile(r"[A-Za-z0-9-]{1,32}")
TEN_KHE_RE = re.compile(r"[a-z0-9-]{1,32}")
API_RE = re.compile(r"(http://(127\.0\.0\.1|localhost):\d{2,5}|https://[A-Za-z0-9.-]+(:\d{2,5})?)/?")
VAI = ("spec", "coder", "qc")
CLI = ("claude", "codex")
KHOA_KHE = {"ten", "cli", "principal", "thu_muc_cau_hinh", "ten_goi_nho", "vai_uu_tien", "models"}


@dataclass(frozen=True)
class KheCauHinh:
    ten: str
    cli: str
    principal: str | None
    thu_muc_cau_hinh: Path
    ten_goi_nho: str
    vai_uu_tien: tuple[str, ...]
    models: tuple[str, ...] = ()


@dataclass(frozen=True)
class CauHinhTho:
    may_id: str
    tram_api: str
    khe: tuple[KheCauHinh, ...]
    chay: CauHinhChay = field(default_factory=CauHinhChay)      # 3a-2: cách chạy phiếu (tram/tho/cau_hinh_chay.py)

    def khe_id(self, k: KheCauHinh) -> str:
        return f"{self.may_id}/{k.ten}"

    @property
    def tren_may_b(self) -> bool:
        """`tram_api` loopback (đã qua `API_RE`) = quản lý thợ chạy trên CHÍNH máy B — tram-api chỉ nghe 127.0.0.1."""
        return self.tram_api.startswith(("http://127.0.0.1:", "http://localhost:"))


def _khe(raw: object) -> KheCauHinh:
    if not isinstance(raw, dict) or set(raw) - KHOA_KHE:
        raise ValueError(f"mỗi khe là bảng với các khoá {sorted(KHOA_KHE)}")
    ten, cli = str(raw.get("ten", "")), raw.get("cli")
    if not TEN_KHE_RE.fullmatch(ten):
        raise ValueError(f"tên khe {ten!r} chỉ gồm chữ thường, số, '-'")
    if cli not in CLI:
        raise ValueError(f"khe {ten}: cli {cli!r} không hỗ trợ — chỉ {CLI}")
    thu_muc = Path(str(raw.get("thu_muc_cau_hinh") or "")).expanduser()
    if not thu_muc.is_absolute():
        raise ValueError(f"khe {ten}: thu_muc_cau_hinh phải là đường dẫn tuyệt đối")
    goi_nho = str(raw.get("ten_goi_nho") or "").strip()
    if not goi_nho or len(goi_nho) > 64 or "@" in goi_nho:
        raise ValueError(f"khe {ten}: ten_goi_nho bắt buộc, ≤ 64 ký tự, không phải email")
    vai = raw.get("vai_uu_tien") or []
    if not isinstance(vai, list) or not vai or not set(vai) <= set(VAI):
        raise ValueError(f"khe {ten}: vai_uu_tien là danh sách con của {VAI}")
    principal = raw.get("principal")
    return KheCauHinh(ten, cli, None if principal is None else str(principal), thu_muc, goi_nho, tuple(vai),
                      models(raw.get("models", [])))


def nap_cau_hinh_tho(duong_dan: Path | None = None) -> CauHinhTho:
    p = duong_dan or tram_home() / "tho.yaml"
    if not p.exists():
        raise ValueError(f"Chưa có {p} — Đại ca tạo theo spec 3 §9.1")
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict) or set(raw) - {"may_id", "tram_api", "khe", "chay"}:
        raise ValueError(f"{p}: chỉ có các khoá may_id, tram_api, khe, chay")
    may_id, api = str(raw.get("may_id", "")), str(raw.get("tram_api", ""))
    if not MAY_RE.fullmatch(may_id):
        raise ValueError("may_id chỉ gồm chữ, số, '-'")
    if not API_RE.fullmatch(api):
        raise ValueError("tram_api phải là http://127.0.0.1:<cổng> (máy B) hoặc https://<máy B trong tailnet>")
    khe = tuple(_khe(k) for k in (raw.get("khe") or []))
    if not khe or len({k.ten for k in khe}) != len(khe):
        raise ValueError("khe: cần ít nhất một khe, tên không trùng")
    rieng = [k.principal for k in khe if (k.principal or "").startswith("user:")]
    if len(set(rieng)) != len(rieng):
        raise ValueError("khe: principal user:<tên> phải riêng từng khe (D53 — gửi tín hiệu/dọn theo UID của khe)")
    return CauHinhTho(may_id, api.rstrip("/"), khe, doc_cau_hinh_chay(raw.get("chay")))
