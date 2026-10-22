"""Tích hợp cục bộ bằng pin/principal giả; không phải bằng chứng Seatbelt/macOS G4."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from test_phu_thuoc_kiem import mau


def test_hai_luot_import_pytest_fastapi_native_tu_ban_rieng(tmp_path, monkeypatch):
    import tram.quan_kiem.cap_deps as cap
    from tram.chu.soan_phu_thuoc import chup
    from tram.kiem.deps_manifest import nen_tang
    stage = tmp_path / 'site'
    stage.mkdir()
    site = Path(sys.executable).parent.parent / 'lib/python3.12/site-packages'
    names = ('pytest', '_pytest', 'pluggy', 'iniconfig', 'packaging', 'pygments', 'py.py',
             'fastapi', 'starlette', 'pydantic', 'pydantic_core', 'annotated_types', 'annotated_doc',
             'typing_extensions.py', 'typing_inspection', 'anyio', 'idna', 'sniffio',
             'opentelemetry', 'deprecated', 'wrapt', 'importlib_metadata', 'zipp')
    for name in names:
        p = site / name
        if p.is_dir():
            shutil.copytree(p, stage / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        elif p.is_file():
            shutil.copy(p, stage / name)
    for p in site.glob('*.dist-info'):
        if p.name.startswith(('opentelemetry_', 'importlib_metadata', 'zipp', 'wrapt', 'deprecated')):
            shutil.copytree(p, stage / p.name)
    node = tmp_path / 'node'
    node.mkdir()
    (node / 'vite.js').write_text('fixture')
    m, blobs = mau(), {}
    m['runtime'] = nen_tang()
    for name, src in [('python-site.tar', stage), ('node-modules.tar', node)]:
        p = tmp_path / name
        m['artifacts'][name] = chup(src, p, python=name.startswith('python'))
        blobs[name] = p.read_bytes()
    # Pin production đã có test riêng; test cục bộ dùng interpreter dev, vẫn mang audithook.
    monkeypatch.setattr(cap, 'PYTHON', str(Path(sys.executable).parent.parent))
    monkeypatch.setattr(cap, 'duong_manifest', lambda m: tmp_path / 'manifest')
    def root(p, nhan):
        for name, b in blobs.items():
            nhan(name, b, m['artifacts'][name])
        return m
    monkeypatch.setattr(cap, 'doc_bundle', root)
    def chay(argv, **kw):
        kw.pop('kill')
        kw['timeout'] = 60
        return subprocess.run([a for a in argv if a != '-I'], capture_output=True, **kw)
    for ten in ('mot', 'hai'):
        wt = tmp_path / ten
        (wt / 'frontend').mkdir(parents=True)
        for name in m['nguon']:
            p = wt / name
            p.write_bytes(name.encode())
        (wt / 'tram').mkdir()
        (wt / 'tram/__init__.py').write_text('')
        cap.cap_deps(wt, m, boc=lambda a: a, kill=lambda *a: None, chay=chay)
        script = '''import pathlib, pytest, fastapi, pydantic_core, tram
w = pathlib.Path.cwd()
assert pathlib.Path(tram.__file__).parent.parent == w
for x in (pytest, fastapi, pydantic_core):
    assert pathlib.Path(x.__file__).is_relative_to(w / '.venv')
assert pydantic_core.to_json({'ok': True}) == b'{"ok":true}'
'''
        r = subprocess.run([str(wt / '.venv/bin/python'), '-B', '-c', script], cwd=wt,
                           env=dict(os.environ, PYTHONPATH=os.environ['PYTHONPATH'] + ':' + str(wt)),
                           capture_output=True, timeout=60)
        assert r.returncode == 0, r.stderr.decode()[-1500:]
        if ten == 'mot':
            (wt / '.venv/lib/python3.12/site-packages/fastapi/__init__.py').write_text('broken')
            (wt / 'frontend/node_modules/vite.js').write_text('broken')
    assert (tmp_path / 'hai/frontend/node_modules/vite.js').read_text() == 'fixture'
