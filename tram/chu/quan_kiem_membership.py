"""Membership có sổ riêng, nhận diện cả GUID user và nhóm trước khi gỡ."""
import subprocess

from tram.chu import dinh_danh
from tram.chu.tai_nguyen import TaiNguyen


def quan_sat(kieu, ten, *, nhe=False, chay=subprocess.run):
    if kieu != 'thanh_vien':
        return dinh_danh.quan_sat_that(kieu, ten, nhe=nhe)
    g, u = ten.split('/')
    if dinh_danh.nhom(g) is None:
        return None
    r = chay(['/usr/sbin/dseditgroup', '-o', 'checkmember', '-m', u, g],
             capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and r.stdout.startswith('yes '):
        return {'user': dinh_danh.user(u), 'nhom': dinh_danh.nhom(g)}
    # dseditgroup 24G90 thoát 67 khi không là thành viên (đo 19/10 22:45); 64 = không có nhóm.
    if r.returncode == 67 and r.stdout.startswith('no '):
        return None
    raise OSError('khong-doc-duoc-membership')


def tai_nguyen(u, g, doc):
    return TaiNguyen('thanh_vien', f'{g}/{u}', lambda i: [
        ['sudo', '/usr/sbin/dseditgroup', '-o', 'edit', '-a', u, '-t', 'user', g]],
        lambda i: {'user': doc('user', u), 'nhom': doc('nhom', g)})
