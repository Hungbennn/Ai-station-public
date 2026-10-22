"""Nhóm chính riêng; sổ R2 chứng minh GID/GUID trước mọi thao tác dùng nhóm."""
import subprocess

from tram.chu.dinh_danh import cung
from tram.chu.tai_nguyen import TaiNguyen

# Máy B 24G90, 19/10: 701 lồng everyone; 100 lồng localaccounts, không gỡ theo user được.
NHOM_NEN = frozenset({'everyone', 'localaccounts', 'com.apple.sharepoint.group.1', '_lpoperator'})
NHOM_THUA = ('staff',)


def nhom_tram(u: str) -> TaiNguyen:
    return TaiNguyen('nhom', u, lambda i: [
        ['sudo', '/usr/sbin/dseditgroup', '-o', 'create', '-r', f'tram {u} {i}', u]],
        lambda i: {'user': u, 'ten_day_du': f'tram {u} {i}'})


def gid_tram(u, so, quan_sat):
    hien = quan_sat('nhom', u)
    if hien is None or not any(cung('nhom', m.dinh_danh, hien) for m in so.da_tao('nhom', u)):
        raise ValueError(f'Nhóm {u} chưa có biên nhận đúng GID/GUID — dừng')
    return str(hien['gid'])


def user_nhom(u, nha, so, quan_sat) -> TaiNguyen:
    def lenh(i):
        gid = f'<gid:{u}>' if i == '<id>' else gid_tram(u, so, quan_sat)
        return [['sudo', 'sysadminctl', '-addUser', u, '-fullName', f'tram {u} {i}',
                 '-home', nha, '-shell', '/usr/bin/false', '-GID', gid]]
    return TaiNguyen('user', u, lenh, lambda i: {'ten_day_du': f'tram {u} {i}'})


def nhom_phu(u, *, chay=subprocess.run):
    r = chay(['/usr/bin/id', '-Gn', u], capture_output=True, text=True, timeout=30, check=True)
    return set(r.stdout.split())


def lenh_bo_nhom(u, nhom):
    return [['sudo', '/usr/sbin/dseditgroup', '-o', 'edit', '-d', u, '-t', 'user', g]
            for g in sorted(nhom) if g not in NHOM_NEN
            and (g in NHOM_THUA or g.startswith("com.apple.sharepoint.group."))]


def siet_user(u, so, quan_sat, *, chay=subprocess.run, truoc_bo=lambda groups: None):
    from tram.chu.tai_nguyen import user_cua_tram
    if user_cua_tram(so, u, quan_sat) is None:
        raise ValueError(f'User {u} không khớp sổ; dừng')
    gid = gid_tram(u, so, quan_sat)
    groups = nhom_phu(u, chay=chay)
    removable = {c[-1] for c in lenh_bo_nhom(u, groups)}
    if groups - removable - {u} - NHOM_NEN:
        raise ValueError(f'User {u} có nhóm ngoài danh sách đã duyệt; dừng trước đổi GID')
    chay(['sudo', '/usr/bin/dscl', '.', '-create', f'/Users/{u}', 'PrimaryGroupID', gid], check=True, timeout=30)
    commands = lenh_bo_nhom(u, nhom_phu(u, chay=chay))
    truoc_bo([cmd[-1] for cmd in commands])  # fsync receipt trước xóa membership thực, sau đổi nhóm chính.
    for cmd in commands:
        if user_cua_tram(so, u, quan_sat) is None or gid_tram(u, so, quan_sat) != gid:
            raise ValueError('Danh tính đổi giữa chừng; dừng')
        chay(cmd, check=True, timeout=30)
    actual = chay(['/usr/bin/id', '-g', u], capture_output=True, text=True, timeout=30, check=True)
    if actual.stdout.strip() != gid or nhom_phu(u, chay=chay) - {u} - NHOM_NEN:
        raise ValueError(f'User {u} vẫn có nhóm thừa; dừng')
