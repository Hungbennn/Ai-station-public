"""Tra phiếu cho MCP máy thợ (spec 1b §9.2): hỏi tram-api `GET /api/noi-bo/phieu/{giao_id}` bằng token nội bộ
`tram-noi-bo-token` (khác `tram-nho-token`), cache 30 giây. tram-api tắt, 401, 5xx, dữ liệu sai dạng → LoiTraPhieu:
người gọi TỪ CHỐI, không bao giờ coi là hợp lệ. Phản hồi chứa `ma_giao` (credential) — không log, không in."""
import http.client
import json
import re
import threading
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from collections.abc import Callable

from tram.keychain import doc_muc

URL_API = "http://127.0.0.1:7700"           # tram-api chỉ nghe localhost (tram/cli_dich_vu.py CONG_MAC_DINH)
KEYCHAIN_NOI_BO = "tram-noi-bo-token"       # cùng tên với tram/api/noi_bo.py (plan 3a-1 Task 23)
GIAO_ID_RE = re.compile(r"g-\d{8}-\d{4,}")
CACHE_GIAY = 30.0                           # §9.2: phiếu vừa thu hồi còn dùng được tối đa 30 giây (M2)
TOI_DA_CACHE = 256
THOI_GIAN_CHO = 2.0
TRUONG = ("du_an", "vai", "ma_giao", "con_hieu_luc")


class LoiTraPhieu(RuntimeError):
    """Không tra được phiếu — lời gọi MCP bị từ chối (fail closed)."""


def doc_token_noi_bo(*, chay=None) -> str | None:
    """Đọc Keychain (có hạn — `tram/keychain.py`); test thay `chay`, không bao giờ đọc Keychain thật."""
    return doc_muc(KEYCHAIN_NOI_BO, chay=chay)


def _dung_dang(d) -> bool:
    return (isinstance(d, dict) and all(k in d for k in TRUONG) and isinstance(d.get("du_an"), str)
            and isinstance(d.get("vai"), str) and isinstance(d.get("con_hieu_luc"), bool)
            and (d.get("ma_giao") is None or isinstance(d["ma_giao"], str)))


class TraPhieu:
    """Gọi được: `tra(giao_id) -> {du_an, vai, ma_giao, con_hieu_luc} | None` (None = tram-api trả 404).
    Cache tính từ lúc BẮT ĐẦU hỏi (lệch về phía ngắn hơn 30 giây); lỗi không được cache."""

    def __init__(self, lay_token: Callable[[], str | None], *, url: str = URL_API, mo=urllib.request.urlopen,
                 dong_ho: Callable[[], float] = time.monotonic, cache_giay: float = CACHE_GIAY):
        self._lay_token, self._url, self._mo, self._dong_ho = lay_token, url, mo, dong_ho
        self._cache_giay, self._khoa = cache_giay, threading.Lock()
        self._cache: OrderedDict[str, tuple[float, dict | None]] = OrderedDict()

    def __call__(self, giao_id: str) -> dict | None:
        if not isinstance(giao_id, str) or not GIAO_ID_RE.fullmatch(giao_id):
            raise ValueError("giao_id sai dạng")
        luc = self._dong_ho()
        with self._khoa:
            o = self._cache.get(giao_id)
            if o is not None and luc - o[0] < self._cache_giay:
                return o[1]
        kq = self._hoi(giao_id)
        with self._khoa:
            self._cache[giao_id] = (luc, kq)
            self._cache.move_to_end(giao_id)
            while len(self._cache) > TOI_DA_CACHE:
                self._cache.popitem(last=False)
        return kq

    def _hoi(self, giao_id: str) -> dict | None:
        token = self._lay_token()
        if not token:
            raise LoiTraPhieu("chưa có tram-noi-bo-token")
        yc = urllib.request.Request(f"{self._url}/api/noi-bo/phieu/{giao_id}",
                                    headers={"Authorization": f"Bearer {token}"})
        try:
            with self._mo(yc, timeout=THOI_GIAN_CHO) as r:
                d = json.loads(r.read(65536) or b"null")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise LoiTraPhieu(f"tram-api trả {e.code}") from None
        except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as e:
            raise LoiTraPhieu(f"không gọi được tram-api: {type(e).__name__}") from None
        if not _dung_dang(d):
            raise LoiTraPhieu("tram-api trả dữ liệu sai dạng")
        return {k: d[k] for k in TRUONG}
