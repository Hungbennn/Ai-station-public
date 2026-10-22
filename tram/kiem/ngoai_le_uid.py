"""D162 thay danh sách D157/D161 bằng gốc hệ thống, gồm hai tài khoản khe B đã chốt.
Chỉ đọc đường dẫn executable từ libproc, không tin argv/comm/env. Lỗi hoặc đổi định danh đóng cổng.
"""
import ctypes
import errno
import os

from tram.kiem.bang_tien_trinh import chup_nhan, mot_nhan

GOC_APPLE = ("/System/", "/usr/libexec/", "/usr/sbin/")
GOC_GHI_DUOC = ("/System/Volumes/",)   # firmlink tới ổ Data ghi được, không phải hệ thống niêm phong
TAI_KHOAN_DA_MO = frozenset({"tram-kiem", "tram-quan-kiem", "tram-khe1", "tram-khe2"})


def duong_apple(path):
    """So nguyên chuỗi nhân trả; không resolve symlink hay sửa đường lạ thành đường được miễn."""
    return (path.startswith(GOC_APPLE) and not path.startswith(GOC_GHI_DUOC) and path == os.path.normpath(path)
            and not any(c.isspace() or c == "\x00" for c in path))


def build_macos():
    """Build của nhân đang chạy; không nhận build qua biến môi trường."""
    libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
    buf, n = ctypes.create_string_buffer(128), ctypes.c_size_t(128)
    if libc.sysctlbyname(b"kern.osversion", buf, ctypes.byref(n), None, 0) != 0:
        raise OSError(ctypes.get_errno(), "không đọc được build macOS — đo lại")
    return buf.value.decode("ascii", errors="strict")


def duong_nhan(pid):
    """proc_pidpath trả executable của kernel, không phải tên agent đặt cho argv[0]."""
    lib = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    lib.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    lib.proc_pidpath.restype = ctypes.c_int
    buf = ctypes.create_string_buffer(4096)
    n = lib.proc_pidpath(pid, buf, len(buf))
    if n <= 0 or n >= len(buf) or not buf.value.startswith(b"/"):
        raise OSError(ctypes.get_errno(), "không đọc được executable của nhân")
    return os.fsdecode(buf.value)


def con_uid(uid, chup=chup_nhan, *, ten=None, ban=None, mot=mot_nhan, duong=duong_nhan):
    """Trả tàn dư theo D162; tên không được mở vẫn đóng. Không gửi tín hiệu."""
    mien = ten in TAI_KHOAN_DA_MO
    if mien and (build_macos() if ban is None else ban) != "24G90":
        raise OSError("D162: build macOS chưa đo — đo lại trước khi mở cổng")
    con = []
    for t in chup():
        if uid not in (t.uid, t.ruid):
            continue
        if not mien or t.ppid != 1 or t.uid != uid or t.ruid != uid or t.khoa is None:
            con.append(t)
            continue
        if mot(t.pid) != t:      # đang thoát/đổi sau kill -1 → coi còn, vòng chờ chụp lại (đo 20/10)
            con.append(t)
            continue
        try:
            path = duong(t.pid)
        except OSError as e:     # ESRCH: đang thoát, nhân đã nhả executable
            if e.errno != errno.ESRCH:
                raise
            con.append(t)
            continue
        if mot(t.pid) != t:
            con.append(t)
            continue
        if not duong_apple(path):
            con.append(t)
    return con
