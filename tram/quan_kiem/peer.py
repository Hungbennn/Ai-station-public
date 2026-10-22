"""macOS getpeereid: nhân cung cấp euid/egid; không nhận danh tính từ JSON."""
import ctypes
import os
import stat
from pathlib import Path


def danh_tinh(s):
    lib = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    u, g = ctypes.c_uint(), ctypes.c_uint()
    lib.getpeereid.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
    lib.getpeereid.restype = ctypes.c_int
    if lib.getpeereid(s.fileno(), ctypes.byref(u), ctypes.byref(g)):
        raise OSError('khong-doc-duoc-peer')
    return u.value, g.value


def xac_thuc(s, uid, *, lay=danh_tinh):
    if type(uid) is not int or uid <= 0 or lay(s)[0] != uid:
        raise PermissionError('peer-sai')


def duong_socket(p: Path, uid: int, gid: int):
    for cha in p.parents:
        st = cha.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid not in (0, uid) or st.st_mode & 0o022:
            raise PermissionError('cha-socket-sai')
    st = p.lstat()
    if not stat.S_ISSOCK(st.st_mode) or st.st_uid != uid or st.st_gid != gid or stat.S_IMODE(st.st_mode) != 0o660:
        raise PermissionError('socket-sai')
