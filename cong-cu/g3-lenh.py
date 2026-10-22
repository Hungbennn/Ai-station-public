#!/usr/bin/env python3
"""Ghi PID/thế hệ/ASID ngay trong child trước exec; waitstatus phân biệt exit và signal.
Chỉ dùng phép đo, cùng principal/hồ sơ với lệnh đích, không gọi hộ ngoài Seatbelt.
"""
import ctypes
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def ghi(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as f: json.dump(data, f)


def danh_tinh():
    class Audit(ctypes.Structure):
        _fields_ = [('auid', ctypes.c_uint32), ('mask', ctypes.c_uint32*2),
                    ('tid', ctypes.c_uint32*6), ('asid', ctypes.c_int32), ('flags', ctypes.c_uint64)]
    a = Audit(); asid = None
    if sys.platform == 'darwin' and ctypes.sizeof(a) == 48 and Audit.asid.offset == 36:
        try:
            lib = ctypes.CDLL('/usr/lib/libbsm.dylib', use_errno=True)
            if lib.getaudit_addr(ctypes.byref(a), ctypes.sizeof(a)) == 0: asid = a.asid
        except OSError: pass
    birth = None
    try:
        born = subprocess.run(['/bin/ps', '-p', str(os.getpid()), '-o', 'lstart='],
                              capture_output=True, text=True, timeout=2)
        if born.returncode == 0: birth = ' '.join(born.stdout.split()) or None
    except (OSError, subprocess.TimeoutExpired): pass
    return dict(pid=os.getpid(), uid=os.getuid(), ruid=os.getuid(), euid=os.geteuid(),
                groups=os.getgroups(), born=birth,
                asid=asid, wall_start=time.strftime('%Y-%m-%d %H:%M:%S'))


def main():
    prefix, *args = sys.argv[1:]
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    started = time.monotonic(); pid = os.fork()
    if pid == 0:
        try:
            ghi(prefix+'.actor', danh_tinh())
            os.execv(args[0], args)
        except BaseException as exc:
            os.write(2, ('exec/setup failed: '+type(exc).__name__+'\n').encode()); os._exit(126)
    # PID con chưa reap nên không thể bị dùng lại khi gửi tín hiệu.
    owned = True
    signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGALRM)
    def ngat(sig, frame):
        if owned: os.kill(pid, sig)
    for sig in signals: signal.signal(sig, ngat)
    def cho(flags):
        nonlocal owned
        old = signal.pthread_sigmask(signal.SIG_BLOCK, signals)
        try:
            result = os.waitpid(pid, flags)
            if result[0] == pid: owned = False
            return result
        except ChildProcessError:
            owned = False
            raise
        finally: signal.pthread_sigmask(signal.SIG_SETMASK, old)
    deadline = started+12; timed = False
    while True:
        done, status = cho(os.WNOHANG)
        if done: break
        if time.monotonic() >= deadline:
            timed = True; os.kill(pid, signal.SIGKILL); _, status = cho(0); break
        time.sleep(0.05)
    sig = os.WTERMSIG(status) if os.WIFSIGNALED(status) else 0
    code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else None
    ghi(prefix+'.status', dict(exit=code, signal=sig, timeout=timed, elapsed=time.monotonic()-started,
                              wall_end=time.strftime('%Y-%m-%d %H:%M:%S')))
    return 128+sig if sig else code


if __name__ == '__main__': sys.exit(main())
