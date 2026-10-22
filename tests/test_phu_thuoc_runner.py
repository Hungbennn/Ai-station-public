"""Runner chuẩn bị vẫn gọi pytest qua plugin/audithook và truyền nguyên mã thoát."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def runner(tmp_path, *, co_venv=True, dung_pin=True):
    root = Path(__file__).resolve().parents[1]
    host = tmp_path / 'tests/chan_host'
    shutil.copytree(root / 'tests/chan_host', host)
    shutil.copy(root / 'tests/conftest.py', tmp_path / 'tests/conftest.py')
    s = (host / 'chay.sh').read_text()
    s = s.replace('/usr/local/tram/toolchains/python/3.12.15-20261009',
                  sys.base_prefix if dung_pin else '/sai-pin')
    s = s.replace('/opt/homebrew/Cellar/git/2.56.0_1/bin/git', os.environ['TRAM_CHAN_GIT'])
    (host / 'chay.sh').write_text(s)
    if co_venv:
        os.symlink(Path(sys.executable).parent.parent, tmp_path / '.venv')
    nha = tmp_path / 'nha'
    (nha / 'tmp').mkdir(parents=True)
    env = dict(os.environ, TRAM_KIEM_DA_CHUAN_BI='1', HOME=str(nha), TMPDIR=str(nha / 'tmp'),
               TRAM_CHAN_NHAT_KY=str(nha / 'nhat-ky'), PYTHONPATH=str(tmp_path))
    return host / 'chay.sh', env


@pytest.mark.parametrize('co_venv,dung_pin', [(False, True), (True, False)])
def test_runner_thieu_venv_sai_pin_khong_fallback_uv(tmp_path, co_venv, dung_pin):
    sh, env = runner(tmp_path, co_venv=co_venv, dung_pin=dung_pin)
    r = subprocess.run([str(sh), '-q', 'khong-ton-tai'], cwd=tmp_path, env=env,
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 2
    assert 'Python lượt kiểm' in r.stderr


@pytest.mark.parametrize('loi,ma', [(False, 0), (True, 1)])
def test_runner_giu_plugin_audithook_home_path_va_ma_thoat(tmp_path, loi, ma):
    sh, env = runner(tmp_path)
    (tmp_path / 'tram').mkdir()
    (tmp_path / 'tram/__init__.py').write_text('')
    test = '''import os, sys, subprocess, pathlib, shutil, tram
def test_noi_bo():
    assert pathlib.Path(tram.__file__).parent.parent == pathlib.Path.cwd()
    assert os.environ['TRAM_CHAN_CHAY_SH'] == '1'
    assert pathlib.Path(os.environ['HOME']).name == 'nha'
    assert pathlib.Path(os.environ['TMPDIR']).parent == pathlib.Path(os.environ['HOME'])
    assert os.environ['TRAM_CHAN_PY'].endswith('/.venv/bin/python')
    assert '/chan_host/bin/git' in shutil.which('git')
    r = subprocess.run([sys.executable, '-c', 'import chan_host; print("hook-ok")'], capture_output=True)
    assert r.returncode == 0 and b'hook-ok' in r.stdout
'''
    if loi:
        test += '    assert False\n'
    (tmp_path / 'tests/test_nho.py').write_text(test)
    r = subprocess.run([str(sh), '-q', 'tests/test_nho.py'], cwd=tmp_path, env=env,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == ma, r.stdout + r.stderr
    assert '0 dòng mới' in r.stdout and '): 0;' in r.stdout
    assert (tmp_path / 'nha/nhat-ky').read_bytes() == b''
