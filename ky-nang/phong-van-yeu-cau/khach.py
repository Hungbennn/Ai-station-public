"""Gọi tram-api máy B từ máy A (D46; plan 4d 4D-3b): chỉ `https://<máy B>[:cổng]`, không proxy, không chuyển hướng,
hạn 20 giây. Gửi `X-Tram: 1` và `Origin: <gốc trạm>` — điều kiện chống CSRF của API ghi, KHÔNG phải danh tính.
Không gửi header danh tính, mã hay token: danh tính do `tailscale serve` máy B gắn (D24: không dùng mã nhịp,
không đọc Keychain). Lỗi mạng không mang chi tiết (Q06). python3 ≥ 3.9, chỉ thư viện chuẩn."""
import http.client
import json
import re
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT_GIAY = 20
TIMEOUT_GUI = 420          # B có thể đọc bd + create + đối soát (mỗi lệnh bd tới 120 s) trước khi trả lời
TOI_DA_BYTE = 256 * 1024
TEN_MAY_RE = re.compile(r"[a-z0-9-]+(\.[a-z0-9-]+)*")    # như `ten_may_b` của B: ASCII, không IPv6, không dấu chấm cuối


class MatKetNoi(Exception):
    """Không biết B đã nhận hay chưa — với lệnh tạo, người gọi KHÔNG được coi là "chưa tạo"."""


class KhongChuyenHuong(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None                                   # 3xx thành lỗi: nội dung phiếu chỉ tới đúng máy B


def mo_mac_dinh():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), KhongChuyenHuong()).open


def goc_tram(url):
    """`https://<máy B>[:cổng]` không đường dẫn, query, user → gốc chuẩn (tên thường, bỏ `:443` — B so `Origin`
    nguyên chuỗi với `https://<ten_may_b>`); còn lại None."""
    u = urllib.parse.urlsplit((url or "").strip())
    if u.scheme != "https" or not u.hostname or u.path not in ("", "/") or u.query or u.fragment or "@" in u.netloc:
        return None
    try:
        cong = u.port
    except ValueError:
        return None
    if not TEN_MAY_RE.fullmatch(u.hostname.lower()):
        return None
    return "https://" + u.hostname.lower() + ("" if cong in (None, 443) else f":{cong}")


def goi(goc, duong, than, mo=None, timeout=TIMEOUT_GIAY):
    """POST JSON → (mã HTTP, thân dict). 4xx/5xx vẫn trả về. Mất kết nối, hết hạn, TLS, đứt giữa thân → MatKetNoi."""
    req = urllib.request.Request(goc + duong, data=json.dumps(than, ensure_ascii=False).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "X-Tram": "1", "Origin": goc})
    try:
        with (mo or mo_mac_dinh())(req, timeout=timeout) as r:
            ma, tho = r.status, r.read(TOI_DA_BYTE)
    except urllib.error.HTTPError as e:
        ma, tho = e.code, b""
        try:
            tho = e.read(TOI_DA_BYTE)
        except (OSError, ValueError, AttributeError, http.client.HTTPException):
            pass                                      # vẫn biết mã HTTP; thân hỏng thì coi như rỗng
    except (OSError, ValueError, http.client.HTTPException):
        raise MatKetNoi() from None
    try:
        d = json.loads(tho or b"{}")
    except ValueError:
        d = {}
    return ma, (d if isinstance(d, dict) else {})
