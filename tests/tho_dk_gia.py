"""Đầu dò giả cho `tram tho dang-ky` (CHỈ DÙNG TRONG TEST): Mac thợ có `tram`, `codex`, `claude`, Tailscale gắn tag."""
import json
import subprocess
from pathlib import Path

from tram.tho.do_may import TAG_THO
from tram.tho.ke_hoach_dk import DauDoDK

URL = "https://may-b.tail1234.ts.net"


def dau_do(tmp_path: Path, *, tags=(TAG_THO,), co=("tram", "codex", "claude", "tailscale"), dang_nhap=0,
           goi: list | None = None) -> DauDoDK:
    goi = [] if goi is None else goi

    def chay(argv, **kw):
        goi.append(argv)
        if argv[1:] == ["status", "--json"]:
            return subprocess.CompletedProcess(argv, 0, json.dumps({"Self": {"Tags": list(tags)}}), "")
        if argv[1:] == ["login", "status"]:
            return subprocess.CompletedProcess(argv, dang_nhap, "", "")
        return subprocess.CompletedProcess(argv, 0, f"{Path(argv[0]).name} 1.0\n", "")
    return DauDoDK(which=lambda c: f"/opt/bin/{c}" if c in co else None, chay=chay, home=tmp_path / "home",
                   uid=501, tram_home=tmp_path / "home" / ".tram", daemon=tmp_path / "daemon.plist")
