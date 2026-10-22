"""Audit ownership, không đổi UID/GID/mode file; rollback nhóm đúng cây có receipt R2; không theo symlink, không sửa ACL."""
import argparse
import json
import os
import plistlib
from pathlib import Path
import shlex
import stat
import subprocess

USERS = ('tram-kiem', 'tram-khe1', 'tram-tho')


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)


# Thư mục do macOS tự quản trong nhà user (Containers có symlink hệ thống, Mail/ContainerManager bị TCC khoá cả root):
# không đi vào, chỉ kiểm chính thư mục đó. Đo máy B 19/10: tram-khe1, tram-tho.
BO_QUA = ('Library',)


def acl_cua(path):
    """Các ACE của path; đọc từ các dòng sau dòng đầu `ls -lde` (dấu `+` bị `@` che khi có xattr)."""
    dong = run(['/bin/ls', '-lde', str(path)]).stdout.splitlines()[1:]
    return [d.strip().partition(': ')[2] for d in dong if d.strip()]


def acl_vo_hai(ace, chu):
    # macOS gắn sẵn cho nhà mới; chỉ chặn xoá, không phụ thuộc nhóm. ACE cấp cho chính chủ không mở cho ai khác.
    return ace == 'group:everyone deny delete' or ace.startswith(f'user:{chu} allow ')


def acl_la(chu):
    return lambda path: any(not acl_vo_hai(a, chu) for a in acl_cua(path))


def record(path, uid, gid, acl):
    st = path.lstat()
    if stat.S_ISLNK(st.st_mode):
        raise ValueError(f'symlink: {path}; dừng audit')
    if st.st_uid != uid:
        raise ValueError(f'owner lạ: {path}; dừng audit')
    if not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
        raise ValueError(f'Loại file không hỗ trợ: {path}')
    if acl(path):
        raise ValueError(f'ACL tại {path}; cần audit riêng, chưa sửa quyền')
    return {'path': str(path), 'uid': uid, 'old_gid': st.st_gid, 'new_gid': gid,
            'mode': stat.S_IMODE(st.st_mode), 'ino': st.st_ino, 'dev': st.st_dev}


def audit(root, uid, gid, *, staff_gid=20, acl=None, bo_qua=BO_QUA):
    if acl is None:
        import pwd
        acl = acl_la(pwd.getpwuid(uid).pw_name)
    rows = [record(root, uid, gid, acl)]
    if root.is_dir():
        def fail(error):
            raise error
        for current, dirs, files in os.walk(root, followlinks=False, onerror=fail):
            for name in sorted(dirs + files):
                rows.append(record(Path(current) / name, uid, gid, acl))
            if Path(current) == root:
                dirs[:] = [d for d in dirs if d not in bo_qua]
    return [r for r in rows if r['old_gid'] == staff_gid]


def audit_duoi(user, root, uid, gid, *, chay=subprocess.run):
    """Chạy audit dưới chính UID chủ cây (đọc được thư mục 0700 của nó, không cần root); lỗi => dừng."""
    from tram.kiem.toolchain import PYTHON
    ma = ("import json,sys;g={'__name__':'audit_nha'};exec(compile(sys.stdin.read(),'siet_nhom_ownership','exec'),g);"
          "from pathlib import Path;print(json.dumps(g['audit'](Path(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))))")
    r = chay(['sudo', '-u', user, '--', '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', f'{PYTHON}/bin/python3.12',
              '-I', '-B', '-c', ma, str(root), str(uid), str(gid)],
             input=Path(__file__).read_text(), capture_output=True, text=True, timeout=600, cwd='/')
    if r.returncode != 0:
        loi = (r.stderr.strip().splitlines() or ['không rõ'])[-1]
        raise ValueError(f'Audit {root} dưới {user} không đạt: {loi}')
    return json.loads(r.stdout)


def confirm(commands):
    for cmd in commands:
        print(shlex.join(cmd))
    if input('Chỉ chạy các lệnh trên — gõ dong-y: ') != 'dong-y':
        raise SystemExit('Chưa thay hệ thống')


def home(user):
    raw = run(['/usr/bin/dscl', '.', '-read', f'/Users/{user}', 'NFSHomeDirectory']).stdout
    value = raw.partition(':')[2].strip()
    if not value.startswith('/') or '\n' in value:
        raise ValueError(f'Home không hợp lệ: {user}')
    return Path(value)


def identities(so, obs):
    from tram.chu.tai_nguyen import user_cua_tram, cua_tram
    result = {}
    for user in USERS:
        who, group = user_cua_tram(so, user, obs), obs('nhom', user)
        if who is None or group is None or not cua_tram(so, 'nhom', user, group):
            raise ValueError(f'User/nhóm không đúng receipt R2: {user}')
        result[user] = {'user': who, 'group': group}
    return result


def roots_from_receipts(so, obs, people):
    from tram.chu.dinh_danh import cung
    roots = {}
    for user in USERS:
        for root in (home(user), Path('/Users/Shared/tram-kiem') if user == 'tram-kiem' else home(user)):
            if root == Path('/var/empty'):
                continue  # home không ghi được của tram-kiem, không đổi ownership hệ thống
            if root.resolve() != root or root.is_symlink() or '..' in root.parts:
                raise ValueError(f'Gốc không an toàn: {root}')
            matches = [m for m in so.muc().values() if m.su == 'da_tao' and m.kieu in ('nha', 'thu_muc')
                       and m.ten == str(root) and cung(m.kieu, m.dinh_danh, obs(m.kieu, m.ten) or {})]
            if not matches or root.lstat().st_uid != people[user]['user']['uid']:
                raise ValueError(f'Gốc không đúng receipt R2/owner: {root}')
            roots[root] = user
    return roots


def kiem_duong_chay(plist, nha_operator):
    from scripts.acl_tho import duong_can, thu_muc
    from tram.chu import dinh_danh
    from tram.chu.so_cai_tho import SoCai
    from tram.chu.tai_nguyen import cua_tram
    so = SoCai()
    for path in thu_muc(duong_can(plist)):
        hien = dinh_danh.quan_sat_that('acl_search', str(path))
        if not hien or not cua_tram(so, 'acl_search', str(path), hien):
            raise ValueError('Đường chạy trong nhà người vận hành chưa có ACL R2 đúng định danh')


def preflight(so, obs, config_roots=()):
    from tram.chu.cai_dat_tho import DAEMON
    if not DAEMON.exists():
        raise ValueError('Thiếu plist thợ; chưa có bản kê đường chạy để migration')
    with DAEMON.open('rb') as f:
        kiem_duong_chay(plistlib.load(f), Path.home())
    people = identities(so, obs)
    roots = roots_from_receipts(so, obs, people)
    for p in config_roots:
        if not p.exists() or not p.is_absolute() or p.resolve() != p or not any(p.is_relative_to(r) for r in roots):
            raise ValueError(f'Config thiếu/ngoài gốc có receipt hoặc qua symlink: {p}')
    for root, user in roots.items():
        audit_duoi(user, root, people[user]['user']['uid'], people[user]['group']['gid'])
    return people


def main():
    from tram.chu import dinh_danh
    from tram.chu.so_cai_tho import SoCai
    from tram.chu.nhom_rieng import lenh_bo_nhom
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('audit', 'rollback'))
    parser.add_argument('--identity-snapshot', type=Path)
    parser.add_argument('--config-root', type=Path, action='append', default=[])
    args = parser.parse_args()
    so, obs = SoCai(), dinh_danh.quan_sat_that
    with so.giu():
        if args.mode == 'audit':
            preflight(so, obs, args.config_root)
            print('Audit ownership đạt: chỉ quyền owner được dùng; không chown file.')
            return
        if args.identity_snapshot is None:
            raise ValueError('Rollback cần snapshot trước đổi nhóm; không cần snapshot ownership')
        people = identities(so, obs)
        before = json.loads(args.identity_snapshot.read_text())
        commands = []
        for user in USERS:
            if before[user]['identity'] != people[user]['user']:
                raise ValueError(f'User thay định danh: {user}')
            if before[user].get('new_group') != people[user]['group']:
                raise ValueError('Nhóm thay GID/GUID; không rollback')
            gid = before[user]['old_gid']
            if not str(gid).isdigit():
                raise ValueError('Snapshot old_gid không hợp lệ')
            commands.append(['sudo', '/usr/bin/dscl', '.', '-create', f'/Users/{user}', 'PrimaryGroupID', str(gid)])
            # Chỉ khôi phục membership đã gỡ, không thêm staff vốn chỉ là nhóm chính.
            # lenh_bo_nhom bỏ cả bốn nhóm nền OS, kể cả snapshot cũ từng kê nhầm 701/100.
            for command in lenh_bo_nhom(user, before[user].get('removed', [])):
                command[command.index('-d')] = '-a'
                commands.append(command)
        confirm(commands)
        for cmd in commands:
            if identities(so, obs) != people:
                raise ValueError('Danh tính đổi giữa chừng; dừng')
            subprocess.run(cmd, check=True, timeout=30)
        for user in USERS:
            gid = run(['/usr/bin/id', '-g', user]).stdout.strip()
            groups = set(run(['/usr/bin/id', '-Gn', user]).stdout.split())
            if gid != str(before[user]['old_gid']) or groups != set(before[user]['old_groups']):
                raise ValueError('Rollback chưa khớp nhóm cũ; giữ S6 đóng')


if __name__ == '__main__':
    main()
