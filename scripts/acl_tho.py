"""Cài/gỡ ACL quản lý có R2; in kế hoạch và chờ dong-y. Chỉ chạy trên máy B sau duyệt."""
import argparse
from pathlib import Path
import plistlib

from tram.chu import dinh_danh
from tram.chu.acl_tho import tai_nguyen, kiem_quyen
from tram.chu.cai_dat_tho import DAEMON
from tram.chu.go_cai_dat_tho import go, lenh_go
from tram.chu.so_cai_tho import SoCai, doi_soat
from tram.chu.tai_nguyen import kiem_truoc, tao, user_cua_tram

NHA = Path('/Users/dai-ca')


def duong_can(plist):
    args = plist['ProgramArguments']
    repo = Path(plist['WorkingDirectory'])
    if plist.get('UserName') != 'tram-tho' or not args or not Path(args[0]).is_absolute():
        raise ValueError('Plist không phải quản lý tram-tho/uv tuyệt đối')
    if args[1:] != ['run', '--offline', '--no-sync', '--project', str(repo), 'tram', 'tho', 'chay']:
        raise ValueError('Plist phải ghim uv offline/no-sync; cài lại plist trước migration')
    paths = [(repo, '-x'), (repo / 'pyproject.toml', '-r'), (repo / 'tram/__init__.py', '-r'),
             (Path(args[0]), '-x'), (repo / '.venv/bin/python', '-x'), (repo / '.venv/pyvenv.cfg', '-r')]
    result = []
    for path, mode in paths:
        if not path.is_absolute() or '..' in path.parts or not path.exists():
            raise ValueError('Đường chạy thiếu hoặc không tuyệt đối')
        result.extend(((path, mode), (path.resolve(strict=True), mode)))
    return sorted(set(result))


def thu_muc(paths):
    result = {NHA}
    for path, mode in paths:
        for p in path.parents:
            if p.is_relative_to(NHA):
                result.add(p.resolve(strict=True))
    return sorted(result, key=lambda p: (len(p.parts), str(p)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('cai', 'kiem', 'go'))
    parser.add_argument('--plist', type=Path, default=DAEMON)
    args = parser.parse_args()
    so, obs = SoCai(), dinh_danh.quan_sat_that
    with so.giu():
        if user_cua_tram(so, 'tram-tho', obs) is None:
            raise ValueError('tram-tho không khớp UID/GUID trong sổ')
        if args.mode == 'go':
            items = [m for m in so.muc().values() if m.kieu == 'acl_search' and m.su in ('du_dinh', 'da_tao')]
            for m in items:
                print(lenh_go(m))
            if input('Gỡ đúng ACL đã tạo — gõ dong-y: ') != 'dong-y':
                return
            doi_soat(so, obs, dinh_danh.khop)
            import subprocess
            for m in items:
                go(so, m, quan_sat=obs, chay=subprocess.run, bao=print)
            return
        pl = plistlib.loads(args.plist.read_bytes())
        patch = None
        old = pl['ProgramArguments']
        if args.mode == 'cai' and old[1:] == ['run', '--project', pl['WorkingDirectory'], 'tram', 'tho', 'chay']:
            from tram.chu.cai_dat_kiem import tep_root
            pl['ProgramArguments'] = [old[0], 'run', '--offline', '--no-sync', *old[2:]]
            patch = plistlib.dumps(pl)
            staged = so.p.parent / 'tho-offline.plist'
        paths = duong_can(pl)
        resources = [tai_nguyen(p) for p in thu_muc(paths)]
        if args.mode == 'kiem':
            from tram.chu.tai_nguyen import cua_tram
            if not all(cua_tram(so, r.kieu, r.ten, obs(r.kieu, r.ten) or {}) for r in resources):
                raise ValueError('ACL chưa khớp biên nhận; giữ cổng đóng')
            kiem_quyen(paths)
            import subprocess
            subprocess.run(['sudo', '-u', 'tram-tho', '/usr/bin/env', '-i', 'HOME=/Users/tram-tho',
                            'PATH=/usr/bin:/bin:/usr/sbin:/sbin', 'PYTHONDONTWRITEBYTECODE=1',
                            *pl['ProgramArguments'][:-3], 'python', '-I', '-B', '-c',
                            'import tram, ssl, sqlite3, ctypes; from tram.tho import cau_hinh'],
                           cwd=pl['WorkingDirectory'], check=True, timeout=60)
            return
        if patch is not None:
            resources.append(tep_root(staged, args.plist, patch, '0644'))
        actions = kiem_truoc(so, resources, quan_sat=obs)
        for r, action in zip(resources, actions):
            print(action, r.mo_ta())
        if input('Chỉ cấp search cho quản lý tram-tho — gõ dong-y: ') != 'dong-y':
            return
        if patch is not None:
            from tram.chu.cai_dat import KeHoach, thuc_hien
            thuc_hien(KeHoach({staged: patch}, [], []))
        doi_soat(so, obs, dinh_danh.khop)
        for r in resources:
            tao(so, r, quan_sat=obs)
        print('ACL đã ghi sổ; sau migration phải chạy kiem và smoke import trước khởi động daemon.')


if __name__ == '__main__':
    main()
