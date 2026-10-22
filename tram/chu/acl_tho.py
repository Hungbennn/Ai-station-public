"""ACL search riêng cho quản lý tin cậy; R2 giữ định danh thư mục, user và toàn ACL để gỡ đúng mục."""
import os
from pathlib import Path
import stat
import subprocess

from tram.chu.tai_nguyen import TaiNguyen

ACE = 'user:tram-tho allow search'


def nguoi_that():
    from tram.chu.dinh_danh import user
    who = user('tram-tho')
    if who is None:
        raise ValueError('Chưa có quản lý tram-tho')
    return {k: who[k] for k in ('uid', 'guid')}


def doc_acl(path):
    r = subprocess.run(['/bin/ls', '-lde', str(path)], check=True, capture_output=True, text=True, timeout=30)
    rows = r.stdout.splitlines()[1:]
    if any(not row.strip().partition(':')[0].isdigit() for row in rows):
        raise ValueError('Không đọc được ACL')
    return [row.strip().partition(':')[2].strip() for row in rows]


def danh_tinh(path, doc, nguoi):
    st = path.lstat()
    if not stat.S_ISDIR(st.st_mode) or path.resolve() != path or st.st_mode & 0o002:
        raise ValueError('Đường ACL không phải thư mục thật hoặc cho mọi người ghi')
    acl = doc(path)
    mine = [a for a in acl if 'tram-tho' in a]
    if mine and mine != [ACE]:
        raise ValueError('ACL tram-tho khác search; kiểm tay')
    return {'ino': st.st_ino, 'dev': st.st_dev, 'uid': st.st_uid, 'user': nguoi(), 'acl': sorted(acl)}


def quan_sat(path, *, doc=doc_acl, nguoi=nguoi_that):
    if not os.path.lexists(path):
        return None
    identity = danh_tinh(path, doc, nguoi)
    return identity if ACE in identity['acl'] else None


def tai_nguyen(path, *, doc=doc_acl, nguoi=nguoi_that):
    identity = danh_tinh(path, doc, nguoi)
    expected = {**identity, 'acl': sorted(set(identity['acl']) | {ACE})}
    def lenh(i):
        if danh_tinh(path, doc, nguoi) != identity:
            raise ValueError('ACL hoặc thư mục đổi sau preview; dừng')
        return [['sudo', '/bin/chmod', '+a', ACE, str(path)]]
    return TaiNguyen('acl_search', str(path), lenh, lambda i: expected)


def kiem_quyen(paths, *, chay=subprocess.run):
    # Xác minh sudo/id riêng: exit 1 của sudo lỗi không được tính thành test âm đạt.
    for user in ('tram-tho', 'tram-khe1', 'tram-kiem'):
        r = chay(['sudo', '-u', user, '/usr/bin/true'], timeout=30)
        if r.returncode:
            raise ValueError('Không chạy được đối chứng sudo; giữ cổng đóng')
    for path, mode in paths:
        r = chay(['sudo', '-u', 'tram-tho', '/bin/test', mode, str(path)], timeout=30)
        if r.returncode:
            raise ValueError('Quản lý không đọc/chạy được đường cần thiết')
    for user in ('tram-khe1', 'tram-kiem'):
        r = chay(['sudo', '-u', user, '/bin/test', '-x', '/Users/dai-ca'], timeout=30)
        if r.returncode != 1:
            raise ValueError('Khe/kiểm còn vào được nhà Đại ca hoặc phép thử lỗi')
