"""Bundle nhỏ trong tmp; không đọc/ghi kho root thật trong unit test."""
import json
from pathlib import Path
from test_phu_thuoc_kiem import archive, mau
from tram.kiem.deps_manifest import bam, ma_bundle
from tram.kiem.deps_root import doc_bundle


def bundle(tmp_path, monkeypatch, nguon):
    import tram.tho.deps_b as d
    import tram.quan_kiem.cap_deps as c
    m = mau()
    m['nguon'] = nguon
    blobs = {'python-site.tar': archive([('thu_vien.py', 'file', b'x=1\n')]),
             'node-modules.tar': archive([('vue/package.json', 'file', b'{}')])}
    for name, b in blobs.items():
        m['artifacts'][name] = {'sha256': bam(b), 'size': len(b),
                                'bytes': 4 if name == 'python-site.tar' else 2, 'entries': 1}
    root = tmp_path / 'bundle' / ma_bundle(m)
    root.mkdir(parents=True)
    (root / 'manifest.json').write_text(json.dumps(m))
    for name, b in blobs.items():
        (root / name).write_bytes(b)
    monkeypatch.setattr(d, 'GOC_DEPS', root.parent)
    monkeypatch.setattr(d, 'doc_root', lambda p, n: Path(p).read_bytes())
    monkeypatch.setattr(c, 'duong_manifest', lambda m: root / 'manifest.json')
    monkeypatch.setattr(c, 'doc_bundle', lambda p, nhan: doc_bundle(p, doc=lambda p, n: p.read_bytes(), nhan=nhan))
    return root, m
