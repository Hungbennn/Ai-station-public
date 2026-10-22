"""Gỡ đúng tài nguyên Uq có sổ; không pkill, không khôi phục sudoers 501→503."""
from pathlib import Path

from tram.chu import dinh_danh
from tram.chu.dung_quan_kiem import dung_daemon
from tram.chu.cai_dat import KeHoach
from tram.chu.cai_quan_kiem import UQ, NHAN, BUNDLE, HOME_Q, SOCKET, DAEMON, SUDOERS
from tram.chu.so_cai_tho import doi_soat
from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.ngoai_le_uid import con_uid


def thuoc(m):
    if m.kieu in ('user', 'nhom'):
        return m.ten == UQ
    if m.kieu == 'thanh_vien':
        return m.ten.startswith(UQ + '/')
    p = Path(m.ten)
    return p in (HOME_Q, SOCKET, DAEMON, SUDOERS) or p == BUNDLE or BUNDLE in p.parents


def lenh(m):
    if m.kieu == 'thanh_vien':
        g, u = m.ten.split('/')
        return [['sudo', '/usr/sbin/dseditgroup', '-o', 'edit', '-d', u, '-t', 'user', g]]
    if m.kieu == 'user':
        return [['sudo', '/usr/sbin/sysadminctl', '-deleteUser', UQ, '-keepHome']]
    if m.kieu == 'nhom':
        return [['sudo', '/usr/sbin/dseditgroup', '-o', 'delete', UQ]]
    if m.ten in (str(HOME_Q), str(SOCKET)):
        return [['sudo', '/bin/rm', '-rf', m.ten]]
    return [['sudo', '/bin/rm', '-f', m.ten]] if m.kieu == 'tep' else [['sudo', '/bin/rmdir', m.ten]]


def lap_go(so, *, quan_sat, chay, chup=chup_nhan):
    ds = { (m.kieu, m.ten): m for m in so.muc().values() if m.su in ('du_dinh', 'da_tao') and thuoc(m) }
    def go(m):
        m = so.muc()[m.id]
        if m.su != 'da_tao':
            return
        h = quan_sat(m.kieu, m.ten)
        if h is not None and not dinh_danh.cung(m.kieu, m.dinh_danh, h):
            raise ValueError('tai-nguyen-da-doi-khong-go')
        if h is not None:
            if m.ten == str(DAEMON):
                dung_daemon(chay)
            if m.kieu == 'user' and con_uid(h['uid'], chup=chup, ten=UQ):
                raise ValueError('Uq-con-tien-trinh-khong-xoa-user')
            for a in lenh(m):
                chay(a, check=True, timeout=30)
            if quan_sat(m.kieu, m.ten) is not None:
                raise OSError('go-chua-xong')
        for cu in so.da_tao(m.kieu, m.ten):
            so.ket(cu.id, 'da_go')
    def thu_tu(m):
        if m.ten == str(DAEMON):
            return (0, 0)
        if m.ten == str(SUDOERS):
            return (1, 0)
        return ({'thanh_vien': 2, 'tep': 3, 'thu_muc': 4, 'user': 5, 'nhom': 6}[m.kieu], -len(Path(m.ten).parts))
    buoc = [('Đối soát sổ R2', lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    def truoc_go():
        if ('tep', str(DAEMON)) in ds and quan_sat('tep', str(DAEMON)) is not None:
            m = so.muc()[ds['tep', str(DAEMON)].id]
            if not dinh_danh.cung('tep', m.dinh_danh, quan_sat('tep', str(DAEMON))):
                raise ValueError('daemon-da-doi-khong-go')
            dung_daemon(chay)
        u = quan_sat('user', UQ)
        if u and con_uid(u['uid'], chup=chup, ten=UQ):
            raise ValueError('Uq-con-worker-khong-xoa-du-lieu')
    buoc.append(('Dừng daemon sở hữu; xác nhận hết worker trước xoá dữ liệu', truoc_go))
    buoc += [(f'Gỡ {m.kieu} {m.ten}: {lenh(m)}', lambda m=m: go(m)) for m in sorted(ds.values(), key=thu_tu)]
    return KeHoach({}, [], ['Sẽ xoá dữ liệu lượt/log Uq; sao lưu chứng cứ trước dong-y. S6 giữ đóng.'], buoc)
