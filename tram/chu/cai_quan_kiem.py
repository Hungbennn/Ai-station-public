"""Cài Uq/LaunchDaemon bằng KeHoach và sổ R2; không khởi động lúc lập kế hoạch."""
import json
import plistlib
import subprocess
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.dung_quan_kiem import dung_daemon
from tram.chu.cai_dat import KeHoach
from tram.chu.cai_dat_kiem import tep_root
from tram.chu.nhom_rieng import nhom_tram, user_nhom, siet_user
from tram.chu.so_cai_tho import doi_soat
from tram.chu.tai_nguyen import TaiNguyen, kiem_truoc, tao
from tram.duong_dan import tram_home, goc_repo
from tram.kiem.toolchain import PYTHON

UQ = 'tram-quan-kiem'
NHAN = 'vn.tram.quan-kiem'
BUNDLE = Path('/usr/local/tram/quan-kiem')
HOME_Q = Path('/private/var/db/tram-quan-kiem')
SOCKET = Path('/private/var/db/tram-quan-kiem-socket')
DAEMON = Path('/Library/LaunchDaemons/vn.tram.quan-kiem.plist')
SUDOERS = Path('/etc/sudoers.d/tram-quan-kiem')
ENTRY = b'import sys\nsys.path.insert(0, "/usr/local/tram/quan-kiem")\nfrom tram.quan_kiem.chay import main\nmain()\n'


def plist():
    return plistlib.dumps({'Label': NHAN, 'UserName': UQ, 'GroupName': UQ, 'SessionCreate': True,
        'ProgramArguments': [f'{PYTHON}/bin/python3.12', '-I', str(BUNDLE / 'chay.py')],
        'WorkingDirectory': '/var/empty', 'RunAtLoad': True, 'KeepAlive': {'SuccessfulExit': False},
        'EnvironmentVariables': {'HOME': str(HOME_Q), 'TRAM_HOME': str(HOME_Q),
                                 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin'},
        'StandardOutPath': str(HOME_Q / 'daemon.log'), 'StandardErrorPath': str(HOME_Q / 'daemon.log')})


def thu_muc(p, chu, quan_sat, mode='0700'):
    return TaiNguyen('thu_muc', str(p), lambda i: [
        ['sudo', '/usr/bin/install', '-d', '-o', chu, '-g', 'wheel' if chu == 'root' else UQ, '-m', mode, str(p)]],
        lambda i: {'chu': None if chu == 'root' else chu,
                   'uid': 0 if chu == 'root' else (quan_sat('user', chu) or {}).get('uid')})


def lap(repo, tram, so, *, quan_sat=dinh_danh.quan_sat_that, chay=subprocess.run,
        policy=None, g4=True, bang_chung=None, deps_manifest=None):
    from tram.tho.principal import USER_RE
    from tram.chu.quan_kiem_membership import tai_nguyen as member
    if not USER_RE.fullmatch(tram) or tram in (UQ, 'tram-kiem', 'root'):
        raise ValueError('tai-khoan-tram-sai')
    if quan_sat('user', UQ) is not None and not so.co_ghi('user', UQ):
        raise ValueError(f'Gỡ G3 trước: sudo {PYTHON}/bin/python3.12 -I -B cong-cu/g3-tai-khoan.py go')
    from tram.quan_kiem.policy import chup_policy, kiem_policy
    policy = chup_policy() if policy is None else kiem_policy(policy)
    if deps_manifest is not None:
        from tram.kiem.deps_root import doc_bundle
        m = doc_bundle(deps_manifest)
        if m['du_an'] not in policy:
            raise ValueError('deps-du-an-chua-dang-ky')
        policy = policy | {m['du_an']: policy[m['du_an']] | {'deps': m}}
    kiem_policy(policy)
    if 'ben-station' in policy and 'deps' not in policy['ben-station']:
        raise ValueError('ben-station-can-deps-manifest')
    soan = tram_home() / 'cai-quan-kiem'
    tep = {soan / 'chay.py': ENTRY, soan / DAEMON.name: plist()}
    ds = [nhom_tram(UQ), user_nhom(UQ, '/var/empty', so, quan_sat),
          thu_muc(HOME_Q, UQ, quan_sat), thu_muc(SOCKET, UQ, quan_sat, '0750'),
          thu_muc(BUNDLE, 'root', quan_sat, '0755')]
    for p in sorted(Path(repo).joinpath('tram').rglob('*.py')):
        if p.is_symlink():
            raise ValueError('bundle-co-symlink')
        rel = p.relative_to(repo)
        tep[soan / rel] = p.read_bytes()
    parents = {p.parent.relative_to(soan) for p in tep if p.parent != soan}
    for rel in sorted({q for p in parents for q in (p, *p.parents) if str(q) != '.'}, key=lambda p: len(p.parts)):
        ds.append(thu_muc(BUNDLE / rel, 'root', quan_sat, '0755'))
    for p, b in tep.items():
        dich = DAEMON if p.name == DAEMON.name else BUNDLE / p.relative_to(soan)
        ds.append(tep_root(p, dich, b, '0644'))
    ds.append(member(tram, UQ, quan_sat))
    kiem_truoc(so, ds, quan_sat=quan_sat)
    def config():
        u, t, g = quan_sat('user', UQ), quan_sat('user', tram), quan_sat('nhom', UQ)
        c = dict(uid_tram=t['uid'], uid_quan=u['uid'], gid_socket=g['gid'], home=str(HOME_Q),
                 goc='/Users/Shared/tram-kiem', socket=str(SOCKET / 'dieu-khien.sock'),
                 python=f'{PYTHON}/bin/python3.12', entry=str(BUNDLE / 'chay.py'),
                 policy=policy, home_tram=str(tram_home()),
                 g4=g4, bang_chung=bang_chung)
        p = soan / 'config.json'
        p.write_text(json.dumps(c))
        tao(so, tep_root(p, BUNDLE / p.name, p.read_bytes(), '0644'), quan_sat=quan_sat, chay=chay)
        from tram.chu.quan_kiem_sudoers import chuyen
        chuyen(so, tram, soan, quan_sat=quan_sat, chay=chay)
    buoc = [('Đối soát sổ R2', lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    if quan_sat('tep', str(DAEMON), nhe=True) is not None:
        def dung_cu():
            from tram.chu.tai_nguyen import cua_tram
            if not cua_tram(so, 'tep', str(DAEMON), quan_sat('tep', str(DAEMON))):
                raise ValueError('daemon-cu-khong-khop-so')
            dung_daemon(chay)
        buoc.append(('Dừng daemon cũ đúng biên nhận trước thay mã', dung_cu))
    buoc += [(f'{tn.kieu} {tn.ten}: {tn.mo_ta()}',
              lambda tn=tn: tao(so, tn, quan_sat=quan_sat, chay=chay)) for tn in ds]
    buoc += [('Siết nhóm tiến trình mới Uq', lambda: siet_user(UQ, so, quan_sat, chay=chay)),
             ('Cài config root và chuyển sudoers 501→503 sang Uq→503, có sổ R2', config)]
    return KeHoach(tep, [['sudo', '/bin/launchctl', 'bootstrap', 'system', str(DAEMON)]],
                   ['Chỉ thực hiện sau dong-y; mặc định G4 dữ liệu giả, S6 còn đóng.',
                    f'Policy nguồn {goc_repo() / "du-an"}: ' + json.dumps(policy, ensure_ascii=False),
                    'Khởi động lại phiên trạm để nhận nhóm socket; không cấp ACL vào nhà Đại ca.'], buoc, 30)
