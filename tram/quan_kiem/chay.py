"""Điểm vào cố định của LaunchDaemon; worker chỉ chạy mã bundle tin cậy."""
import os
import sys
from contextlib import contextmanager
from functools import partial
from pathlib import Path

from tram.giao_viec.ban_chep import giu_khoa
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.cong_that import thu_hoi_theo_uid
from tram.quan_kiem.cau_hinh import nap, kiem_ngu_canh
from tram.quan_kiem.cong import dung
from tram.quan_kiem.dich_vu import nghe
from tram.quan_kiem.thuc_thi import thuc_thi, mo_that
from tram.quan_kiem.vong import QuanKiem


def _chi_tiet(e):
    """Lệnh con lỗi: lệnh thật sau tiền tố sudo/sandbox/env (mỗi đối số cắt 60 ký tự) + 200 byte cuối stderr."""
    import subprocess
    if not isinstance(e, subprocess.CalledProcessError):
        return ''
    a = [str(x) for x in (getattr(e, 'argv', None) or e.cmd or [])]
    i = max((k for k, x in enumerate(a) if x == '/usr/bin/env'), default=-1) + 1
    while i < len(a) and '=' in a[i] and not a[i].startswith('/'):
        i += 1
    loi = (e.stderr or b'')[-200:]
    loi = loi.decode('utf-8', 'replace') if isinstance(loi, bytes) else str(loi)
    return f" | lenh: {' '.join(x[:60] for x in a[i:i + 6])} | stderr: {loi.strip()!r}"


@contextmanager
def _ghi_loi_con(c, viec):
    """Tiến trình con chạy với stderr DEVNULL: để lại một dòng lý do (cắt 300 ký tự) trong daemon.log của Uq."""
    try:
        yield
    except BaseException as e:
        try:
            with open(Path(c['home']) / 'daemon.log', 'a') as f:
                ct = _chi_tiet(e)
                f.write(f'con {viec}: {type(e).__name__}: {(f"ma {e.returncode}" if ct else str(e))[:300]}{ct}\n')
        except OSError:
            pass
        raise


def main():
    c = nap()
    if os.getuid() != c['uid_quan'] or os.geteuid() != c['uid_quan']:
        raise PermissionError('sai-uid-quan-ly')
    os.environ['TRAM_HOME'] = c['home']
    if sys.argv[1:2] in (['mo'], ['don']):
        from tram.quan_kiem.cong import phuc_hoi
        with _ghi_loi_con(c, sys.argv[1]):
            phuc_hoi(c, sys.argv[1], sys.argv[2])
        return
    if sys.argv[1:2] == ['luot']:
        from tram.quan_kiem.luot import worker
        p = Path(sys.argv[2]).resolve()
        if p.parent != Path(c['home']) or not p.name.startswith('nhan-'):
            raise ValueError('duong-worker-sai')
        with _ghi_loi_con(c, 'luot'):
            worker(p, c)
        return
    nc = kiem_ngu_canh(c)
    pk = tu_cach_ly('user:tram-kiem')
    with giu_khoa(Path(c['home']) / 'daemon.khoa'):
        cong = dung(c, pk, nc, quan_sat=False)
        cong.dong('khoi-dong-can-xac-nhan-lai')
        q = QuanKiem(c['home'], cong, partial(thuc_thi, cfg=c, pk=pk), partial(mo_that, cfg=c, pk=pk))
        nghe(q, c)
