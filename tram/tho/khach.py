"""Khách API thợ: B đọc file riêng của tram-tho; máy từ xa giữ Keychain. Không đưa token xuống khe."""
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from tram.cau_hinh.cach_ly import DIA_CHI_RE
from tram.keychain import doc_muc

KEYCHAIN_THO = "tram-tho-token"
LOGIN_RE = re.compile(r"[!-~]{1,320}")                   # ASCII in được, không khoảng trắng/xuống dòng (đi vào header)
MAY_B_RE = re.compile(r"[A-Za-z0-9.-]{1,253}")


class LoiKhachTram(RuntimeError):
    pass


def doc_token_may(*, tren_may_b=False, chay=None) -> str | None:
    if tren_may_b:
        from tram.tho.token_may_file import doc_token_b
        return doc_token_b()
    return doc_muc(KEYCHAIN_THO, chay=chay)


@dataclass(frozen=True)
class DichKiemAm:
    """Đích hai thăm dò khe của `tram tho kiem` do trạm cấp (D54) — đã kiểm dạng trước khi vào argv thăm dò."""
    dai_ca_login: str
    may_b: str
    db_nghiep_vu: tuple[str, ...]


def _khop(x, mau: re.Pattern) -> bool:
    return isinstance(x, str) and mau.fullmatch(x) is not None


@dataclass
class KhachTram:
    url: str
    token: str
    mo: object = field(default=urllib.request.urlopen, repr=False)
    thoi_gian_cho: float = 10.0

    def __repr__(self) -> str:                       # không bao giờ lộ token qua log/traceback
        return f"KhachTram(url={self.url!r})"

    def goi(self, method: str, duong: str, than: dict | None = None, *, xac_thuc: bool = True) -> tuple[int, dict]:
        h = {"Content-Type": "application/json", **({"Authorization": f"Bearer {self.token}"} if xac_thuc else {})}
        yc = urllib.request.Request(self.url + duong, method=method, headers=h,
                                    data=None if than is None else json.dumps(than, ensure_ascii=False).encode())
        try:
            with self.mo(yc, timeout=self.thoi_gian_cho) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read() or b"{}")
            except ValueError:
                return e.code, {}
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise LoiKhachTram(f"không gọi được tram-api: {type(e).__name__}") from None

    def ping(self) -> dict:
        ma, kq = self.goi("GET", "/api/tho/ping")
        if ma != 200:
            raise LoiKhachTram(f"tram-api trả {ma}")
        return kq

    def du_an(self) -> list[str]:
        """Danh sách dự án (API đọc của dashboard — không gửi token máy)."""
        ma, kq = self.goi("GET", "/api/du-an", xac_thuc=False)
        if ma != 200:
            raise LoiKhachTram(f"tram-api trả {ma}")
        return [d["ten"] for d in kq.get("du_an", [])]

    def kiem_am(self) -> DichKiemAm:
        ma, kq = self.goi("GET", "/api/tho/kiem-am")
        if ma != 200:
            raise LoiKhachTram(f"tram-api trả {ma}")
        db = kq.get("db_nghiep_vu") if isinstance(kq, dict) else None
        if not (isinstance(db, list) and all(isinstance(d, str) and DIA_CHI_RE.fullmatch(d) for d in db)
                and _khop(kq.get("dai_ca_login"), LOGIN_RE) and _khop(kq.get("may_b"), MAY_B_RE)):
            raise LoiKhachTram("tram-api trả đích kiểm chứng âm sai dạng")
        return DichKiemAm(kq.get("dai_ca_login"), kq.get("may_b"), tuple(db))
