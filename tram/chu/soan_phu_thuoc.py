"""Chụp staging sạch đã sync offline; không chạy installer/build hook, không chuyển nguyên venv."""
import configparser
import hashlib
import json
import os
import tarfile
from pathlib import Path

from tram.chu.cai_dat import KeHoach
from tram.kiem.deps_manifest import KHOA_NGUON, bam, chuan, kiem_manifest
from tram.kiem.toolchain import PYTHON, UV, NODE, NPM


def do_cong_cu():
    from tram.kiem.lenh_ngan import chay_ngan
    import tram.kiem.deps_manifest as mf
    script = Path(mf.__file__).read_text() + '\nprint(json.dumps(nen_tang()))\n'
    def doc(a):
        ma, b = chay_ngan(a, timeout=30, doc=True)
        if ma != 0:
            raise ValueError('deps-khong-do-duoc-cong-cu')
        return b.decode().strip()
    r = json.loads(doc([f'{PYTHON}/bin/python3.12', '-I', '-c', script]))
    # npm là script dùng env node; chọn đúng Node ghim, không lấy từ PATH của người vận hành.
    c = {'uv': doc([f'{UV}/bin/uv', '--version']).split()[1],
         'node': doc([f'{NODE}/bin/node', '--version']).removeprefix('v'),
         'npm': doc([f'{NODE}/bin/node', f'{NPM}/bin/npm-cli.js', '--version'])}
    return r, c


def chup(goc, dich, *, python=False):
    goc = Path(goc)
    if goc.is_symlink() or not goc.is_dir():
        raise ValueError('deps-nguon-khong-phai-thu-muc-that')
    goc = goc.resolve(strict=True)
    tong, dem = 0, 0
    with tarfile.open(dich, 'x', format=tarfile.PAX_FORMAT, dereference=False) as t:
        for p in sorted(goc.rglob('*')):
            rel = p.relative_to(goc)
            if '__pycache__' in rel.parts or p.suffix == '.pyc' or python and rel.parts[0] in (
                    '_virtualenv.pth', '_virtualenv.py'):
                continue
            if python and (rel.parts[0] == 'tram' or rel.parts[0].startswith(('ben_station', '_editable'))):
                raise ValueError('deps-chua-ma-du-an')
            if p.is_symlink() and (python or os.path.isabs(os.readlink(p))):
                raise ValueError('deps-link-khong-an-toan')
            if not p.resolve(strict=True).is_relative_to(goc) or not (p.is_dir() or p.is_file()):
                raise ValueError('deps-link-thoat-hoac-loai-sai')
            if python and p.suffix == '.pth' and any(
                    d.strip() and not d.lstrip().startswith('#') for d in p.read_text().splitlines()):
                raise ValueError('deps-pth-khong-an-toan')
            if python and p.name == 'direct_url.json':
                url = json.loads(p.read_bytes())
                if url.get('dir_info', {}).get('editable') or str(url.get('url', '')).startswith('file:'):
                    raise ValueError('deps-editable-hoac-url-cuc-bo')
            m = t.gettarinfo(str(p), arcname=rel.as_posix())
            m.uid, m.gid, m.uname, m.gname, m.mtime = 0, 0, '', '', 0
            m.mode = 0o755 if p.is_dir() or m.mode & 0o111 else 0o644
            tong, dem = tong + m.size, dem + 1
            if tong > 1024**3 or dem > 100000:
                raise ValueError('deps-vuot-tran')
            if m.isfile():
                with p.open('rb') as f:
                    t.addfile(m, f)
            else:
                t.addfile(m)
    with Path(dich).open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    return dict(sha256=digest, size=Path(dich).stat().st_size, bytes=tong, entries=dem)


def lap_soan(nguon, commit, venv, node_modules, dich):
    r, c = do_cong_cu()
    cfg = configparser.ConfigParser()
    cfg.read_string('[venv]\n' + (venv / 'pyvenv.cfg').read_text())
    if Path(cfg['venv']['home']).resolve() != Path(PYTHON) / 'bin':
        raise ValueError('deps-venv-khac-pin')
    site = venv / 'lib/python3.12/site-packages'
    m = dict(v=1, du_an='ben-station', commit=commit, nguon={k: bam((nguon / k).read_bytes()) for k in KHOA_NGUON},
             runtime=r, cong_cu=c, python_groups=['dev'],
             npm_flags=['--ignore-scripts', '--include=dev', '--no-audit', '--no-fund'])
    def soan():
        dich.mkdir(mode=0o700)  # độc quyền: lỗi giữ staging để xem, không ghi đè bản đã soạn
        m['artifacts'] = {'python-site.tar': chup(site, dich / 'python-site.tar', python=True),
                          'node-modules.tar': chup(node_modules, dich / 'node-modules.tar')}
        kiem_manifest(m)
        (dich / 'manifest.json').write_bytes(chuan(m))
    return KeHoach({}, [], [f'Chụp staging đã dựng sạch đúng lock; manifest: {dich / "manifest.json"}',
                            json.dumps(m, ensure_ascii=False)], [('Soạn hai archive và manifest', soan)])
