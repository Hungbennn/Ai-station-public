#!/usr/bin/env python3
"""Hook Claude Code trên MÁY A: báo nhịp phiên điều phối về trạm (spec 2 §5.5; plan 2e Task 3, G15–G19, G23).

Đọc JSON sự kiện hook từ stdin, chỉ lấy `hook_event_name` và `session_id`; gửi `POST <TRAM_DIEU_PHOI_URL>/api/
dieu-phoi/nhip` thân `{su_kien, phien}` với `phien` = 16 hex đầu của sha256(session_id). KHÔNG gửi prompt, cwd,
đường transcript. Mã: MÃ ĐIỀU PHỐI riêng (D24) trong Keychain máy A, dịch vụ `tram-dieu-phoi-ma` — không phải mã Đại
ca, không bao giờ nằm trong file, argv hay log; biến `TRAM_DIEU_PHOI_MA` chỉ để kiểm nhanh. Không bao giờ chặn phiên:
timeout mỗi thao tác (Keychain, HTTP) 2 giây, cả hook tối đa `HAN_TOAN_BO` = 4 giây rồi thoát (dưới `timeout: 5` của
settings); mọi lỗi im lặng, luôn thoát 0, không in gì (stdout của hook UserPromptSubmit/SessionStart bị đưa vào ngữ
cảnh phiên). Không dùng proxy, không theo chuyển hướng: `Authorization` chỉ tới đúng máy B. python3 ≥ 3.9 của macOS,
chỉ thư viện chuẩn."""
import hashlib
import json
import os
import subprocess
import sys
import threading
import urllib.parse
import urllib.request

SU_KIEN = ("SessionStart", "UserPromptSubmit", "Stop", "SessionEnd")
KEYCHAIN = "tram-dieu-phoi-ma"
DUONG = "/api/dieu-phoi/nhip"
TIMEOUT_GIAY = 2
HAN_TOAN_BO = 4


class KhongChuyenHuong(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None                                   # 3xx → lỗi (im lặng), không mang mã sang chỗ khác


def mo_mac_dinh():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), KhongChuyenHuong()).open


def lay_ma(env, chay=subprocess.run):
    ma = env.get("TRAM_DIEU_PHOI_MA", "").strip()
    if ma:
        return ma
    try:
        kq = chay(["/usr/bin/security", "find-generic-password", "-s", KEYCHAIN, "-w"], capture_output=True,
                  text=True, timeout=TIMEOUT_GIAY)
    except (OSError, subprocess.SubprocessError):
        return None
    return (kq.stdout.strip() or None) if kq.returncode == 0 else None


def goc_tram(url):
    """`https://<máy B>[:cổng]` không đường dẫn, query, user → gốc; còn lại None (không gửi)."""
    u = urllib.parse.urlsplit(url.strip())
    if u.scheme != "https" or not u.hostname or u.path not in ("", "/") or u.query or u.fragment or "@" in u.netloc:
        return None
    return "https://" + u.netloc


def dung_yeu_cau(goc, ma, su_kien, session_id):
    than = json.dumps({"su_kien": su_kien, "phien": hashlib.sha256(session_id.encode()).hexdigest()[:16]})
    return urllib.request.Request(goc + DUONG, data=than.encode(), method="POST", headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + ma, "X-Tram": "1", "Origin": goc})


def chay(stdin, env, mo=None, lay=lay_ma):
    try:
        vao = json.loads(stdin.read() or "{}")
        su_kien, phien = vao.get("hook_event_name"), vao.get("session_id")
        goc = goc_tram(env.get("TRAM_DIEU_PHOI_URL", ""))
        if su_kien not in SU_KIEN or not isinstance(phien, str) or not phien or goc is None:
            return 0
        ma = lay(env)
        if not ma:
            return 0
        with (mo or mo_mac_dinh())(dung_yeu_cau(goc, ma, su_kien, phien), timeout=TIMEOUT_GIAY) as r:
            r.read(1024)
    except Exception:                                 # noqa: BLE001 — trạm không với tới / lỗi gì cũng im lặng
        pass
    return 0


def chay_co_han(stdin, env, han=HAN_TOAN_BO, viec=None):
    """Hạn cho CẢ hook (review đợt 4 F14): DNS hay Keychain treo cũng không giữ phiên quá `han` giây."""
    t = threading.Thread(target=viec or chay, args=(stdin, env), daemon=True)
    t.start()
    t.join(han)
    return 0


if __name__ == "__main__":
    chay_co_han(sys.stdin, os.environ)
    os._exit(0)                                       # không chờ luồng còn treo; không có gì cần flush
