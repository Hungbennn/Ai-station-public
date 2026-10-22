"""Bảng tiến trình của NHÂN qua `sysctl(KERN_PROC)` (V2-0, dot7-C01) — nguồn ảnh chụp có ĐỊNH DANH SINH cho P1.
`kinfo_proc.kp_proc.p_starttime` (giây + micro giây) do nhân ghi lúc fork; số pid chỉ được cấp lại sau khi tiến trình
cũ đã chết VÀ đã được gặt, nên khoá (pid, sinh) phân biệt hai lần sống của cùng một số. CHỈ so BẰNG: `p_starttime` là
giờ tường (đổi giờ hệ thống làm lệch thứ tự) — không dùng để so trước/sau. Không tiến trình con, không phân tích chữ;
người dùng thường đọc được bảng của mọi tiến trình (`ps` dùng cùng nguồn), không gửi tín hiệu.
Bố cục `struct kinfo_proc` lấy từ SDK macOS 15.6.1 arm64 (offsetof; sizeof 648) và TỰ KIỂM ở mỗi lần đọc: dòng của chính
tiến trình này phải khớp `os.getppid/getpgrp/geteuid/getuid`. Lệch, sysctl lỗi → `OSError` — người gọi coi như KHÔNG
chụp được, không chứng minh gì."""
import ctypes
import ctypes.util
import errno
import os
import struct
from collections.abc import Callable

from tram.kiem.cay_tien_trinh import TienTrinh

CO = 648                                        # sizeof(struct kinfo_proc)
TAT_CA, MOT_PID = (1, 14, 0), (1, 14, 1)        # CTL_KERN, KERN_PROC, KERN_PROC_ALL | KERN_PROC_PID
_libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


def doc_kinfo(raw: bytes) -> list[TienTrinh]:
    if len(raw) % CO:
        raise OSError("bảng kinfo_proc sai kích thước")
    ds = []
    for i in range(0, len(raw), CO):
        giay, micro = struct.unpack_from("<qi", raw, i)                  # p_starttime: timeval ở đầu kp_proc
        (pid,) = struct.unpack_from("<i", raw, i + 40)                   # kp_proc.p_pid
        ppid, pgid = struct.unpack_from("<ii", raw, i + 560)             # kp_eproc.e_ppid, e_pgid
        (ruid,) = struct.unpack_from("<I", raw, i + 392)                 # kp_eproc.e_pcred.p_ruid
        (uid,) = struct.unpack_from("<I", raw, i + 420)                  # kp_eproc.e_ucred.cr_uid
        ds.append(TienTrinh(pid, ppid, pgid, uid, ruid, giay * 1_000_000 + micro))
    return ds


def _sysctl(mib: tuple[int, ...]) -> bytes:
    m = (ctypes.c_int * len(mib))(*mib)
    for _ in range(5):
        n = ctypes.c_size_t(0)
        if _libc.sysctl(m, len(mib), None, ctypes.byref(n), None, 0) != 0:
            raise OSError(ctypes.get_errno(), "sysctl: không đọc được kích thước bảng")
        n.value += 32 * CO                                               # bảng có thể lớn thêm giữa hai lần gọi
        buf = ctypes.create_string_buffer(n.value)
        if _libc.sysctl(m, len(mib), buf, ctypes.byref(n), None, 0) == 0:
            return buf.raw[: n.value]
        if ctypes.get_errno() != errno.ENOMEM:
            raise OSError(ctypes.get_errno(), "sysctl: không đọc được bảng tiến trình")
    raise OSError(errno.ENOMEM, "sysctl: bảng tiến trình đổi liên tục")


def _tu_kiem(ds: list[TienTrinh]) -> None:
    toi = [t for t in ds if t.pid == os.getpid()]
    if len(toi) != 1 or (toi[0].ppid, toi[0].pgid, toi[0].uid, toi[0].ruid) != (
            os.getppid(), os.getpgrp(), os.geteuid(), os.getuid()):
        raise OSError("bố cục kinfo_proc không khớp tiến trình này — không tin ảnh chụp")


def chup_nhan(*, doc: Callable[[tuple[int, ...]], bytes] = _sysctl) -> list[TienTrinh]:
    """Toàn bộ bảng tiến trình trong MỘT lần gọi sysctl, đã tự kiểm bố cục."""
    ds = doc_kinfo(doc(TAT_CA))
    _tu_kiem(ds)
    return ds


def mot_nhan(pid: int, *, doc: Callable[[tuple[int, ...]], bytes] = _sysctl) -> TienTrinh | None:
    """Dòng của MỘT pid ngay lúc gọi (đọc pid đích TRƯỚC, tự kiểm sau); None khi không còn tiến trình mang số đó."""
    if pid <= 0:
        raise ValueError("pid phải dương")
    ds = doc_kinfo(doc((*MOT_PID, pid)))
    _tu_kiem(doc_kinfo(doc((*MOT_PID, os.getpid()))))
    if len(ds) > 1 or (ds and ds[0].pid != pid):
        raise OSError("sysctl trả dòng lạ cho một pid")
    return ds[0] if ds else None


def van_o_nhom(ds: list[TienTrinh], g: int, *, mot: Callable[[int], TienTrinh | None] = mot_nhan) -> bool:
    """Một thành viên đã thấy vẫn là ĐÚNG lần sống đó và vẫn ở `g` tại lúc đọc. Đây chỉ là kiểm tra để giảm tín hiệu
    thừa, không nguyên tử với lúc gửi; phạm vi gửi do `kill_uid` giới hạn (A01). Lỗi đọc → False."""
    for t in ds:
        try:
            moi = mot(t.pid)
        except (OSError, ValueError):
            return False
        if t.khoa is not None and moi is not None and moi.khoa == t.khoa and moi.pgid == g:
            return True
    return False


def phien_khoi_dong() -> str:
    """`kern.bootsessionuuid` — đổi sau mỗi lần khởi động máy; pid/sinh của phiên khác không còn tiến trình nào."""
    n = ctypes.c_size_t(64)
    buf = ctypes.create_string_buffer(n.value)
    if _libc.sysctlbyname(b"kern.bootsessionuuid", buf, ctypes.byref(n), None, 0) != 0 or not buf.value:
        raise OSError(ctypes.get_errno(), "sysctl: không đọc được phiên khởi động")
    return buf.value.decode("ascii")
