"""Waitstatus thật của tiến trình tự tạo; ps có thể bị sandbox chặn, không giả vờ có birth."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

pytestmark = pytest.mark.g3

KB = Path(__file__).resolve().parents[1] / 'cong-cu/g3-lenh.py'


@pytest.mark.parametrize('code,rc,exitcode,sig', [
    ('raise SystemExit(137)',137,137,0),
    ('import os,signal; os.kill(os.getpid(),signal.SIGKILL)',137,None,9),
])
def test_waitstatus_khong_danh_dong_exit137_va_signal9(tmp_path, code, rc, exitcode, sig):
    prefix = tmp_path/'ca'
    r = subprocess.run([sys.executable, str(KB), str(prefix), sys.executable, '-c', code],
                       capture_output=True, text=True, timeout=15)
    status = json.loads(Path(str(prefix)+'.status').read_text())
    assert Path(str(prefix)+'.actor').exists(), r.stderr+str(status)
    actor = json.loads(Path(str(prefix)+'.actor').read_text())
    assert r.returncode == rc and status['exit'] == exitcode and status['signal'] == sig
    assert actor['uid'] == os.getuid() and actor['pid'] > 0
    assert not status['timeout']


def test_khong_chuyen_tin_hieu_sau_khi_da_reap(tmp_path):
    bad = tmp_path/'gui-sai'
    code = '''import importlib.util, os, signal, sys
s=importlib.util.spec_from_file_location('g3',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.danh_tinh=lambda: {}
wait=os.waitpid; send=os.kill; reaped=False
def watched_kill(pid,sig):
    if reaped and pid != os.getpid():
        open(sys.argv[2], 'w').write('khong duoc gui PID da reap'); return
    send(pid,sig)
def watched_wait(pid,flags):
    global reaped
    result=wait(pid,flags)
    if result[0] == pid:
        reaped=True; send(os.getpid(),signal.SIGTERM)
    return result
m.os.waitpid=watched_wait; m.os.kill=watched_kill
prefix=sys.argv[3]; sys.argv=['g3',prefix,'/usr/bin/true']
raise SystemExit(m.main())
'''
    # Đường ghi đánh dấu giữ riêng vì main thay argv.
    code = code.replace("open(sys.argv[2],", f"open({str(bad)!r},")
    r = subprocess.run([sys.executable, '-c', code, str(KB), str(bad), str(tmp_path/'ca')],
                       capture_output=True, text=True, timeout=15)
    assert r.returncode == 0, r.stderr
    assert not bad.exists(), 'handler gửi tín hiệu vào PID đã reap'
