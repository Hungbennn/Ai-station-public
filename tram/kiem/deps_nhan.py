"""Helper tin cậy, chỉ thực thi dưới 503 + hồ sơ; không nạp mã của repo để kiểm lock."""
import os
from pathlib import Path

from tram.kiem.deps_manifest import bam, nen_tang


def kiem_cay(wt, m):
    if nen_tang() != m['runtime']:
        raise ValueError('deps-runtime-khong-khop')
    wt = Path(wt).resolve(strict=True)
    front = wt / 'frontend'
    if front.is_symlink() or not front.is_dir():
        raise ValueError('deps-frontend-khong-phai-thu-muc-that')
    for rel, digest in m['nguon'].items():
        p = wt / rel
        if p.is_symlink() or not p.resolve(strict=True).is_relative_to(wt) or bam(p.read_bytes()) != digest:
            raise ValueError('deps-nguon-khong-khop')
    for rel in ('.venv', 'frontend/node_modules'):
        if os.path.lexists(wt / rel):
            raise ValueError('deps-dich-da-co')
