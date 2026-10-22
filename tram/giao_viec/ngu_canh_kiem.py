"""Ngữ cảnh vận hành của quan sát launchd (3C-D7, review đợt 9 vòng 1 mục 4): bằng chứng G3.9 ("launchd từ chối
tram-kiem ghi vào miền đăng nhập của người gọi sudo") chỉ có giá trị đúng ngữ cảnh đã đo — bản macOS, máy, UID
`tram-kiem`, UID trạm, và loại phiên của người gọi (tiến trình dưới sudo kế thừa audit session của trạm, G3:
`procinfo` → `audit info → session id`). TRẠM tự đọc từ OS, không qua env hay lời `tram-kiem`: build từ
`SystemVersion.plist` (của root), máy = sha256 của `gethostuuid` (16 ký tự đầu — không ghi UUID thô vào mã), loại
phiên = cờ `sessionHasGraphicAccess` của `SessionGetInfo(callerSecuritySession)` (Security.framework). Đọc lỗi →
`OSError`/`ValueError`; người gọi đóng cổng. Không dùng số asid (đổi mỗi lần đăng nhập)."""
import ctypes
import hashlib
import os
import plistlib
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.danh_tinh import uid_cua

SYS_VER = Path("/System/Library/CoreServices/SystemVersion.plist")
SECURITY = "/System/Library/Frameworks/Security.framework/Security"
CO_DO_HOA = 0x0010                                   # sessionHasGraphicAccess (AuthSession.h)


@dataclass(frozen=True)
class NguCanh:
    ban: str            # ProductBuildVersion
    may: str            # sha256(gethostuuid)[:16]
    uid_kiem: int
    uid_tram: int
    do_hoa: bool        # người gọi sudo ở phiên có đồ hoạ (Aqua) hay phiên nền


def ban_macos(tep: Path = SYS_VER) -> str:
    with open(tep, "rb") as f:
        ban = plistlib.load(f).get("ProductBuildVersion")
    if not isinstance(ban, str) or not ban.isalnum():
        raise ValueError("ProductBuildVersion không hợp lệ")
    return ban


def ma_may() -> str:
    buf, han = (ctypes.c_ubyte * 16)(), (ctypes.c_long * 2)(1, 0)
    if ctypes.CDLL(None).gethostuuid(buf, han) != 0:
        raise OSError("gethostuuid lỗi")
    return hashlib.sha256(bytes(buf)).hexdigest()[:16]


def phien_do_hoa() -> bool:
    sid, cot = ctypes.c_uint32(), ctypes.c_uint32()
    if ctypes.CDLL(SECURITY).SessionGetInfo(ctypes.c_int32(-1), ctypes.byref(sid), ctypes.byref(cot)) != 0:
        raise OSError("SessionGetInfo lỗi")
    return bool(cot.value & CO_DO_HOA)


def ngu_canh_hien_hanh(ten_kiem: str) -> NguCanh:
    """Ngữ cảnh lúc này; `KeyError` khi không có tài khoản `ten_kiem`."""
    return NguCanh(ban_macos(), ma_may(), uid_cua(ten_kiem), os.getuid(), phien_do_hoa())
