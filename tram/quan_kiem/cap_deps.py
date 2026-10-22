"""Uq chỉ đọc root artifact rồi chuyển bytes; helper 503 kiểm nguồn/nhận vào đích cố định."""
import inspect
from pathlib import Path

from tram.giao_viec.ban_chep import _chay
from tram.kiem import deps_manifest, deps_nhan, deps_tar
from tram.kiem.deps_manifest import KHOA_NGUON, chuan
from tram.kiem.deps_root import doc_bundle, duong_manifest
from tram.kiem.toolchain import PYTHON


def kiem_dich_env(dich):
    for p in (*KHOA_NGUON, '.venv', 'frontend/node_modules', 'manifest.json'):
        if dich == p or dich.startswith(p + '/') or p.startswith(dich + '/'):
            raise ValueError('deps-env-de-dich-bao-ve')


def cap_deps(wt, m, *, boc, kill, chay=_chay):
    # Chỉ lấy helper từ bundle mã root đã cài, không đọc/import Python trong cây LUOT.
    script = (Path(deps_manifest.__file__).read_text() + '\n' + Path(deps_tar.__file__).read_text() +
              '\n' + inspect.getsource(deps_nhan.kiem_cay))
    def helper(body, *args, **kw):
        a = [f'{PYTHON}/bin/python3.12', '-I', '-c', script + '\n' + body, str(wt), chuan(m).decode(), *args]
        chay(boc(a), kill=kill, check=True, timeout=300, **kw)
    helper('kiem_cay(Path(sys.argv[1]), json.loads(sys.argv[2]))')
    chay(boc([f'{PYTHON}/bin/python3.12', '-I', '-m', 'venv', '--without-pip', str(wt / '.venv')]),
         kill=kill, check=True, timeout=300)
    def nhan(name, b, a):
        body = '''
wt, m, name = Path(sys.argv[1]), json.loads(sys.argv[2]), sys.argv[3]
rel = '.venv/lib/python3.12/site-packages' if name == 'python-site.tar' else 'frontend/node_modules'
dich = wt / rel
if dich.is_symlink() or dich.exists() and (not dich.is_dir() or any(dich.iterdir())):
    raise ValueError('deps-dich-khong-trong')
dich.mkdir(parents=True, exist_ok=True)
a = m['artifacts'][name]
giai_nen(sys.stdin.buffer, dich, a['bytes'], a['entries'])
'''
        helper(body, name, input=b)
    that = doc_bundle(duong_manifest(m), nhan=nhan)
    if that != m:
        raise ValueError('deps-manifest-root-da-doi')
