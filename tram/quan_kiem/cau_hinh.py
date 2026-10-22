"""Cấu hình/bằng chứng root; không cho env hay client lựa chọn mã, đường ghi hoặc policy."""
import json
import os
import pwd
from pathlib import Path

from tram.giao_viec.cong_that import doc_tep_root
from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh
from tram.quan_kiem.giao_thuc import fingerprint

CAU_HINH = Path('/usr/local/tram/quan-kiem/config.json')


def nap():
    c = json.loads(doc_tep_root(CAU_HINH))
    keys = {'uid_tram', 'uid_quan', 'gid_socket', 'home', 'goc', 'socket', 'python', 'entry',
            'policy', 'home_tram', 'g4', 'bang_chung'}
    if set(c) != keys or type(c['g4']) is not bool or not isinstance(c['policy'], dict):
        raise ValueError('cau-hinh-sai')
    if c['home'] != '/private/var/db/tram-quan-kiem' or \
            c['socket'] != '/private/var/db/tram-quan-kiem-socket/dieu-khien.sock' or \
            c['entry'] != '/usr/local/tram/quan-kiem/chay.py':
        raise ValueError('duong-cau-hinh-sai')
    u = pwd.getpwnam('tram-quan-kiem')
    if c['uid_quan'] != u.pw_uid or u.pw_uid in (0, c['uid_tram'], pwd.getpwnam('tram-kiem').pw_uid):
        raise ValueError('uid-khong-rieng')
    from tram.quan_kiem.policy import kiem_policy
    kiem_policy(c['policy'])
    return c


def kiem_ngu_canh(c):
    u = pwd.getpwnam('tram-quan-kiem')
    nc = ngu_canh_hien_hanh('tram-kiem')
    if os.getuid() != u.pw_uid or os.geteuid() != u.pw_uid or os.getppid() != 1 or nc.do_hoa:
        raise ValueError('khong-phai-system-quan-kiem')
    import grp
    from tram.chu.nhom_rieng import NHOM_NEN
    he = {grp.getgrnam(n).gr_gid for n in NHOM_NEN}
    if os.getgid() != u.pw_gid or set(os.getgroups()) - {u.pw_gid, c['gid_socket']} - he:
        raise ValueError('nhom-tien-trinh-sai')
    from tram.quan_kiem.bang_chung import dau_van_tay, MUC_G4
    bc = c['bang_chung']
    if not c['g4'] and (not isinstance(bc, dict) or bc.get('dau_van_tay') != dau_van_tay(c) or
                        bc.get('ket_luan') != {k: True for k in MUC_G4}):
        raise ValueError('chua-co-bang-chung-g4')
    return nc
