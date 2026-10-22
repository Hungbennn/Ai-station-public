"""Ma trận launchctl G4 dùng sleep cố định; receipt trước ghi; không coi lỗi OS là Seatbelt chặn."""
import json
import os
import plistlib
import re
import shlex
import time
from tempfile import NamedTemporaryFile
from pathlib import Path

from tram.giao_viec.mau_g4 import ghi_receipt, nhan_luot


def _ghi(tep: Path, **gia_tri) -> None:
    data = json.loads(tep.read_text())
    data.update(gia_tri)
    with NamedTemporaryFile(mode='w', dir=tep.parent, delete=False) as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    Path(f.name).replace(tep)


def _vang(ma, out: bytes, nhan: str) -> bool:
    pattern = rb'Could not find service \"?' + re.escape(nhan.encode()) + rb'\"?(?: in domain[^\n]*)?\s*'
    # macOS 24G90 đo 19/10: mã 113, stderr thêm đúng dòng "Bad request." trước thông báo vắng service.
    return ma == 113 and re.fullmatch(rb'(?:Bad request\.\n)?' + pattern, out.strip()) is not None


def _quan_sat_don(pk, mien: list[str], nhan: str, chay, uids=None) -> tuple[list[dict], bool]:
    thay, sach = [], True
    for m in mien:
        uid_kiem = mien[0].split('/')[1]
        boc = pk.boc_lenh if m in (f'user/{uid_kiem}', f'gui/{uid_kiem}') else (lambda a: a)
        target = f'{m}/{nhan}'
        ma, out = chay(boc(['/bin/launchctl', 'print', target]))
        # Chỉ xét nhãn của lượt; print khác 0 là vắng, không so thông báo macOS.
        if ma != 0:
            continue
        pid = re.search(rb'^\s*pid = ([1-9][0-9]*)\s*$', out, re.M)
        row = {'mien': m, 'co_service': True, 'pid': int(pid[1]) if pid else None, 'danh_tinh': None}
        if pid:
            rc, ps = chay(['/bin/ps', '-p', pid[1].decode(), '-o', 'uid=,ruid=,lstart='])
            text = ps.decode(errors='replace').strip()
            if rc == 0 and re.fullmatch(r'\d+\s+\d+\s+\w{3}\s+\w{3}\s+\d+\s+[\d:]+\s+\d{4}', text):
                row['danh_tinh'] = text
                allowed = set(uids or (int(mien[0].split('/')[1]), int(mien[-1].split('/')[1])))
                uid, ruid = map(int, text.split()[:2])
                sach = sach and uid == ruid and uid in allowed
        sach = sach and row['danh_tinh'] is not None
        thay.append(row)
        chay(boc(['/bin/launchctl', 'bootout', target]))
        rc, _ = chay(boc(['/bin/launchctl', 'print', target]))
        sach = sach and rc != 0
        if pid:
            rc, ps = chay(['/bin/ps', '-p', pid[1].decode(), '-o', 'uid=,ruid=,lstart='])
            sach = sach and rc == 1 and not ps.strip()
    return thay, sach


def do_launchd(pk, luot: Path, receipt: Path, uid: int, operator: int, chay, *, mien=None, uids=None) -> list[dict]:
    mien = mien or [f'user/{uid}', f'gui/{uid}', f'gui/{operator}']
    ghi_receipt(receipt, luot, uid, operator, mien=mien)
    nhan = nhan_luot(luot)
    rows = []
    for ho_so, boc in (('ngoai', pk.boc_lenh), ('trong', pk.boc_luot(luot))):
        for binary, exe in (('goc', '/bin/launchctl'), ('copy', str(luot / 'launchctl-copy'))):
            exec_ma, _ = chay(boc([exe, 'help', 'submit']))
            for op in ('submit', 'bootstrap'):
                bat_dau = time.monotonic()
                def case_chay(argv):
                    if time.monotonic() - bat_dau > 45:
                        raise TimeoutError('ca G4 hết ngân sách 60 giây')
                    return chay(argv)
                nguon = ('submit' if op == 'submit' else 'launchd') + ('copy' if binary == 'copy' else '')
                label = f'{nhan}.{nguon}'
                if op == 'submit':
                    argv = [exe, op, '-l', label, '--', '/bin/sleep', '10']
                else:
                    p = luot / f'{nguon}.plist'
                    data = plistlib.dumps({'Label': label, 'ProgramArguments': ['/bin/sleep', '10'],
                                           'RunAtLoad': True}).decode()
                    script = f'printf %s {shlex.quote(data)} > {shlex.quote(str(p))}'
                    rc, _ = case_chay(pk.boc_lenh(['/bin/sh', '-ec', script]))
                    if rc != 0:
                        raise ValueError('không dựng được plist G4')
                    argv = [exe, op, mien[0], str(p)]
                _ghi(receipt, trang_thai='can-don', ca_hien_tai=f'{ho_so}:{binary}:{op}')
                ma, _ = case_chay(boc(argv))
                thay, sach = _quan_sat_don(pk, mien, label, case_chay, uids)
                sach = sach and not (ma == 0 and not thay)  # Nhận job nhưng mất dấu miền: giữ fixture.
                ket_luan = 'chua-ket-luan'
                if ho_so == 'trong' and (ma == 0 or thay):
                    ket_luan = 'lot'
                elif sach and exec_ma == 0:
                    if ho_so == 'ngoai' and ma == 0 and thay:
                        ket_luan = 'doi-chung-duong'
                    elif ho_so == 'trong' and ma not in (None, 0):
                        ket_luan = 'cho-bang-chung-os'
                rows.append({'ket_luan': ket_luan, 'ho_so': ho_so, 'binary': binary, 'lenh': op, 'exec_ma': exec_ma,
                             'ma': ma, 'service': thay, 'don': sach})
                _ghi(receipt, trang_thai='da-don' if sach else 'can-don', ket_qua=rows)
                if not sach or (ho_so == 'trong' and (ma == 0 or thay)):
                    return rows
    return rows
