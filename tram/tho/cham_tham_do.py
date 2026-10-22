"""Chấm MỘT thăm dò cách ly (V2-6b; review vòng 1 A04) — mỗi loại một bằng chứng riêng; kết luận chỉ là LÝ DO CỐ ĐỊNH,
không bao giờ chép stdout/stderr (có thể chứa token đọc được, email…). "Đạt" (bị chặn) CHỈ khi có dấu hiệu TỪ CHỐI QUYỀN
của chính đích; lỗi hạ tầng (không khởi chạy, thiếu công cụ 126/127, chết vì tín hiệu, mục tiêu không có, API không trả
lời/404/500, mã chưa phân loại) → "không kết luận", KHÔNG BAO GIỜ "bị chặn".
| loại | đạt (bị chặn) | không đạt | còn lại → không kết luận |
| doc, ghi, sua, nc, tram | mã ≠ 0, stderr "Permission denied"/"Operation not permitted" | mã 0 | |
| keychain | mã 44, stderr "could not be found" (keychain của principal không thấy mục) | mã 0 | mã khác — đo G4 |
| http | curl mã 0, HTTP 401/403 | HTTP 2xx/422 (đã qua kiểm quyền) | curl ≠ 0, 000, 404, 500… |
| ok (dương) | mã 0 | mã ≠ 0 | |
Đối chứng mục tiêu (`ThamDo.doi_chung`, chạy dưới tài khoản QUẢN LÝ trước thăm dò): đích phải tồn tại — file/thư mục
có thật, mục Keychain có trong keychain của quản lý (KHÔNG lấy mật khẩu: không `-w`), cổng DB mở được."""
import re
import socket
from collections.abc import Callable

from tram.keychain import LoiKeychain, co_muc

TU_CHOI = re.compile(r"Permission denied|Operation not permitted")
KHONG_THAY_MUC = re.compile(r"could not be found")
MA_HTTP = re.compile(r"[1-5]\d\d")


def cham(kieu: str, ma: int | None, out: str, err: str) -> tuple[str, str]:
    """(kết luận `dat` | `khong-dat` | `khong-ket-luan`, lý do cố định)."""
    if ma is None or ma < 0:
        return "khong-ket-luan", "không khởi chạy được hoặc bị tín hiệu dừng"
    if ma in (126, 127):
        return "khong-ket-luan", f"thiếu công cụ hoặc không thực thi được (mã {ma})"
    if kieu == "ok":
        return ("dat", "mã 0") if ma == 0 else ("khong-dat", f"thăm dò dương hỏng (mã {ma})")
    if kieu == "http":
        if ma != 0 or not MA_HTTP.fullmatch(out):
            return "khong-ket-luan", f"không gọi được API (curl mã {ma})"
        if out in ("401", "403"):
            return "dat", f"API từ chối (HTTP {out})"
        if out.startswith("2") or out == "422":
            return "khong-dat", f"API nhận yêu cầu (HTTP {out})"
        return "khong-ket-luan", f"API trả HTTP {out} — không chứng minh từ chối quyền"
    if ma == 0:
        return "khong-dat", "lệnh chạy được — không bị chặn"
    if kieu == "keychain":
        if ma == 44 and KHONG_THAY_MUC.search(err):
            return "dat", "keychain của principal không thấy mục (mã 44)"
        return "khong-ket-luan", f"mã {ma} chưa phân loại — đo ở G4"
    if kieu in ("doc", "ghi", "sua", "nc", "tram") and TU_CHOI.search(err):
        return "dat", f"bị từ chối quyền (mã {ma})"
    return "khong-ket-luan", f"mã {ma} không phải từ chối quyền"


def co_muc_keychain(k: str, *, chay: Callable | None = None) -> bool:
    """Đối chứng: mục `k` có trong keychain của QUẢN LÝ — qua `keychain.co_muc` (V3-1: không `-w`, có hạn, chỉ 0/44 là
    biết); không kiểm được → False ("không kết luận" ở người gọi)."""
    try:
        return co_muc(k, chay=chay)
    except LoiKeychain:
        return False


def mo_cong(dich: str, *, noi: Callable = socket.create_connection) -> bool:
    """Đối chứng: cổng `host:port` mở được từ tài khoản quản lý/trạm (hạn 3 s); lỗi → False."""
    host, _, cong = dich.rpartition(":")
    try:
        noi((host, int(cong)), timeout=3).close()
        return True
    except (OSError, ValueError):
        return False
