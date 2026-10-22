"""Kiểm toàn prefix Python root giữ, so digest trước cổng; không thực thi file đang kiểm."""
import hashlib
import json
import os
import stat
from pathlib import Path

from tram.kiem.toolchain import PYTHON


def _an_toan(p: Path, chu: int, thu_muc: bool = False) -> None:
    st = p.lstat()
    dung = stat.S_ISDIR(st.st_mode) if thu_muc else stat.S_ISREG(st.st_mode)
    if not dung or st.st_uid != chu or st.st_mode & 0o022:
        raise ValueError('Python kiểm sai chủ/quyền/loại — cài lại')


def kiem_prefix(goc: Path = Path(PYTHON), *, chu: int = 0, kiem_cha: bool = True) -> None:
    for p in (goc, *(goc.parents if kiem_cha else ())):
        _an_toan(p, chu, True)
    mf = goc / 'manifest.json'
    _an_toan(mf, chu)
    if mf.stat().st_size > 4_000_000:
        raise ValueError('manifest Python quá lớn')
    m = json.loads(mf.read_bytes())
    if set(m) != {'phien_ban', 'tep'} or m['phien_ban'] != '3.12.15-20261009' or not isinstance(m['tep'], dict):
        raise ValueError('manifest Python khác bản ghim')
    if not {'bin/python3.12', 'bin/python', 'lib/python3.12/os.py'}.issubset(m['tep']):
        raise ValueError('manifest Python thiếu prefix đầy đủ')
    for ten, expected in m['tep'].items():
        rel = Path(ten)
        if rel.is_absolute() or '..' in rel.parts or str(rel) != ten:
            raise ValueError('manifest Python sai đường')
        p = goc / rel
        for cha in p.parents:
            if cha == goc:
                break
            _an_toan(cha, chu, True)
        _an_toan(p, chu)
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as f:
            st = os.fstat(f.fileno())
            if st.st_uid != chu or st.st_mode & 0o022 or not stat.S_ISREG(st.st_mode):
                raise ValueError('Python kiểm đổi định danh')
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        if digest != expected['sha256']:
            raise ValueError('Python kiểm sai digest — cài lại')
    thuc = set()
    for p in goc.rglob('*'):
        _an_toan(p, chu, p.is_dir())
        if not p.is_dir():
            thuc.add(p.relative_to(goc).as_posix())
    if thuc != set(m['tep']) | {'manifest.json'}:
        raise ValueError('Python kiểm có file ngoài manifest — cài lại')
