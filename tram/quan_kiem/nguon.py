"""Phía 501 chỉ xuất bytes có giới hạn; nguồn git có chủ P1, env kín và tar tất định."""
import io
import os
import selectors
import stat
import tarfile
import time

from tram.giao_viec.cay_kiem import nguon_archive, loi_cau_hinh_kho, loi_dich_trong_cay
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.quan_kiem.giao_thuc import NGUON, ENV


def archive(kho, sha):
    if loi_cau_hinh_kho(kho):
        raise ValueError('kho-co-filter')
    chu, ra = [], bytearray()
    try:
        n = nguon_archive(kho, sha, chu=chu)
        het = time.monotonic() + 120
        with selectors.DefaultSelector() as sel:
            sel.register(n.p.stdout, selectors.EVENT_READ)
            while time.monotonic() < het:
                if not sel.select(min(0.2, max(0, het - time.monotonic()))):
                    continue
                b = os.read(n.p.stdout.fileno(), 65536)
                if not b:
                    break
                ra.extend(b)
                if len(ra) > NGUON:
                    raise ValueError('nguon-qua-lon')
            else:
                raise TimeoutError('nguon-qua-han')
        if n.cho(max(0, het - time.monotonic())) != 0:
            raise OSError('archive-loi')
        return bytes(ra)
    finally:
        for n in chu:
            n.p.stdout.close()
        if not thu_hoi_con_lai(chu):
            raise OSError('nguon-chua-thu-hoi')


def moi_truong(kho, sha, mt):
    if mt is None or loi_dich_trong_cay(kho, sha, mt.dich):
        raise ValueError('thieu-moi-truong-kiem')
    fd = os.open(mt.file, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as f:
        st = os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077 or st.st_size > ENV - 10240:
            raise ValueError('env-khong-kin')
        data = f.read(ENV)
    if len(data) > ENV - 10240:
        raise ValueError('env-qua-lon')
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w') as t:
        m = tarfile.TarInfo(mt.dich)
        m.size, m.mode, m.mtime = len(data), 0o600, 0
        t.addfile(m, io.BytesIO(data))
    return b.getvalue()
