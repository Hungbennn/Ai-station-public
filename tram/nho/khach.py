"""Gọi memory service qua HTTP nội bộ 127.0.0.1:7710 (spec 1b §9.1) — dùng bởi 1a và lệnh `tram nho`.

Không import lancedb. Token `tram-nho-token` chỉ đọc từ Keychain (không đọc biến môi trường — biến môi trường
của tiến trình lộ qua `ps eww`); không bao giờ in ra, ghi file hay đưa vào môi trường CLI của khe."""
import http.client
import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable

from tram.keychain import doc_muc

URL_NHO = "http://127.0.0.1:7710"
KEYCHAIN_NHO = "tram-nho-token"
THOI_GIAN_CHO_1A = 2.0            # spec 1b §7: 1a chờ tối đa 2 giây rồi lùi về cách cũ
KHUC = 65536
TRUONG = ("id", "noi_dung", "pham_vi")       # 1a chỉ nhận ba trường (§7)


class LoiNhoKhach(RuntimeError):
    """Memory service tắt, lỗi, từ chối hoặc quá hạn — người gọi lùi về cách cũ. `ma`: mã HTTP khi service đã trả
    lời (None khi không gọi được); `than`: thân lỗi JSON của service (`{loi, ly_do?}`) để tram-api báo đúng (1b-3)."""

    def __init__(self, thong_bao: str, *, ma: int | None = None, than: dict | None = None):
        super().__init__(thong_bao)
        self.ma, self.than = ma, than or {}


def _than_loi(e: urllib.error.HTTPError) -> dict:
    try:
        d = json.loads(e.read(KHUC) or b"{}")
    except Exception:                         # noqa: BLE001 — thân lỗi hỏng/thiếu: chỉ còn mã HTTP
        return {}
    return d if isinstance(d, dict) else {}


def doc_token(*, chay=None) -> str | None:
    """Đọc từ Keychain (có hạn — `tram/keychain.py`); test thay `chay` (hoặc monkeypatch `doc_token`)."""
    return doc_muc(KEYCHAIN_NHO, chay=chay)


def _doc_trong_han(r, het_han: float, dong_ho) -> bytes:
    """Đọc thân theo khúc; hạn là hạn tổng — server nhỏ giọt từng byte không kéo dài được lời gọi."""
    doc = getattr(r, "read1", r.read)
    sock = getattr(getattr(getattr(r, "fp", None), "raw", None), "_sock", None)
    khuc = []
    while True:
        con_lai = het_han - dong_ho()
        if con_lai <= 0:
            raise TimeoutError("quá hạn tổng")
        if sock is not None:
            try:
                sock.settimeout(con_lai)          # mỗi lần recv cũng không vượt phần hạn còn lại
            except OSError:                       # bs-hpc.15: http.client/urllib đã đóng đối tượng socket (EBADF)
                                                  # dù fp vẫn đọc được
                sock = None                       # còn timeout của urlopen cho từng lần nhận
                                                  # + kiểm hạn tổng giữa các khúc
        b = doc(KHUC)
        if not b:
            return b"".join(khuc)
        khuc.append(b)


def goi_nho(duong: str, than: dict, *, token: str, url: str = URL_NHO, thoi_gian_cho: float = THOI_GIAN_CHO_1A,
            mo=urllib.request.urlopen, dong_ho=time.monotonic) -> dict:
    yc = urllib.request.Request(url + duong, method="POST", data=json.dumps(than, ensure_ascii=False).encode(),
                                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    het_han = dong_ho() + thoi_gian_cho
    try:
        with mo(yc, timeout=thoi_gian_cho) as r:
            kq = json.loads(_doc_trong_han(r, het_han, dong_ho) or b"{}")
    except urllib.error.HTTPError as e:
        raise LoiNhoKhach(f"memory service trả {e.code}", ma=e.code, than=_than_loi(e)) from None
    except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as e:
        raise LoiNhoKhach(f"không gọi được memory service: {type(e).__name__}") from None
    if not isinstance(kq, dict):
        raise LoiNhoKhach("memory service trả dữ liệu sai dạng")
    return kq


def nho_lai_http(truy_van: str, vung_cap: list[str], *, token: str, **kw) -> list[dict]:
    """Trả [{id, noi_dung, pham_vi}] — chỉ ba trường (§7)."""
    ds = goi_nho("/nho-lai", {"truy_van": truy_van, "vung_cap": vung_cap}, token=token, **kw).get("ky_uc")
    if not isinstance(ds, list) or not all(
            isinstance(k, dict) and all(isinstance(k.get(t), str) for t in TRUONG) for k in ds):
        raise LoiNhoKhach("memory service trả dữ liệu sai dạng")
    return [{t: k[t] for t in TRUONG} for k in ds]


def tao_nho_lai(*, chay=None, mo=urllib.request.urlopen) -> Callable[[str, list[str]], list[dict]] | None:
    """Hàm recall cho 1a; None khi chưa cài memory service (chưa có token) → 1a dùng cách cũ."""
    token = doc_token(chay=chay)
    if token is None:
        return None
    return lambda truy_van, vung_cap: nho_lai_http(truy_van, vung_cap, token=token, mo=mo)
