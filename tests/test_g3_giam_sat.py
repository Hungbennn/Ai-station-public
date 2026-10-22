"""Giám sát chỉ báo/dừng đúng shell con tự tạo; không kill theo nhóm hay tên."""
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.g3

KB = Path(__file__).resolve().parents[1] / 'cong-cu/g3-giam-sat.pl'


def test_giam_sat_het_do_cho_shell_don(tmp_path):
    child = tmp_path / 'child.sh'
    child.write_text('trap \'echo da-don; exit 142\' ALRM\nwhile :; do /bin/sleep 0.1; done\n')
    r = subprocess.run(['/usr/bin/perl', str(KB), '1', '3', '/bin/bash', str(child)],
                       capture_output=True, text=True, timeout=6)
    assert r.returncode == 142 and 'da-don' in r.stdout


def test_giam_sat_shell_bi_kill_bao_giu_receipt(tmp_path):
    child = tmp_path / 'child.sh'; child.write_text('kill -KILL $$\n')
    r = subprocess.run(['/usr/bin/perl', str(KB), '2', '2', '/bin/bash', str(child)],
                       capture_output=True, text=True, timeout=6)
    assert r.returncode == 137 and 'giữ khoá/receipt' in r.stderr
