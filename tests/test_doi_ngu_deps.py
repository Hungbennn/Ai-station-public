import io
import json
from pathlib import Path
import subprocess
import pytest
from tram.kiem.deps_manifest import KHOA_NGUON, bam
from tram.kiem.deps_root import GOC_DEPS, doc_bundle
from tram.kiem.deps_tar import giai_nen
from tram.kiem.toolchain import PYTHON


def test_worktree_ben_duoc_cap_python_node(tmp_path, monkeypatch):
    from tho_chay_gia import dung_may, lay_phieu
    from git_gia import git
    from tram.tho.chuan_bi import chuan_bi
    m = dung_may(tmp_path, monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    repo = Path(__file__).resolve().parents[1]
    for rel in KHOA_NGUON:
        p = m.b.tho / rel
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_bytes((repo / rel).read_bytes())
    git(m.b.tho, 'add', '-A')
    git(m.b.tho, '-c', 'user.name=Test', '-c', 'user.email=test@localhost', 'commit', '-qm', 'lock')
    tt.phieu['repo']['cha'] = git(m.b.tho, 'rev-parse', 'HEAD')
    tt.phieu['du_an'] = 'ben-station'
    tt.phieu['can_moi_truong_kiem'] = False
    m.b.tho.rename(m.b.tho.with_name('ben-station'))
    from doi_deps_gia import bundle
    bundle(tmp_path, monkeypatch, {rel: bam((repo / rel).read_bytes()) for rel in KHOA_NGUON})
    pc = chuan_bi(m.nc, k, so, hop, tt)
    assert (pc.wt / '.venv/bin/python').is_file()
    assert (pc.wt / 'frontend/node_modules/vue/package.json').is_file()


def test_env_duoc_dat_sau_boc_principal():
    from tram.tho.deps_b import boc_kiem_b
    pc = type('PC', (), {'p': type('P', (), {'du_an': 'ben-station'})(),
                         'principal': type('PR', (), {'boc': lambda self, a: ['sudo-gia', *a]})()})()
    assert boc_kiem_b(pc)(['tests/chan_host/chay.sh', '-q']) == [
        'sudo-gia', '/usr/bin/env', 'TRAM_KIEM_DA_CHUAN_BI=1', 'tests/chan_host/chay.sh', '-q']


@pytest.mark.parametrize('loi', ['doi-lock', 'thieu-bundle', 'sai-hash', 'symlink', 'dich-da-co'])
def test_deps_loi_khong_ghi_vao_dich_la(tmp_path, monkeypatch, loi):
    from doi_deps_gia import bundle
    from tram.tho.deps_b import cap_deps_b
    wt = tmp_path / 'cay'
    wt.mkdir()
    for rel in KHOA_NGUON:
        p = wt / rel
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(rel)
    root, m = bundle(tmp_path, monkeypatch, {rel: bam(rel.encode()) for rel in KHOA_NGUON})
    if loi == 'doi-lock':
        (wt / 'uv.lock').write_text('doi')
    elif loi == 'thieu-bundle':
        (root / 'manifest.json').unlink()
    elif loi == 'sai-hash':
        (root / 'python-site.tar').write_bytes(b'hong')
    elif loi == 'symlink':
        (wt / 'uv.lock').unlink()
        (wt / 'uv.lock').symlink_to(root / 'manifest.json')
    else:
        (wt / '.venv').mkdir()
    with pytest.raises((ValueError, subprocess.SubprocessError)):
        cap_deps_b(wt)
    assert not (wt / 'frontend/node_modules').exists()


def test_khong_chay_ma_repo_duoi_quan_ly(tmp_path, monkeypatch):
    from doi_deps_gia import bundle
    from tram.tho.deps_b import cap_deps_b
    wt = tmp_path / 'cay'
    wt.mkdir()
    for rel in KHOA_NGUON:
        p = wt / rel
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(rel)
    bundle(tmp_path, monkeypatch, {rel: bam(rel.encode()) for rel in KHOA_NGUON})
    (wt / 'sitecustomize.py').write_text('raise RuntimeError("MA-REPO-CHAY")')
    da = []
    def chay(a, **kw):
        da.append((a, kw))
        return subprocess.run(a, **kw)
    cap_deps_b(wt, chay=chay)
    assert (wt / '.venv/lib/python3.12/site-packages/thu_vien.py').is_file()
    assert all(a[:2] == [f'{PYTHON}/bin/python3.12', '-I'] and kw['timeout'] == 300 for a, kw in da)
