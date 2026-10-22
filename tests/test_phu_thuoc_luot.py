import copy
import io
from types import SimpleNamespace

import pytest

from test_phu_thuoc_kiem import archive, mau


def cay(tmp_path, monkeypatch):
    import tram.kiem.deps_nhan as n
    m = mau()
    monkeypatch.setattr(n, 'nen_tang', lambda: m['runtime'])
    for name in m['nguon']:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(name.encode())
    return n, m


@pytest.mark.parametrize('name', ['uv.lock', 'pyproject.toml', 'frontend/package-lock.json', 'frontend/package.json'])
@pytest.mark.parametrize('doi', ['mat', 'doi'])
def test_helper_lock_thieu_hoac_doi_truoc_test(tmp_path, monkeypatch, name, doi):
    n, m = cay(tmp_path, monkeypatch)
    (tmp_path / name).unlink() if doi == 'mat' else (tmp_path / name).write_bytes(b'changed')
    with pytest.raises((ValueError, OSError)):
        n.kiem_cay(tmp_path, m)
    assert not (tmp_path / '.venv').exists()


@pytest.mark.parametrize('name', ['.venv', 'frontend/node_modules'])
def test_helper_khong_ghi_de_deps_nguon(tmp_path, monkeypatch, name):
    n, m = cay(tmp_path, monkeypatch)
    (tmp_path / name).mkdir()
    with pytest.raises(ValueError):
        n.kiem_cay(tmp_path, m)


def test_helper_sai_abi_truoc_test(tmp_path, monkeypatch):
    n, m = cay(tmp_path, monkeypatch)
    bad = copy.deepcopy(m)
    bad['runtime']['abi'] = 'other-abi'
    with pytest.raises(ValueError):
        n.kiem_cay(tmp_path, bad)


@pytest.mark.parametrize('dich', ['uv.lock', 'pyproject.toml', 'frontend/package-lock.json',
    'frontend/package.json', '.venv/a', 'frontend/node_modules/a', 'frontend', 'manifest.json'])
def test_env_khong_de_lock_hoac_dich_chuan_bi(dich):
    from tram.quan_kiem.cap_deps import kiem_dich_env
    with pytest.raises(ValueError):
        kiem_dich_env(dich)


def test_worker_cap_bytes_qua_stdin_tao_venv_pin(tmp_path, monkeypatch):
    import tram.quan_kiem.cap_deps as cap
    from tram.kiem.toolchain import PYTHON
    m = mau()
    calls = []
    monkeypatch.setattr(cap, 'doc_bundle', lambda p, nhan: [
        nhan(name, b'archive', a) for name, a in m['artifacts'].items()] and m)
    cap.cap_deps(tmp_path, m, boc=lambda a: ['BOC', *a], kill='kill',
                 chay=lambda a, **kw: calls.append((a, kw)))
    assert any(a[1:5] == [f'{PYTHON}/bin/python3.12', '-I', '-m', 'venv'] and '--without-pip' in a
               for a, _ in calls)
    assert sum(kw.get('input') == b'archive' for _, kw in calls) == 2
    assert all(a[0] == 'BOC' and kw['kill'] == 'kill' and kw['check'] for a, kw in calls)
    assert not any('/usr/local/tram/deps' in ' '.join(a) for a, _ in calls)


def test_preparation_timeout_khong_chay_test_va_van_don(tmp_path, monkeypatch):
    import tram.quan_kiem.luot as l
    import tram.quan_kiem.cap_deps as cap
    calls = []
    m = mau()
    monkeypatch.setattr(l, 'NHAN', 'tram/quan_kiem/nhan.py')
    monkeypatch.setattr(l, '_chay', lambda *a, **kw: SimpleNamespace(stdout=b'tree'))
    monkeypatch.setattr(cap, 'cap_deps', lambda *a, **kw: (_ for _ in ()).throw(TimeoutError()))
    monkeypatch.setattr(l, 'chay_mot_lenh', lambda *a, **kw: calls.append('test'))
    monkeypatch.setattr(l, 'don_ban', lambda *a, **kw: calls.append('don'))
    pk = SimpleNamespace(boc_luot=lambda wt: lambda a: a, kill_nhom=lambda *a: None)
    d = dict(id='a'*32, tree='tree', du_an='ben-station', dich='.env.testing', lenh=['test'])
    with pytest.raises(TimeoutError):
        l.chay_luot(d, b'', b'', pk=pk, goc=tmp_path, log=tmp_path, policy=['test'], thu_hoi=lambda: None,
                    cfg={'g4': False, 'policy': {'ben-station': {'deps': m}}})
    assert calls == ['don']


@pytest.mark.parametrize('ten', ['uv.lock', 'frontend/package.json', '.venv/x'])
def test_env_tar_khong_duoc_noi_doi_dich(tmp_path, ten):
    from tram.quan_kiem.nhan import nhan_env
    with pytest.raises(ValueError):
        nhan_env(io.BytesIO(archive([(ten, 'file', b'x')])), tmp_path, '.env.testing')
    assert list(tmp_path.iterdir()) == []


def test_env_chi_mot_file_khong_ghi_de_va_khong_link(tmp_path):
    from tram.quan_kiem.nhan import nhan_env
    with pytest.raises(ValueError):
        nhan_env(io.BytesIO(archive([('.env.testing', 'link', 'uv.lock')])), tmp_path, '.env.testing')
    with pytest.raises(ValueError):
        nhan_env(io.BytesIO(archive([('.env.testing', 'file', b'x'), ('uv.lock', 'file', b'x')])),
                 tmp_path, '.env.testing')
    assert list(tmp_path.iterdir()) == []
    nhan_env(io.BytesIO(archive([('.env.testing', 'file', b'x')])), tmp_path, '.env.testing')
    assert (tmp_path / '.env.testing').stat().st_mode & 0o777 == 0o600
    with pytest.raises(ValueError):
        nhan_env(io.BytesIO(archive([('.env.testing', 'file', b'y')])), tmp_path, '.env.testing')
