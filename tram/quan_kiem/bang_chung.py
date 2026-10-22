"""Fingerprint của bản cài G4; kết luận để Đại ca ký sau đo, không tự coi digest là bằng chứng OS."""
import hashlib
import json
import os
import pwd
from pathlib import Path

from tram.giao_viec.ngu_canh_kiem import ban_macos, ma_may
from tram.kiem.toolchain import PREFIX, PHU_THUOC
from tram.quan_kiem.giao_thuc import fingerprint

# Đại ca 20/10 (cách 2): bỏ 'reboot' khỏi điều kiện cài chính thức — sau khởi động lại mà Uq không lên thì cổng đóng
# (an toàn khi hỏng); kiểm khởi động lại làm sau, khi Đại ca ở máy.
MUC_G4 = ('nguon-system', 'rao-ho-so', 'doc-canary', 'cong-cu', 'nhieu-luot', 'crash', 'don')


def _tep(p):
    """Tệp không cho mọi người đọc (đo 20/10: `test.netrc` 0600 trong Cellar git) → chỉ chủ/quyền/cỡ, không nội dung:
    vân tay tính dưới Đại ca và dưới Uq phải trùng nhau."""
    st = p.stat()
    if not st.st_mode & 0o004:
        return [str(p.resolve()), st.st_uid, st.st_gid, st.st_mode, st.st_size]
    with p.open('rb') as f:
        h = hashlib.file_digest(f, 'sha256').hexdigest()
    return [str(p.resolve()), st.st_uid, st.st_gid, st.st_mode, h]


def dau_van_tay(c):
    roots = [Path('/usr/local/tram/quan-kiem'), *map(Path, (*PREFIX, *PHU_THUOC))]
    tep = {}
    for root in roots:
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.name != 'config.json' and '__pycache__' not in p.parts:
                tep[str(p)] = _tep(p)
    from tram.kiem.deps_root import doc_bundle, duong_manifest
    for policy in c['policy'].values():
        if 'deps' in policy:
            p = duong_manifest(policy['deps'])
            if doc_bundle(p) != policy['deps']:
                raise ValueError('deps-khac-policy')
            for q in sorted(p.parent.iterdir()):
                tep[str(q)] = _tep(q)
    for p in map(Path, ['/usr/local/tram/tram-kiem.sb', '/usr/local/tram/tram-kiem.sb.json',
                        '/Library/LaunchDaemons/vn.tram.quan-kiem.plist', '/etc/sudoers.d/tram-quan-kiem',
                        '/etc/pam.d/sudo', '/etc/sudo.conf']):
        tep[str(p)] = _tep(p) if p.exists() else None
    users = {n: [*pwd.getpwnam(n)[2:4], sorted(os.getgrouplist(n, pwd.getpwnam(n).pw_gid))]
             for n in ('tram-kiem', 'tram-quan-kiem', pwd.getpwuid(c['uid_tram']).pw_name)}
    config = {k: v for k, v in c.items() if k not in ('g4', 'bang_chung')}
    return fingerprint(dict(ban=ban_macos(), may=ma_may(), config=config, users=users, tep=tep))


def in_mau():
    from tram.quan_kiem.cau_hinh import nap
    print(json.dumps({'dau_van_tay': dau_van_tay(nap()), 'ket_luan': {k: False for k in MUC_G4}}, indent=2))


if __name__ == '__main__':
    in_mau()
