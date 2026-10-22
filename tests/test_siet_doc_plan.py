from pathlib import Path
import json
import pytest

from tram.tho.quyen_kiem import manifest_ho_so, ho_so_tu_manifest
from tram.kiem.chay_lenh import moi_truong_kiem
from tram.giao_viec.repo_ban_chep import lenh_repo


@pytest.mark.parametrize('goc_chung', [False, True])
def test_ho_so_doc_chung_cam_rieng_roi_mo_dung_luot(tmp_path, goc_chung):
    goc = Path('/Users/Shared/tram-kiem') if goc_chung else tmp_path.resolve()
    hs, raw = manifest_ho_so(tram_home_tram=tmp_path / 'tram', nha_quan_ly=Path('/Users/tram-tho'),
                            goc=goc, cong=[7710])
    text = hs.decode()
    assert '(allow file-read*)' in text
    assert 'user-preference-read' not in text
    cam = ('/Users', '/private/var/root', '/Library/Keychains', '/private/var/db/tram-quan-kiem',
           '/private/var/db/tram-quan-kiem-socket', '/private/var/db/tram-g3-quan-kiem',
           '/private/etc/sudoers', '/private/etc/sudoers.d', '/Library/Application Support/com.apple.TCC',
           '/private/var/db/dslocal')
    # Khóa cả tập luật đọc và thứ tự: không cho allow bổ sung vô tình mở lại vùng cấm.
    assert [d for d in text.splitlines() if 'file-read' in d] == [
        '(allow file-read*)',
        *(f'(deny file-read* (subpath "{p}"))' for p in cam),
        f'(deny file-read* (subpath "{tmp_path}/tram") (subpath "/Users/tram-tho/.tram"))',
        f'(deny file-read* (subpath "{goc}"))',
        '(allow file-read* (subpath (param "LUOT")) (subpath (param "NHA")))',
        '(allow file-read-metadata ' + ' '.join(f'(literal "{c}")' for c in [*reversed(goc.parents[:-1]), goc]) + ')',
    ]
    m, same = ho_so_tu_manifest(raw)
    assert m['phien_ban'] == 3 and same == hs
    assert m['toolchain']['python'].startswith('/usr/local/tram/')
    bad = json.loads(raw)
    bad['toolchain']['python'] = '/Users/dai-ca/.local/python'
    with pytest.raises(ValueError):
        ho_so_tu_manifest(json.dumps(bad).encode())


def test_path_kiem_khong_ke_thua_nha():
    env = moi_truong_kiem({'PATH': '/Users/dai-ca/.local/bin', 'HOME': '/luot.nha'},
                         {'PATH': '/tmp/agent', 'UV_PYTHON': '/Users/dai-ca/python'})
    assert env['PATH'].startswith('/usr/local/tram/toolchains/python/')
    assert '/Users/' not in env['PATH']
    assert env['UV_PYTHON'].endswith('/bin/python3.12')
    assert env['UV_PYTHON_DOWNLOADS'] == 'never'
    assert env['UV_CACHE_DIR'] == '/luot.nha/.cache/uv'
    assert env['NPM_CONFIG_CACHE'] == '/luot.nha/.cache/npm'


def test_git_ban_chep_khong_tim_tren_path(monkeypatch, tmp_path):
    monkeypatch.setenv('PATH', '/tmp/agent')
    for argv in lenh_repo(tmp_path).values():
        assert '/opt/homebrew/Cellar/git/2.56.0_1/bin/git' in argv
        assert '/usr/bin/git' not in argv


def test_bien_toolchain_duoc_dat_sau_sudo(tmp_path):
    from tram.giao_viec.principal_kiem import tu_cach_ly
    argv = tu_cach_ly('user:tram-kiem').boc_luot(tmp_path)(['uv', 'run', 'python'])
    vi_tri = argv.index('/usr/bin/env')
    assert f'UV_CACHE_DIR={tmp_path}.nha/.cache/uv' in argv[vi_tri:]
    assert 'UV_PYTHON=/usr/local/tram/toolchains/python/3.12.15-20261009/bin/python3.12' in argv[vi_tri:]
    assert any(x.startswith('PATH=/usr/local/tram/toolchains/python/') for x in argv[vi_tri:])


def test_toolchain_van_ghim_manifest_va_offline():
    from tram.kiem.toolchain import manifest, bien_kiem
    m = manifest()
    assert '/System/Volumes/Preboot/Cryptexes/OS/usr/lib' in m['he_thong']
    assert '/private/var/db/timezone' in m['he_thong']
    assert '/dev/fd' in m['literal']
    assert bien_kiem('/luot.nha')['UV_OFFLINE'] == '1'
