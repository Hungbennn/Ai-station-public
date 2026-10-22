"""Soạn toàn prefix Python offline; mỗi file có SHA và tài nguyên R2 riêng, không chạy nguồn."""
import hashlib
import json
from pathlib import Path

from tram.chu.cai_dat_kiem import tep_root
from tram.chu.tai_nguyen import TaiNguyen
from tram.kiem.toolchain import PYTHON

BAN = '3.12.15-20261009'


def phan_python(nguon: Path, soan: Path) -> tuple[dict, list]:
    nguon = nguon.resolve(strict=True)
    if (nguon / 'BUILD').read_text().strip() != '20261009' or not (nguon / 'bin/python3.12').is_file():
        raise ValueError('Python khác build đã ghim — không cài')
    tep, ds, muc = {}, [], {}
    dich = Path(PYTHON)
    thu_muc = {dich, *[p for p in dich.parents if str(p).startswith('/usr/local/tram')]}
    for p in sorted(nguon.rglob('*')):
        that = p.resolve(strict=True)
        if not that.is_relative_to(nguon):
            raise ValueError('symlink ra ngoài prefix — không cài')
        if p.is_dir():
            if p.is_symlink():
                raise ValueError('symlink thư mục chưa hỗ trợ — không cài')
            thu_muc.add(dich / p.relative_to(nguon))
            continue
        if not p.is_file():
            raise ValueError('prefix chứa tài nguyên không phải file — không cài')
        ten = p.relative_to(nguon).as_posix()
        data = p.read_bytes()
        if data.startswith(b'#!'):
            data = data.replace(str(nguon).encode(), PYTHON.encode())
        mode = '0755' if p.stat().st_mode & 0o111 else '0644'
        muc[ten] = {'sha256': hashlib.sha256(data).hexdigest(), 'mode': mode}
        tam = soan / 'python' / ten
        tep[tam] = data
        ds.append(tep_root(tam, dich / ten, data, mode))
    mf = (json.dumps({'phien_ban': BAN, 'tep': muc}, sort_keys=True, indent=1) + '\n').encode()
    tam = soan / 'python-manifest.json'
    tep[tam] = mf
    ds.append(tep_root(tam, dich / 'manifest.json', mf, '0644'))
    dirs = [TaiNguyen('thu_muc', str(p), lambda i, p=p: [
        ['sudo', 'install', '-d', '-o', 'root', '-g', 'wheel', '-m', '0755', str(p)]], lambda i: {'uid': 0})
        for p in sorted(thu_muc, key=lambda p: (len(p.parts), str(p)))]
    return tep, dirs + ds
