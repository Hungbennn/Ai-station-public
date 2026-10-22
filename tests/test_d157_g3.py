"""Kiểm G3 dùng một nguồn ngoại lệ, không chép danh sách hay tin comm."""
import os
from pathlib import Path


def test_g3_dung_nguon_chung():
    p = Path(os.environ.get("D157_G3_SCRIPT", "docs/handovers/g3-bo-sung.sh"))
    s = p.read_text()
    assert "APPLE_TU_BAT=" not in s
    assert "from tram.kiem.ngoai_le_uid import con_uid" in s
    assert 'con_uid(int(sys.argv[1]), lambda: ds, ten="tram-kiem")' in s
    assert "pid=,ppid=,uid=,ruid=,comm=" not in s
