"""Extractor artifact riêng: link npm tương đối nội bộ, không ghi đè/đi qua symlink."""
import os
import shutil
import tarfile
from pathlib import Path, PurePosixPath


def giai_nen(nguon, dich, so_byte, so_entry):
    if not 0 <= so_byte <= 1024**3 or not 0 <= so_entry <= 100000:
        raise ValueError('deps-vuot-tran')
    dich = Path(dich).resolve(strict=True)
    tong, dem, da, links = 0, 0, set(), []
    with tarfile.open(fileobj=nguon, mode='r|') as t:
        for m in t:
            p = PurePosixPath(m.name)
            tong, dem = tong + m.size, dem + 1
            if p.is_absolute() or not p.parts or '..' in p.parts or str(p) != m.name.rstrip('/') or \
                    m.name in da or tong > so_byte or dem > so_entry or m.size < 0 or \
                    not (m.isfile() or m.isdir() or m.issym()):
                raise ValueError('deps-archive-khong-an-toan')
            da.add(m.name)
            q = dich / p
            if any(a.is_symlink() for a in (q, *q.parents)) or not q.parent.resolve().is_relative_to(dich):
                raise ValueError('deps-ghi-qua-link')
            q.parent.mkdir(parents=True, exist_ok=True)
            if m.issym():
                if not m.linkname or PurePosixPath(m.linkname).is_absolute():
                    raise ValueError('deps-link-tuyet-doi')
                links.append((q, m.linkname))
            elif m.isdir():
                q.mkdir(exist_ok=True)
                q.chmod(0o755)
            else:
                with q.open('xb') as f, t.extractfile(m) as src:
                    shutil.copyfileobj(src, f, 65536)
                q.chmod(0o755 if m.mode & 0o111 else 0o644)
    if (tong, dem) != (so_byte, so_entry):
        raise ValueError('deps-so-do-khong-khop')
    try:
        for q, link in links:
            os.symlink(link, q)
        for q, _ in links:
            if not q.resolve(strict=True).is_relative_to(dich):
                raise ValueError('deps-link-thoat-cay')
    except (OSError, RuntimeError):
        raise ValueError('deps-link-khong-an-toan') from None
    return tong, dem
