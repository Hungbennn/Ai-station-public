import json
import os
from pathlib import Path

import pytest

from test_phu_thuoc_kiem import archive, mau
from tram.kiem.deps_manifest import ARCHIVES, bam, chuan, ma_bundle


def goi(tmp_path):
    root = tmp_path / 'goi'
    root.mkdir()
    m = mau()
    for name in ARCHIVES:
        b = archive([('x', 'file', b'x')])
        (root / name).write_bytes(b)
        m['artifacts'][name] = dict(sha256=bam(b), size=len(b), bytes=1, entries=1)
    (root / 'manifest.json').write_bytes(chuan(m))
    return root, m


def test_soan_khong_mang_pyc_uv_hook_va_bin(tmp_path, monkeypatch):
    import tram.chu.soan_phu_thuoc as s
    from tram.kiem.deps_manifest import KHOA_NGUON
    src, venv = tmp_path / 'src', tmp_path / 'venv'
    site, node = venv / 'lib/python3.12/site-packages', src / 'frontend/node_modules'
    site.mkdir(parents=True)
    node.mkdir(parents=True)
    for name in KHOA_NGUON:
        (src / name).write_text('lock')
    (venv / 'pyvenv.cfg').write_text('home = /usr/local/tram/toolchains/python/3.12.15-20261009/bin\n')
    (site / 'fastapi.py').write_text('x = 1')
    (site / '_virtualenv.pth').write_text('import _virtualenv')
    (site / 'a.pyc').write_bytes(b'pyc')
    (node / 'vite.js').write_text('js')
    monkeypatch.setattr(s, 'do_cong_cu', lambda: (mau()['runtime'], mau()['cong_cu']))
    out = tmp_path / 'out'
    kh = s.lap_soan(src, 'a' * 40, venv, node, out)
    assert not out.exists()
    for _, f in kh.buoc:
        f()
    import tarfile
    with tarfile.open(out / 'python-site.tar') as t:
        assert t.getnames() == ['fastapi.py']
    assert json.loads((out / 'manifest.json').read_bytes())['nguon']['uv.lock'] == bam(b'lock')


@pytest.mark.parametrize('name,data', [('evil.pth', '/Users/test/cache'),
    ('evil.pth', 'import os'), ('tram/__init__.py', ''),
    ('x.dist-info/direct_url.json', '{"dir_info":{"editable":true}}'),
    ('x.dist-info/direct_url.json', '{"url":"file:///Users/test/cache/x.whl"}')])
def test_snapshot_python_khong_editable_pth_ma_du_an(tmp_path, name, data):
    from tram.chu.soan_phu_thuoc import chup
    p = tmp_path / 'site'
    (p / name).parent.mkdir(parents=True)
    (p / name).write_text(data)
    with pytest.raises(ValueError):
        chup(p, tmp_path / 'x.tar', python=True)


def test_cai_r2_khong_goi_lenh_truoc_dong_y(tmp_path, monkeypatch):
    from tram.chu.cai_phu_thuoc import lap_cai
    from tram.chu.so_cai_tho import SoCai
    root, m = goi(tmp_path)
    monkeypatch.setenv('TRAM_HOME', str(tmp_path / 'home'))
    kh = lap_cai(root, SoCai(tmp_path / 'so'), quan_sat=lambda *a, **kw: None)
    assert not (tmp_path / 'so').exists()
    assert sum(' tep ' in t for t, _ in kh.buoc) == 3
    assert any(f'/ben-station/{ma_bundle(m)}/manifest.json' in t for t, _ in kh.buoc)
    assert kh.lenh == []


def test_cai_bundle_da_co_khac_bytes_khong_thay_tai_cho(tmp_path, monkeypatch):
    from tram.chu.cai_phu_thuoc import lap_cai
    from tram.chu.so_cai_tho import SoCai
    root, _ = goi(tmp_path)
    monkeypatch.setenv('TRAM_HOME', str(tmp_path / 'home'))
    with pytest.raises(ValueError):
        lap_cai(root, SoCai(tmp_path / 'so'), quan_sat=lambda *a, **kw: {'uid': 0, 'sha256': 'wrong'})


def test_doc_bundle_root_kiem_chu_quyen_hash(tmp_path):
    from tram.kiem.deps_root import doc_bundle
    root, m = goi(tmp_path)
    for p in root.iterdir():
        p.chmod(0o644)
    read = lambda p, n: p.read_bytes() if p.stat().st_uid == os.getuid() and p.stat().st_mode & 0o022 == 0 else (
        (_ for _ in ()).throw(ValueError('chu-quyen')))
    assert doc_bundle(root / 'manifest.json', doc=read) == m
    (root / ARCHIVES[0]).write_bytes(b'bad')
    with pytest.raises(ValueError):
        doc_bundle(root / 'manifest.json', doc=read)
    (root / ARCHIVES[0]).chmod(0o666)
    with pytest.raises(ValueError):
        doc_bundle(root / 'manifest.json', doc=read)


@pytest.mark.parametrize('uid,mode,size', [(503, 0o100644, 1), (0, 0o100666, 1),
    (0, 0o120644, 1), (0, 0o100644, 100001)])
def test_doc_root_tu_choi_chu_quyen_loai_kich_thuoc(tmp_path, monkeypatch, uid, mode, size):
    from types import SimpleNamespace
    import tram.kiem.deps_root as r
    p = tmp_path / 'tep'
    p.write_bytes(b'x')
    monkeypatch.setattr(Path, 'lstat', lambda *a, **kw: SimpleNamespace(st_uid=0, st_mode=0o40755))
    monkeypatch.setattr(r, 'khong_acl', lambda p: None)
    monkeypatch.setattr(r.os, 'fstat', lambda fd: SimpleNamespace(st_uid=uid, st_gid=0, st_mode=mode, st_size=size))
    with pytest.raises(ValueError):
        r.doc_root(p, 65536)


def test_cli_khong_dong_y_khong_thuc_hien(tmp_path, monkeypatch):
    import tram.chu.phu_thuoc_kiem as c
    from tram.chu.cai_dat import KeHoach
    calls = []
    monkeypatch.setattr(c, 'lap_cai', lambda *a: KeHoach({}, [], [], [('cai', lambda: calls.append(1))]))
    assert c.main(['cai', '--goi', str(tmp_path)], hoi=lambda _: 'khong') == 1
    assert calls == []


def test_r2_crash_giu_da_tao_khong_tao_phan_sau(tmp_path, monkeypatch):
    from tram.chu.cai_phu_thuoc import lap_cai
    from tram.chu.cai_dat import thuc_hien
    from tram.chu.so_cai_tho import SoCai
    from tram.chu.tai_nguyen import LoiCaiDat
    import tram.chu.soan_phu_thuoc as s
    root, m = goi(tmp_path)
    monkeypatch.setattr(s, 'do_cong_cu', lambda: (m['runtime'], m['cong_cu']))
    monkeypatch.setenv('TRAM_HOME', str(tmp_path / 'home'))
    so, state, calls = SoCai(tmp_path / 'so'), {}, []
    def qs(k, n, **kw):
        return state.get(n)
    def run(a, **kw):
        assert any(x.su == 'du_dinh' and x.ten == a[-1] for x in so.muc().values())
        calls.append(a)
        if 'python-site.tar' in a[-1]:
            raise OSError('crash')
        p = Path(a[-1])
        if '-d' in a:
            state[str(p)] = {'ino': len(calls), 'uid': 0}
        else:
            state[str(p)] = {'uid': 0, 'sha256': __import__('hashlib').sha256(Path(a[-2]).read_bytes()).hexdigest()}
    kh = lap_cai(root, so, quan_sat=qs, chay=run)
    with pytest.raises(LoiCaiDat):
        thuc_hien(kh)
    assert any(x.su == 'da_tao' for x in so.muc().values())
    assert any(x.su == 'khong_tao' for x in so.muc().values())
    assert not any('node-modules.tar' in a[-1] for a in calls)


def test_cai_khong_doc_goi_qua_lop_boc_hay_tep_dac_biet(tmp_path):
    from tram.chu.cai_phu_thuoc import doc_goi
    p = tmp_path / 'mf'
    p.write_bytes(b'x' * 100)
    with pytest.raises(ValueError):
        doc_goi(p, 10)
    link = tmp_path / 'link'
    link.symlink_to(p)
    with pytest.raises(OSError):
        doc_goi(link, 1000)


def test_khong_acl_that_tren_macos(tmp_path):
    import subprocess
    from tram.kiem.deps_root import khong_acl
    p = tmp_path / 'tep'; p.write_text('x')
    assert khong_acl(p) is None  # không ACL: macOS trả NULL + ENOENT, không được coi là lỗi đọc
    with pytest.raises(FileNotFoundError):
        khong_acl(tmp_path / 'khong-co')
    subprocess.run(['/bin/chmod', '+a', 'everyone deny delete', str(p)], check=True)
    try:
        with pytest.raises(ValueError, match='deps-co-acl'):
            khong_acl(p)
    finally:
        subprocess.run(['/bin/chmod', '-N', str(p)], check=True)  # bỏ ACL để pytest dọn được thư mục tạm
