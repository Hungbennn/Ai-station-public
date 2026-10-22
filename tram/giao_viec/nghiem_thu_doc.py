"""CLI G4 dữ liệu giả, chỉ chạy sau duyệt riêng; không mở S6 hay bỏ dấu đóng cổng."""
import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import giu_khoa
from tram.giao_viec.mau_g4 import do_canary
from tram.giao_viec.do_launchd_g4 import do_launchd
from tram.giao_viec.mau_g4 import tao_mau, smoke_toolchain
from tram.kiem.danh_tinh import xac_minh_uid
from tram.kiem.lenh_ngan import chay_ngan


def _cau_hinh():
    from tram.giao_viec.lenh_nghiem_thu import _pk_goc
    return _pk_goc()


def _chay(argv):
    return chay_ngan(['/bin/sh', '-c', 'exec "$@" 2>&1', '--', *argv], timeout=15, doc=True)


def _adapter(chay):
    def run(argv, **kw):
        ma, out = chay(argv)
        return subprocess.CompletedProcess(argv, 255 if ma is None else ma, out.decode(errors='replace'))
    return run


def nghiem_thu(pk, goc: Path, uid: int, *, home: Path, tam: Path, chay=_chay) -> dict:
    luot = goc / f'g4-{secrets.token_hex(12)}'
    log = tram_home() / 'log' / 'nghiem-thu'
    log.mkdir(parents=True, exist_ok=True)
    receipt = log / f'{luot.name}.json'
    meta = log / f'{luot.name}-fixture.json'
    fixture = tao_mau(pk, luot, home, tam, chay, receipt=meta)
    smoke = smoke_toolchain(pk, luot, chay)
    if not all(smoke.values()):
        return {'toolchain': smoke, 'don': False, 's6': 'dong'}
    canary = do_canary(pk, luot, fixture['tep'], fixture['mau'], chay=_adapter(chay))
    expected = ['0:no-match:no:no', '1:no-match:no:yes', '2:no-match:no:no',
                '3:no-match:no:no', '4:match:yes:yes']
    outside = canary.get('ngoai')
    if canary.get('trong') != expected or not outside or outside[3:] != ['3:match:yes:yes', '4:match:yes:yes']:
        return {'toolchain': smoke, 'canary': canary, 'don': False, 's6': 'dong'}
    launchd = do_launchd(pk, luot, receipt, uid, os.getuid(), chay)
    sach = len(launchd) == 8 and all(r['don'] for r in launchd)
    if sach:
        ma, _ = chay(pk.boc_lenh(['/bin/rm', '-rf', '--', str(luot), f'{luot}.nha']))
        sach = ma == 0
    if sach:
        for p in (fixture['home'].parent, fixture['dac'].parent):
            shutil.rmtree(p)
    return {'toolchain': smoke, 'canary': canary, 'launchd': launchd, 'don': sach, 's6': 'dong'}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='G4: canary giả + launchctl cố định ngoài/trong hồ sơ')
    p.add_argument('--dong-y-g4', action='store_true', help='Chỉ dùng sau khi Đại ca duyệt đúng kịch bản G4')
    args = p.parse_args(argv)
    if not args.dong_y_g4:
        print('Chưa chạy: cần duyệt canary trong nhà và đối chứng launchd của G4.', file=sys.stderr)
        return 2
    try:
        if not (tram_home() / 'kiem-lai.dong').is_file():
            raise ValueError('phải giữ dấu kiem-lai.dong trước nghiệm thu')
        pk, goc = _cau_hinh()
        uid = xac_minh_uid(pk.ten, pk.boc_lenh, pk.kill_nhom)
        with giu_khoa():
            kq = nghiem_thu(pk, goc.resolve(strict=True), uid, home=Path.home(),
                            tam=Path('/private/tmp'))
        print(json.dumps(kq, ensure_ascii=False))
        return 1                         # không chứng nhận OS/S6 tự động, kể cả mọi lệnh đã dọn
    except (OSError, ValueError, RuntimeError) as e:
        print(f'G4 dừng: {type(e).__name__}; giữ cổng đóng và receipt để kiểm/dọn.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
