"""B5: lệnh root phải ngăn Python viết lại pyc và làm lệch manifest."""
import runpy
import sys
from pathlib import Path

import pytest


def test_cai_quan_kiem_huong_dan_go_g3_co_B(tmp_path):
    from tram.chu.cai_quan_kiem import lap
    from tram.chu.so_cai_tho import SoCai
    with pytest.raises(ValueError, match=r'python3\.12 -I -B cong-cu/g3-tai-khoan.py go'):
        lap(tmp_path, 'hungle', SoCai(tmp_path / 'so'), quan_sat=lambda *a: {'uid': 505})


def test_g3_huong_dan_root_co_B(monkeypatch):
    ns = runpy.run_path('cong-cu/g3-tai-khoan.py')
    monkeypatch.setattr(sys, 'argv', ['g3-tai-khoan.py'])
    with pytest.raises(RuntimeError, match=r'python3 -I -B cong-cu/g3-tai-khoan.py'):
        ns['main']()


def test_moi_huong_dan_goi_g3_bang_root_co_B():
    dong = [(p, line) for goc in ('tram', 'cong-cu', 'docs') for p in Path(goc).rglob('*')
            if p.suffix in ('.py', '.md', '.sh') for line in p.read_text().splitlines()
            if 'sudo ' in line and ' cong-cu/g3-tai-khoan.py' in line]
    assert dong
    assert all(' -B ' in line for p, line in dong), dong
