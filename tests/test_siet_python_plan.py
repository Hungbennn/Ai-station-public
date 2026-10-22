import hashlib
import json
from pathlib import Path
import pytest


def nguon(tmp_path):
    src = tmp_path / 'python'
    (src / 'bin').mkdir(parents=True)
    (src / 'lib/python3.12').mkdir(parents=True)
    (src / 'BUILD').write_text('20261009')
    (src / 'bin/python3.12').write_bytes(b'python-gia')
    (src / 'bin/python').symlink_to('python3.12')
    (src / 'lib/python3.12/os.py').write_bytes(b'pass\n')
    return src


def test_prefix_day_du_manifest_sha_va_root(tmp_path):
    from tram.chu.python_kiem import phan_python
    tep, ds = phan_python(nguon(tmp_path), tmp_path / 'soan')
    dich = '/usr/local/tram/toolchains/python/3.12.15-20261009'
    assert any(t.ten == dich + '/lib/python3.12/os.py' for t in ds)
    assert any(t.ten == dich + '/bin/python' for t in ds)
    mf = json.loads(next(b for p, b in tep.items() if p.name == 'python-manifest.json'))
    assert mf['phien_ban'] == '3.12.15-20261009'
    assert mf['tep']['lib/python3.12/os.py']['sha256'] == hashlib.sha256(b'pass\n').hexdigest()
    for t in ds:
        for c in t.lenh('id'):
            assert c[:2] == ['sudo', 'install']
            assert c[c.index('-o') + 1] == 'root' and c[c.index('-g') + 1] == 'wheel'
    assert mf['tep']['bin/python']['sha256'] == mf['tep']['bin/python3.12']['sha256']


def test_khong_chep_symlink_ra_nha_nguoi_khac(tmp_path):
    from tram.chu.python_kiem import phan_python
    src = nguon(tmp_path)
    (src / 'lib/ngoai').symlink_to('/etc/passwd')
    with pytest.raises(ValueError, match='ngoài prefix'):
        phan_python(src, tmp_path / 'soan')


def test_build_khac_khong_cai(tmp_path):
    from tram.chu.python_kiem import phan_python
    src = nguon(tmp_path)
    (src / 'BUILD').write_text('khac')
    with pytest.raises(ValueError, match='build'):
        phan_python(src, tmp_path / 'soan')


def test_kiem_prefix_hash_va_quyen(tmp_path):
    from tram.chu.python_kiem import phan_python
    from tram.kiem.kiem_python import kiem_prefix
    tep, ds = phan_python(nguon(tmp_path), tmp_path / 'soan')
    root = tmp_path / 'root'
    root.mkdir()
    source = tmp_path / 'soan/python'
    for p, data in tep.items():
        rel = p.relative_to(source) if p.is_relative_to(source) else Path('manifest.json')
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(0o644)
    import os
    kiem_prefix(root, chu=os.getuid(), kiem_cha=False)
    (root / 'lib/python3.12/os.py').write_bytes(b'bi sua')
    with pytest.raises(ValueError, match='digest'):
        kiem_prefix(root, chu=os.getuid(), kiem_cha=False)
    (root / 'lib/python3.12/os.py').unlink()
    (root / 'lib/python3.12/os.py').symlink_to('/etc/passwd')
    with pytest.raises(ValueError, match='chủ/quyền/loại'):
        kiem_prefix(root, chu=os.getuid(), kiem_cha=False)


def test_cong_luot_kiem_python_truoc_tien_trinh(monkeypatch, tmp_path):
    from tram.giao_viec import cong_that
    from tram.kiem.kiem_python import kiem_prefix
    seen = {}
    monkeypatch.setattr(cong_that, 'CongLuot', lambda *a, **kw: seen.update(kw))
    cong_that.dung_cong(type('PK', (), {'ten': 'tram-kiem'})(), tmp_path, cac_du_an=lambda: [])
    assert seen['quan_sat'][0] is kiem_prefix


def test_prefix_khong_co_thu_muc_rong_ghi_duoc(tmp_path):
    import os
    from tram.chu.python_kiem import phan_python
    from tram.kiem.kiem_python import kiem_prefix
    tep, _ = phan_python(nguon(tmp_path), tmp_path / 'soan')
    root, source = tmp_path / 'root', tmp_path / 'soan/python'
    for p, data in tep.items():
        rel = p.relative_to(source) if p.is_relative_to(source) else Path('manifest.json')
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(0o644)
    (root / 'chen').mkdir()
    (root / 'chen').chmod(0o777)
    with pytest.raises(ValueError, match='chủ/quyền/loại'):
        kiem_prefix(root, chu=os.getuid(), kiem_cha=False)
