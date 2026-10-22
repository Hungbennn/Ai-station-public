"""Đọc bundle từ prefix cố định, mọi cha/file root giữ, không ACL; kiểm lại bytes mỗi lượt."""
import ctypes
import errno
import os
import stat
from pathlib import Path

from tram.kiem.deps_manifest import ARCHIVES, bam, doc_manifest, kiem_manifest, ma_bundle

GOC_DEPS = Path('/usr/local/tram/deps/ben-station')


def khong_acl(p):
    c = ctypes.CDLL(None, use_errno=True)
    c.acl_get_file.argtypes, c.acl_get_file.restype = [ctypes.c_char_p, ctypes.c_int], ctypes.c_void_p
    c.acl_to_text.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ssize_t)]
    c.acl_to_text.restype, c.acl_free.argtypes = ctypes.c_void_p, [ctypes.c_void_p]
    os.lstat(p)  # phải có thật: sau đây ENOENT chỉ còn nghĩa "không có ACL"
    acl = c.acl_get_file(os.fsencode(p), 0x100)  # ACL_TYPE_EXTENDED từ sys/acl.h macOS
    if not acl:
        # macOS trả NULL + ENOENT khi path không có ACL mở rộng (đo máy B 19/10 22:40 trên /usr/local/tram).
        if ctypes.get_errno() == errno.ENOENT:
            return
        raise ValueError('deps-khong-doc-duoc-acl')
    try:
        n = ctypes.c_ssize_t()
        s = c.acl_to_text(acl, ctypes.byref(n))
        if not s:
            raise ValueError('deps-khong-doc-duoc-acl')
        try:
            if n.value:
                raise ValueError('deps-co-acl')
        finally:
            c.acl_free(s)
    finally:
        c.acl_free(acl)


def doc_root(p, tran):
    p = Path(p)
    for q in reversed(p.parents):
        st = q.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o022:
            raise ValueError('deps-cha-khong-kin')
        if q.is_relative_to(GOC_DEPS.parent) and (st.st_gid != 0 or stat.S_IMODE(st.st_mode) != 0o755):
            raise ValueError('deps-thu-muc-khac-quyen')
        khong_acl(q)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        st = os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or st.st_gid != 0 or \
                stat.S_IMODE(st.st_mode) != 0o644 or st.st_size > tran:
            raise ValueError('deps-tep-khong-kin')
        khong_acl(p)
        b = f.read(tran + 1)
    if len(b) > tran:
        raise ValueError('deps-tep-qua-lon')
    return b


def doc_bundle(p, *, doc=doc_root, nhan=None):
    p = Path(p)
    m = doc_manifest(doc(p, 65536))
    if doc is doc_root and p != GOC_DEPS / ma_bundle(m) / 'manifest.json':
        raise ValueError('deps-duong-khong-khop')
    for name in ARCHIVES:
        a = m['artifacts'][name]
        b = doc(p.parent / name, a['size'])
        if len(b) != a['size'] or bam(b) != a['sha256']:
            raise ValueError('deps-hash-khong-khop')
        if nhan is not None:
            nhan(name, b, a)
    return m


def duong_manifest(m):
    return GOC_DEPS / ma_bundle(kiem_manifest(m)) / 'manifest.json'
