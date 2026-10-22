"""Chép lại tệp Python kiểm bị lệch digest từ bản soạn gốc (đã khớp manifest); in kế hoạch, chờ dong-y.

Dùng khi root chạy Python kiểm thiếu `-B` và ghi đè `.pyc` (B1 19/10 21:51/21:53). Chạy dưới Đại ca, không chạy
Python dưới root; chỉ `sudo install` đúng tệp lệch, rồi kiểm lại toàn prefix.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tram.duong_dan import tram_home  # noqa: E402
from tram.kiem.kiem_python import kiem_prefix  # noqa: E402
from tram.kiem.toolchain import PYTHON  # noqa: E402


def bam(p):
    with open(p, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    goc, soan = Path(PYTHON), tram_home() / 'cai-dat-tho' / 'python-soan' / 'python'
    m = json.loads((goc / 'manifest.json').read_bytes())['tep']
    lech = [t for t, e in sorted(m.items()) if bam(goc / t) != e['sha256']]
    if not lech:
        print('Không có tệp lệch; không làm gì.')
        return 0
    for t in lech:
        if not t.endswith('.pyc') or (soan / t).is_symlink() or bam(soan / t) != m[t]['sha256']:
            print(f'DỪNG: {t} không phải .pyc hoặc bản soạn không khớp manifest — báo Em')
            return 2
    for t in lech:
        print(f'sudo install -m 0644 -o root -g wheel {soan / t} {goc / t}')
    if input(f'Chép lại {len(lech)} tệp .pyc từ bản soạn — gõ dong-y: ').strip() != 'dong-y':
        return 1
    for t in lech:
        subprocess.run(['sudo', '/usr/bin/install', '-m', '0644', '-o', 'root', '-g', 'wheel',
                        str(soan / t), str(goc / t)], check=True, timeout=30)
    kiem_prefix()
    print('python-kiem: dat')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
