"""`codex exec --json` GIẢ — CHỈ DÙNG TRONG TEST (chạy bằng sys.executable). In từng dòng của $FIXTURE, chép stdin
vào $GHI, thoát mã $MA. CHE_DO=treo: in dòng đầu rồi bỏ qua SIGTERM và ngủ (thử leo thang SIGKILL)."""
import os
import signal
import sys
import time
from pathlib import Path

Path(os.environ["GHI"]).write_text(sys.stdin.read(), encoding="utf-8")
dong = Path(os.environ["FIXTURE"]).read_text(encoding="utf-8").splitlines()
if os.environ.get("CHE_DO") == "treo":
    print(dong[0], flush=True)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(30)
for d in dong:
    print(d, flush=True)
sys.exit(int(os.environ.get("MA", "0")))
