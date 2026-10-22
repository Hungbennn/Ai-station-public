"""Socket cục bộ; hai kết nối tối đa để huỷ/trạng thái không bị lượt đang chạy chặn."""
import os
import select
import socket
import sys
import threading
import time
from pathlib import Path

from tram.cau_hinh.lenh import khop_bat_ky
from tram.quan_kiem.giao_thuc import digest_policy, doc, ghi, yeu_cau, nhan, fingerprint, HAN_DOC
from tram.quan_kiem.peer import xac_thuc


def _co_log(c):
    try:
        return (Path(c['home']) / 'daemon.log').stat().st_size
    except (KeyError, OSError):
        return 0


def _moi_ghi(c, tu):
    """Dòng `con …` tiến trình con vừa ghi vào daemon.log trong yêu cầu này (đã cắt, không env) — trả kèm cho trạm."""
    try:
        with open(Path(c['home']) / 'daemon.log', 'rb') as f:
            f.seek(tu)
            return [x for x in f.read(4096).decode(errors='replace').splitlines() if x.startswith('con ')][-1:]
    except (KeyError, OSError):
        return []


def phuc_vu(s, q, c):
    ma_loi, tu = 'loi-kenh', _co_log(c)
    try:
        xac_thuc(s, c['uid_tram'])
        het = time.monotonic() + HAN_DOC
        d = yeu_cau(doc(s, het=het))
        if d['op'] == 'trang-thai':
            ghi(s, q.trang_thai(d['id']))
        elif d['op'] == 'huy':
            ghi(s, {'huy': q.huy(d['id'])})
        elif d['op'] == 'mo':
            ma_loi = 'loi-mo'
            q.mo()
            ghi(s, {'cong': q.cong.trang_thai()['trang_thai']})
        else:
            ma_loi = 'loi-chay'
            if c['g4'] and not d['giao_id'].startswith('g4-'):
                raise ValueError('g4-chi-du-lieu-gia')
            policy = c['policy'].get(d['du_an'])
            if not policy or d['policy'] != digest_policy(
                    policy['cho_phep'], policy['mac_dinh'], policy.get('deps')) or any(
                    not khop_bat_ky(x, policy['cho_phep']) for x in d['lenh']) or any(
                    x not in d['lenh'] for x in policy['mac_dinh']):
                raise ValueError('policy-sai')
            nguon, env = nhan(s, d['nguon_n'], het), nhan(s, d['env_n'], het)
            def mat_kenh():
                return bool(select.select([s], [], [], 0)[0])
            ghi(s, q.chay(d, nguon, env, mat_kenh))
    except (Exception, KeyboardInterrupt) as e:
        q.dong()
        try:
            print(f'{type(e).__name__}: {ma_loi}', file=sys.stderr, flush=True)
        except OSError:
            pass
        try:
            ghi(s, {'loi': 'khong-cong-nhan', 'ly_do': ' | '.join([f'{type(e).__name__}: {ma_loi}', *_moi_ghi(c, tu)])})
        except OSError:
            pass
    finally:
        s.close()


def nghe(q, c):
    p = Path(c['socket'])
    if os.path.lexists(p):
        st = p.lstat()
        import stat
        if not stat.S_ISSOCK(st.st_mode) or st.st_uid != os.getuid():
            raise PermissionError('socket-cu-khong-thuoc-quan-ly')
        p.unlink()
    cho = threading.BoundedSemaphore(2)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(p))
        os.chown(p, -1, c['gid_socket'])
        os.chmod(p, 0o660)
        server.listen(2)
        while True:
            s, _ = server.accept()
            if not cho.acquire(blocking=False):
                s.close()
                continue
            def mot(s=s):
                try:
                    phuc_vu(s, q, c)
                finally:
                    cho.release()
            threading.Thread(target=mot, daemon=False).start()
