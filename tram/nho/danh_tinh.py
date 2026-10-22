"""Ai đang gọi MCP memory và được cấp vùng nào (spec 1b §4, §9.2, §9.3) — trạm cấp, LLM không bao giờ chọn.

Đúng MỘT trong hai đường mỗi lời gọi (trộn → từ chối):
- CLI máy thợ: `X-Tram-Giao-Id` + `X-Tram-Ma-Giao` → tra phiếu (cache 30 giây), so `ma_giao` hằng thời gian →
  vùng `[/du-an/X, /vai/<vai của phiếu>, /chung]`, được ghi (`ghi_nho` luôn vào `/du-an/X`).
- Phiên tay của Đại ca: `Authorization: Bearer <mã Đại ca>` + `X-Tram-Du-An: X` → so sha256 với bản băm trong
  `~/.tram/cau-hinh.yaml` → vùng `[/du-an/X, /vai/dieu-phoi, /chung]`, CHỈ ĐỌC.
Header danh tính Tailscale không được xét (tiến trình cục bộ giả được — §9.3). Thông báo từ chối không chứa
`ma_giao` hay mã Đại ca."""
import hashlib
import hmac
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from tram.nho.pham_vi import TEN, goc_du_an

GIAO_ID_RE = re.compile(r"g-\d{8}-\d{4,}")
MA_GIAO_RE = re.compile(r"[A-Za-z0-9_-]{22}")
TEN_RE = re.compile(TEN)
VAI_PHIEN_TAY = "dieu-phoi"
H_GIAO, H_MA, H_AUTH, H_DU_AN = b"x-tram-giao-id", b"x-tram-ma-giao", b"authorization", b"x-tram-du-an"


class TuChoi(Exception):
    """`ma`: 401 bằng chứng thiếu/sai, 403 dự án không có, 503 không tra được phiếu — đều là từ chối (M2)."""

    def __init__(self, ly_do: str, ma: int = 401):
        super().__init__(ly_do)
        self.ma = ma


@dataclass(frozen=True)
class DanhTinh:
    du_an: str
    vung_cap: tuple[str, ...]
    duoc_ghi: bool
    giao_id: str | None = None
    vai: str | None = None
    ma_giao: str | None = field(default=None, repr=False)     # chỉ để che trong nội dung ghi_nho — không log


def _mot(headers: list[tuple[bytes, bytes]], ten: bytes) -> str | None:
    ds = [v for k, v in headers if k.lower() == ten]
    if len(ds) > 1:
        raise TuChoi("header lặp")
    return ds[0].decode("latin-1").strip() if ds else None


def xac_thuc(headers: Iterable[tuple[bytes, bytes]], *, tra: Callable[[str], dict | None] | None,
             bam_ma_dai_ca: Callable[[], str | None], co_du_an: Callable[[str], bool]) -> DanhTinh:
    """`headers`: header ASGI thô. `tra`: TraPhieu (None khi chưa có tram-noi-bo-token). Lỗi → TuChoi."""
    headers = list(headers)
    giao_id, ma_giao, auth, du_an = (_mot(headers, h) for h in (H_GIAO, H_MA, H_AUTH, H_DU_AN))
    if giao_id is not None or ma_giao is not None:
        if auth is not None or du_an is not None:
            raise TuChoi("trộn bằng chứng phiếu với mã Đại ca / X-Tram-Du-An")
        return _theo_phieu(giao_id, ma_giao, tra)
    if auth is not None or du_an is not None:
        return _phien_tay(auth, du_an, bam_ma_dai_ca, co_du_an)
    raise TuChoi("thiếu bằng chứng (phiếu hoặc mã Đại ca)")


def _theo_phieu(giao_id: str | None, ma_giao: str | None, tra) -> DanhTinh:
    if not giao_id or not ma_giao or not GIAO_ID_RE.fullmatch(giao_id) or not MA_GIAO_RE.fullmatch(ma_giao):
        raise TuChoi("thiếu hoặc sai dạng X-Tram-Giao-Id / X-Tram-Ma-Giao")
    if tra is None:
        raise TuChoi("memory service chưa có tram-noi-bo-token — không tra được phiếu", 503)
    try:
        p = tra(giao_id)
    except Exception as e:                                   # noqa: BLE001 — mọi lỗi tra phiếu: từ chối (fail closed)
        raise TuChoi(f"không tra được phiếu: {type(e).__name__}", 503) from None
    if p is None or p.get("con_hieu_luc") is not True or not isinstance(p.get("ma_giao"), str):
        raise TuChoi("phiếu không có hoặc đã hết hiệu lực")
    if not hmac.compare_digest(ma_giao.encode(), p["ma_giao"].encode()):
        raise TuChoi("ma_giao không khớp phiếu")
    du_an, vai = p.get("du_an"), p.get("vai")
    if not all(isinstance(x, str) and TEN_RE.fullmatch(x) for x in (du_an, vai)):
        raise TuChoi("phiếu mang dự án/vai sai dạng", 503)
    return DanhTinh(du_an, (goc_du_an(du_an), f"/vai/{vai}", "/chung"), True, giao_id, vai, ma_giao)


def _phien_tay(auth: str | None, du_an: str | None, bam_ma_dai_ca, co_du_an) -> DanhTinh:
    if not auth or not auth.startswith("Bearer ") or not du_an or not TEN_RE.fullmatch(du_an):
        raise TuChoi("phiên tay cần Authorization: Bearer <mã Đại ca> và X-Tram-Du-An: <dự án>")
    bam = bam_ma_dai_ca()
    if not bam:
        raise TuChoi("chưa đặt mã Đại ca (tram chu dat-ma-dai-ca)")
    gui = hashlib.sha256(auth.removeprefix("Bearer ").encode()).hexdigest()
    if not hmac.compare_digest(gui.encode(), bam.encode()):
        raise TuChoi("sai mã Đại ca")
    if not co_du_an(du_an):
        raise TuChoi(f"không có dự án {du_an}", 403)
    return DanhTinh(du_an, (goc_du_an(du_an), f"/vai/{VAI_PHIEN_TAY}", "/chung"), False)
