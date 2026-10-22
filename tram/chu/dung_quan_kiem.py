"""Dừng label cố định; chưa nạp cũng phải chứng minh vắng, không nuốt mọi lỗi bootout."""
from tram.giao_viec.do_launchd_g4 import _vang


def dung_daemon(chay):
    nhan = 'vn.tram.quan-kiem'
    chay(['sudo', '/bin/launchctl', 'bootout', f'system/{nhan}'], check=False, timeout=30)
    r = chay(['sudo', '/bin/launchctl', 'print', f'system/{nhan}'],
             capture_output=True, timeout=30)
    if not _vang(r.returncode, (r.stdout or b'') + (r.stderr or b''), nhan):
        raise OSError('chua-chung-minh-daemon-da-dung')
