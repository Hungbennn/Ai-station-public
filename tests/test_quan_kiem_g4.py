from pathlib import Path
from types import SimpleNamespace

import pytest


def test_g4_giu_nguyen_policy_du_an(tmp_path, monkeypatch):
    import io
    import tarfile
    import json
    import tram.quan_kiem.g4 as m
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w') as f:
        t = tarfile.TarInfo('README')
        t.size = 4
        f.addfile(t, io.BytesIO(b'fake'))
    monkeypatch.setattr(m, 'git_nhap', lambda *a: 'a' * 40)
    monkeypatch.setattr(m, 'archive', lambda *a: b.getvalue())
    monkeypatch.setattr(m, 'Path', lambda x: tmp_path / 'dac' if x == '/Users/Shared/tram-g4-quan-kiem' else Path(x))
    policy = {'mac_dinh': ['python -m pytest'], 'cho_phep': ['python -m pytest']}
    c = {'home_tram': str(tmp_path / '.tram'), 'policy': {'repo': policy}}
    m.chuan_bi(tmp_path / 'g4', c, 'repo', tmp_path / 'fake')
    info = json.loads((tmp_path / 'g4/lan.json').read_text())
    assert info['du_an'] == 'repo' and info['policy'] == policy
    assert (tmp_path / 'g4/kho/README').read_bytes() == b'fake'


@pytest.mark.parametrize('dau', [b'', b'Bad request.\n'])
def test_bootout_vang_daemon_duoc_nhung_loi_quan_sat_khong_duoc(dau):
    from tram.chu.dung_quan_kiem import dung_daemon
    calls = []
    def run(a, **kw):
        calls.append(a)
        return SimpleNamespace(returncode=113, stdout=b'',
                               stderr=dau + b'Could not find service "vn.tram.quan-kiem" in domain for system\n')
    dung_daemon(run)
    assert calls[-1][-2:] == ['print', 'system/vn.tram.quan-kiem']
    with pytest.raises(OSError, match='chua-chung-minh'):
        dung_daemon(lambda *a, **kw: SimpleNamespace(returncode=1, stdout=b'', stderr=b'permission denied'))


@pytest.mark.parametrize('mien', ['system', 'user gui: 501'])
def test_vang_dung_output_macos_24g90(mien):
    from tram.giao_viec.do_launchd_g4 import _vang
    out = f'Bad request.\nCould not find service "vn.tram.codex-absent-b4" in domain for {mien}\n'.encode()
    assert _vang(113, out, 'vn.tram.codex-absent-b4')
    assert not _vang(112, out, 'vn.tram.codex-absent-b4')
    assert not _vang(113, out, 'vn.tram.codex-absent')


@pytest.mark.parametrize('dau,duoi', [
    (b'Bad request!\n', b''), (b'Bad request. \n', b''), (b'Bad request.\r\n', b''),
    (b'Bad request.\nBad request.\n', b''), (b'Permission denied\n', b''),
    (b'Bad request.\n', b'\nPermission denied'), (b'Bad request.\n\n', b''),
])
def test_vang_khong_nuot_dong_loi_khac(dau, duoi):
    from tram.giao_viec.do_launchd_g4 import _vang
    out = dau + b'Could not find service "vn.tram.quan-kiem" in domain for system' + duoi
    assert not _vang(113, out, 'vn.tram.quan-kiem')
