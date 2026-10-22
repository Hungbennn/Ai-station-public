#!/usr/bin/env python3
# Giữ cài/gỡ chung hợp đồng receipt và định danh; không tách các bước root thành điểm vào khác.
"""Cài/gỡ duy nhất tài khoản đo D160. Đại ca chạy bằng root trong Terminal; không cài daemon."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import uuid

# Điểm vào root do người vận hành duyệt; chỉ import checkout chứa script, không cwd/env.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TEN = 'tram-quan-kiem'
RULE = f'{TEN} ALL=(tram-kiem) NOPASSWD: ALL\n'


def lenh(*a):
    r = subprocess.run(a, capture_output=True, text=True, timeout=15, env={'PATH': '/usr/bin:/bin:/usr/sbin:/sbin',
                                                                          'LC_ALL': 'C'})
    if r.returncode:
        raise RuntimeError(f'lệnh {Path(a[0]).name}/{a[1]} lỗi ({r.returncode}); giữ biên nhận')
    return r.stdout.strip()


class CaiGo:
    def __init__(self, goc=Path('/var/db/tram-g3-quan-kiem'),
                 sudoers=Path('/etc/sudoers.d/tram-g3-quan-kiem'), chay=lenh):
        self.goc, self.rule, self.chay = goc, sudoers, chay
        self.rc = goc / 'receipt.json'

    def ds(self, *a):
        return self.chay('/usr/bin/dscl', '.', *a)

    def luu(self, s):
        # Biên nhận có trước mutation. replace không theo symlink đích.
        p = self.goc / 'receipt.tmp'
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(s, f); f.flush(); os.fsync(f.fileno())
        os.replace(p, self.rc)
        fd = os.open(self.goc, os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)

    def doc(self):
        st = self.rc.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o600:
            raise RuntimeError('biên nhận sai chủ/quyền/loại')
        s = json.loads(self.rc.read_text())
        if s['name'] != TEN or s['rule'] != str(self.rule):
            raise RuntimeError('biên nhận khác đối tượng')
        return s

    def danh_sach(self, loai, attr):
        rows = [x.split() for x in self.ds('-list', loai, attr).splitlines()]
        if any(not x or x[0] == TEN for x in rows):
            raise RuntimeError(f'{TEN} đã tồn tại; không nhận sở hữu')
        if any(len(x) != 2 or not re.fullmatch(r'-?\d+', x[1]) for x in rows):
            raise RuntimeError('danh sách ID thiếu/sai; không chọn ID')
        return {int(x[1]) for x in rows}

    def ke_hoach(self):
        if self.rc.exists() or self.rc.is_symlink() or self.rule.exists() or self.rule.is_symlink():
            raise RuntimeError('đã có receipt/sudoers; dùng go với biên nhận, không ghi đè')
        users = self.danh_sach('/Users', 'UniqueID'); groups = self.danh_sach('/Groups', 'PrimaryGroupID')
        groups |= self.danh_sach('/Users', 'PrimaryGroupID')
        uid = next(n for n in range(505, 60000) if n not in users)
        gid = next(n for n in range(505, 60000) if n not in groups)
        tk = int(self.chay('/usr/bin/id', '-u', 'tram-kiem'))
        if tk != 503: raise RuntimeError('tram-kiem cần đúng UID 503 của phép đo G3 này')
        return dict(name=TEN, uid=uid, gid=gid, user_uuid=str(uuid.uuid4()).upper(),
                    group_uuid=str(uuid.uuid4()).upper(), run=str(uuid.uuid4()),
                    rule=str(self.rule), todo=[], made=[], removed=[])

    def cai(self, s):
        if s['uid'] in self.danh_sach('/Users', 'UniqueID') \
                or s['gid'] in (self.danh_sach('/Groups', 'PrimaryGroupID') |
                                self.danh_sach('/Users', 'PrimaryGroupID')):
            raise RuntimeError('ID đã bị chiếm sau kế hoạch; không tạo')
        self.luu(s)
        for kind, attrs in (
            ('Groups', {'PrimaryGroupID': str(s['gid']), 'GeneratedUID': s['group_uuid']}),
            ('Users', {'UniqueID': str(s['uid']), 'GeneratedUID': s['user_uuid'],
                       'PrimaryGroupID': str(s['gid']), 'NFSHomeDirectory': '/var/empty',
                       'UserShell': '/usr/bin/false', 'Password': '*', 'IsHidden': '1'})):
            # Kiểm lại collision sát bước tạo; không thay record có sẵn.
            ids = self.danh_sach('/'+kind, 'UniqueID' if kind == 'Users' else 'PrimaryGroupID')
            if s['uid' if kind == 'Users' else 'gid'] in ids:
                raise RuntimeError('ID bị chiếm sát bước tạo; giữ receipt')
            s['todo'].append(kind); self.luu(s)
            for attr, value in attrs.items(): self.ds('-create', f'/{kind}/{TEN}', attr, value)
            s['made'].append(kind); self.luu(s)
        text = f'# G3 D160 run={s["run"]}\n' + RULE
        tmp = self.goc / 'sudoers'
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o440)
        if os.getuid() == 0: os.fchown(fd, 0, 0)
        os.fchmod(fd, 0o440)
        with os.fdopen(fd, 'w') as f: f.write(text)
        self.chay('/usr/sbin/visudo', '-cf', str(tmp))
        s['todo'].append('sudoers'); s['sha256'] = hashlib.sha256(text.encode()).hexdigest(); self.luu(s)
        # Ghi độc quyền, không theo link, không thay file có sẵn.
        fd = os.open(self.rule, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o440)
        if os.getuid() == 0: os.fchown(fd, 0, 0)
        os.fchmod(fd, 0o440)
        with os.fdopen(fd, 'w') as f: f.write(text); f.flush(); os.fsync(f.fileno())
        s['inode'] = self.rule.stat().st_ino; s['made'].append('sudoers'); self.luu(s)
        self.chay('/usr/sbin/visudo', '-c')
        self.xac_minh(s)
        s['complete'] = True; self.luu(s)

    def xac_minh(self, s):
        # Preflight toàn bộ trước lần xoá đầu tiên. Partial không rõ thì giữ nguyên.
        for key in ('todo', 'made', 'removed'):
            items = s.get(key)
            if not isinstance(items, list) or any(x not in ('Groups', 'Users', 'sudoers') for x in items) \
                    or len(items) != len(set(items)):
                raise RuntimeError('receipt sai cấu trúc')
        if not set(s['removed']) <= set(s['made']) <= set(s['todo']):
            raise RuntimeError('receipt thiếu ý định/định danh; không gỡ')
        for kind in s['todo']:
            if kind in s['removed']: continue
            if kind not in s['made']: raise RuntimeError('mutation dở; cần đối soát thủ công theo receipt')
            if kind == 'sudoers':
                st = self.rule.lstat()
                if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_ino != s['inode'] \
                        or stat.S_IMODE(st.st_mode) != 0o440 \
                        or hashlib.sha256(self.rule.read_bytes()).hexdigest() != s['sha256']:
                    raise RuntimeError('sudoers thay đổi; không gỡ')
            else:
                attrs = {'GeneratedUID': s['user_uuid' if kind == 'Users' else 'group_uuid'],
                         'UniqueID' if kind == 'Users' else 'PrimaryGroupID': str(s['uid' if kind == 'Users' else 'gid'])}
                if kind == 'Users':
                    attrs.update(PrimaryGroupID=str(s['gid']), NFSHomeDirectory='/var/empty',
                                 UserShell='/usr/bin/false', Password='*', IsHidden='1')
                for attr, value in attrs.items():
                    # dscl 24G90 in IsHidden kèm tiền tố `dsAttrTypeNative:` (đo 19/10 21:40); giá trị vẫn so đúng.
                    if self.ds('-read', f'/{kind}/{TEN}', attr).removeprefix('dsAttrTypeNative:') != f'{attr}: {value}':
                        raise RuntimeError('danh tính/nhóm đã đổi; không gỡ')
                if kind == 'Groups':
                    group = self.ds('-read', f'/Groups/{TEN}')
                    key = None
                    for line in group.splitlines():
                        header = re.fullmatch(r'\s*([A-Za-z_][A-Za-z0-9_]*):\s*(.*)', line)
                        if header: key, value = header.groups()
                        else: value = line # Giá trị nhiều dòng vẫn thuộc thuộc tính vừa đọc.
                        if key in ('GroupMembership', 'GroupMembers', 'NestedGroups') and value.strip():
                            raise RuntimeError('nhóm có thành viên; không gỡ')
                    for line in self.ds('-list', '/Users', 'PrimaryGroupID').splitlines():
                        fields = line.split()
                        if len(fields) != 2 or not re.fullmatch(r'-?\d+', fields[1]):
                            raise RuntimeError('danh sách primary GID không đầy đủ; không gỡ')
                        if len(fields) == 2 and fields[1] == str(s['gid']) and fields[0] != TEN:
                            raise RuntimeError('nhóm có chủ khác; không gỡ')
        if 'Users' in s['made'] and 'Users' not in s['removed']:
            # Nền OS 24G90 (đo 19/10): 12 everyone, 61 localaccounts, 701/100 qua nhóm lồng — mọi user cục bộ đều có.
            nen = {str(s['gid']), '12', '61', '701', '100'}
            if not set(self.chay('/usr/bin/id', '-G', TEN).split()) <= nen:
                raise RuntimeError('tài khoản có nhóm phụ ngoài nền OS; không gỡ')

    def go(self, s):
        self.xac_minh(s)
        from tram.kiem.ngoai_le_uid import con_uid
        if con_uid(s['uid'], ten=TEN):
            raise RuntimeError('Uq còn tiến trình ngoài D162; không giết/không gỡ')
        for kind in ('sudoers', 'Users', 'Groups'):
            if kind not in s['made'] or kind in s['removed']: continue
            self.xac_minh(s)
            s['removing'] = kind; self.luu(s)
            if kind == 'sudoers': self.rule.unlink()
            else:
                self.ds('-delete', f'/{kind}/{TEN}')
                self.danh_sach('/'+kind, 'UniqueID' if kind == 'Users' else 'PrimaryGroupID')
            s['removed'].append(kind); s.pop('removing'); self.luu(s)
        self.chay('/usr/sbin/visudo', '-c')
        s['uninstalled'] = True; self.luu(s)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('cai', 'go'):
        raise RuntimeError('dùng: sudo /usr/bin/python3 -I -B cong-cu/g3-tai-khoan.py cai|go')
    if os.getuid() != 0 or not sys.stdin.isatty():
        raise RuntimeError('Đại ca chạy bằng sudo trong Terminal.app tương tác')
    c = CaiGo()
    # /etc là symlink hệ thống; chuẩn hoá, kiểm toàn chuỗi cha tin cậy.
    c.rule = c.rule.parent.resolve(strict=True) / c.rule.name
    c.goc = c.goc.parent.resolve(strict=True) / c.goc.name
    c.rc = c.goc / 'receipt.json'
    for base in (c.goc.parent, c.rule.parent):
        for p in (base, *base.parents):
            st = p.lstat()
            if not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o022:
                raise RuntimeError('cha hệ thống không tin cậy')
    if c.goc.exists() or c.goc.is_symlink():
        st = c.goc.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or stat.S_IMODE(st.st_mode) != 0o700:
            raise RuntimeError('thư mục receipt sai chủ/quyền/loại')
    mode = sys.argv[1]
    s = c.ke_hoach() if mode == 'cai' else c.doc()
    if mode == 'go': c.xac_minh(s)
    print(f'{mode}: {TEN}, UID={s["uid"]}, nhóm riêng GID={s["gid"]}; nhà /var/empty, shell false, không daemon.')
    print('Tạo/xoá record user + group; sudoers duy nhất:', c.rule)
    print(RULE, end=''); print('Biên nhận (giữ cả khi gỡ):', c.rc)
    if input('Gõ dong-y: ') != 'dong-y': return 2
    if not c.goc.exists(): c.goc.mkdir(mode=0o700)
    st = c.goc.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or stat.S_IMODE(st.st_mode) != 0o700:
        raise RuntimeError('thư mục receipt sai chủ/quyền/loại')
    fd = os.open(c.goc / 'khoa', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if mode == 'cai':
            # Đọc lại sau khoá; không dùng số ID đã bị người khác chiếm sau lúc in kế hoạch.
            new = c.ke_hoach()
            if (new['uid'], new['gid']) != (s['uid'], s['gid']): raise RuntimeError('ID đã đổi; chạy lại kế hoạch')
            c.cai(s)
        else: c.go(c.doc())
    finally: os.close(fd)
    print('XONG; receipt:', c.rc)
    return 0


if __name__ == '__main__':
    try: sys.exit(main())
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as e:
        print('DỪNG:', e, file=sys.stderr); sys.exit(3)
