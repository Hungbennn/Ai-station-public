"""Chỉ gọi dưới tram-kiem + boc_luot; Uq không phân tích archive."""
import os
import sys
import tarfile
from pathlib import Path, PurePosixPath


def giai_nen(nguon, dich):
    with tarfile.open(fileobj=nguon, mode='r|') as t:
        tong, dem, da = 0, 0, set()
        for m in t:
            p = PurePosixPath(m.name)
            tong, dem = tong + m.size, dem + 1
            if p.is_absolute() or '..' in p.parts or '.git' in p.parts or m.name in da or \
                    tong > 256 * 1024 * 1024 or dem > 100000 or not (m.isfile() or m.isdir() or m.issym()):
                raise ValueError('archive-khong-an-toan')
            if m.issym() and (PurePosixPath(m.linkname).is_absolute() or '..' in PurePosixPath(m.linkname).parts):
                raise ValueError('link-khong-an-toan')
            da.add(m.name)
            t.extract(m, dich, filter='data')


def nhan_env(nguon, goc, ten):
    rel = PurePosixPath(ten)
    if rel.is_absolute() or not rel.parts or '..' in rel.parts or str(rel) != ten:
        raise ValueError('env-dich-sai')
    with tarfile.open(fileobj=nguon, mode='r|') as t:
        m = t.next()
        if m is None or m.name != ten or not m.isfile() or not 0 <= m.size <= 1024 * 1024:
            raise ValueError('env-khong-dung-mot-file')
        data = t.extractfile(m).read(1024 * 1024 + 1)
        if len(data) != m.size or t.next() is not None:
            raise ValueError('env-khong-dung-mot-file')
    p, goc = Path(goc) / rel, Path(goc).resolve(strict=True)
    if not p.parent.resolve(strict=True).is_relative_to(goc) or any(q.is_symlink() for q in (p, *p.parents)) or \
            os.path.lexists(p):
        raise ValueError('env-dich-da-co-hoac-link')
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        nhan_env(sys.stdin.buffer, Path(sys.argv[1]), sys.argv[2])
    else:
        giai_nen(sys.stdin.buffer, Path(sys.argv[1]))
