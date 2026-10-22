"""Đối chứng G4 tích hợp worker sản phẩm; chỉ dữ liệu cố định, không RPC chạy shell Uq."""
import ctypes
import json
import os
import pwd
from pathlib import Path

from tram.giao_viec.ban_chep import _chay
from tram.giao_viec.do_launchd_g4 import do_launchd
from tram.giao_viec.ngu_canh_kiem import SECURITY


def doi_chung(c, pk, wt, id_):
    sid, flags = ctypes.c_uint32(), ctypes.c_uint32()
    if ctypes.CDLL(SECURITY).SessionGetInfo(ctypes.c_int32(-1), ctypes.byref(sid), ctypes.byref(flags)):
        raise OSError('khong-doc-duoc-session')
    log = Path(c['home']) / 'log'
    log.mkdir(mode=0o700, exist_ok=True)
    uid = pwd.getpwnam(pk.ten).pw_uid
    def chay(a):
        r = _chay(a, kill=pk.kill_nhom, timeout=15)
        out = (r.stdout or b'') + (r.stderr or b'')
        driver = log / f'driver-{id_}.jsonl'
        with driver.open('a') as f:
            os.fchmod(f.fileno(), 0o600)
            if f.tell() < 65536:
                f.write(json.dumps({'argv': a, 'ma': r.returncode,
                                    'out': out[:2048].decode(errors='replace')}) + '\n')
        return r.returncode, out
    _chay(pk.boc_lenh(['/bin/cp', '/bin/launchctl', str(wt / 'launchctl-copy')]), kill=pk.kill_nhom, check=True)
    mien = [f'user/{uid}', f'gui/{uid}', f'user/{c["uid_quan"]}', f'gui/{c["uid_quan"]}',
            f'login/{sid.value}', 'system', f'gui/{c["uid_tram"]}']
    paths = [Path(c['home_tram']).parent / 'tram-g4-quan-kiem/canary',
             Path('/Users/Shared/tram-g4-quan-kiem/canary')]
    doc = []
    for p in paths:
        ma, b = chay(pk.boc_lenh(['/bin/cat', str(p)]))
        doc.append({'ma': ma, 'doc_mau': ma == 0 and b == b'TRAM-G4-NONSECRET\n'})
    (log / f'context-{id_}.json').write_text(json.dumps({
        'pid': os.getpid(), 'ppid': os.getppid(), 'uid': os.getuid(), 'gid': os.getgid(),
        'groups': os.getgroups(), 'asid': sid.value, 'flags': flags.value, 'canary_ngoai_ho_so': doc}))
    from tram.giao_viec.mau_g4 import do_canary, smoke_toolchain
    import shlex
    mau, link = wt / 'mau', wt / 'canary-link'
    script = (f"printf 'TRAM-G4-NONSECRET\\n' > {shlex.quote(str(mau))}; "
              f"ln -s {shlex.quote(str(paths[0]))} {shlex.quote(str(link))}")
    _chay(pk.boc_luot(wt)(['/bin/sh', '-ec', script]), kill=pk.kill_nhom, check=True)
    firmlink = Path('/System/Volumes/Data') / paths[0].relative_to('/')
    def run(a, **kw):
        r = _chay(a, kill=pk.kill_nhom, timeout=15)
        from types import SimpleNamespace
        return SimpleNamespace(returncode=r.returncode, stdout=r.stdout.decode())
    canary = do_canary(pk, wt, [paths[0], link, firmlink, paths[1], mau], mau, chay=run)
    expected = ['0:no-match:no:no', '1:no-match:no:yes', '2:no-match:no:no',
                '3:no-match:no:no', '4:match:yes:yes']
    if canary['trong'] != expected or not all(smoke_toolchain(pk, wt, chay).values()):
        raise OSError('g4-canary-hoac-cong-cu-khong-dat')
    (log / f'canary-{id_}.json').write_text(json.dumps(canary))
    rows = do_launchd(pk, wt, log / f'launchd-{id_}.json', uid, c['uid_quan'], chay,
                      mien=mien, uids=[uid, c['uid_quan'], c['uid_tram']])
    if not rows or any(not r['don'] or r['ket_luan'] == 'lot' for r in rows):
        r = rows[-1] if rows else {}
        raise OSError(f"g4-lot-hoac-don-chua-ro {r.get('ho_so')}:{r.get('binary')}:{r.get('lenh')} ma={r.get('ma')} "
                      f"exec={r.get('exec_ma')} don={r.get('don')} {r.get('ket_luan')}")
    if doc[0]['ma'] == 0 or not doc[1]['doc_mau']:
        raise OSError('g4-doi-chung-doc-khong-dat')
    # Đo 20/10: canary-link trỏ ra vùng cấm làm pytest quét gốc lượt dính PermissionError → dọn đồ đo trước lệnh kiểm.
    tam = [wt / t for t in ('mau', 'canary-link', 'launchctl-copy', 'launchd.plist', 'launchdcopy.plist')]
    _chay(pk.boc_luot(wt)(['/bin/rm', '-f', '--', *map(str, tam)]), kill=pk.kill_nhom, check=True)
