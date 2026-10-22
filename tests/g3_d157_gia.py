"""Adapter chỉ của test G3: bảng/path giả, dùng chính predicate D157 sản phẩm."""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
code = sys.argv[3]
if "from tram.kiem.ngoai_le_uid import con_uid" not in code:
    os.execv(sys.executable, [sys.executable, *sys.argv[1:]])
from tram.kiem import ngoai_le_uid as n
from tram.kiem.cay_tien_trinh import TienTrinh

r = subprocess.run([str(Path(os.environ["G3_GIA"]) / "ps")], capture_output=True, text=True)
if r.returncode or r.stderr or not r.stdout.strip():
    sys.exit(1)
rows, paths = [], {}
try:
    for line in r.stdout.splitlines():
        pid, ppid, uid, ruid, path = line.split(maxsplit=4)
        t = TienTrinh(int(pid), int(ppid), int(pid), int(uid), int(ruid), int(pid))
        rows = [x for x in rows if x.pid != t.pid] + [t]   # ps giả ghi đè dòng thật cùng PID (sleep "dưới tram-kiem")
        paths[t.pid] = path
except ValueError:
    sys.exit(1)
from tram.kiem import bang_tien_trinh
bang_tien_trinh.mot_nhan = lambda pid: next(t for t in rows if t.pid == pid)
n.duong_nhan = paths.__getitem__
n.chup_nhan = lambda: rows
n.build_macos = lambda: os.environ.get("G3_BAN", "24G90")
original = n.con_uid
n.con_uid = lambda uid, chup=None, **kw: original(uid, lambda: rows, mot=lambda pid: next(t for t in rows if t.pid == pid),
                                     duong=paths.__getitem__, **kw)
sys.argv = ["-c", *sys.argv[4:]]
exec(code)
