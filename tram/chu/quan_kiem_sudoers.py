"""Đổi đúng dòng legacy đã có biên nhận; không phục hồi lối 501 chạy kiểm khi gỡ."""
from pathlib import Path

from tram.chu.cai_dat_kiem import tep_root
from tram.chu.tai_nguyen import tao, cua_tram
from tram.tho.quyen_kiem import dong_sudoers_kiem


LEGACY = Path('/etc/sudoers.d/tram-tho')
DICH = Path('/etc/sudoers.d/tram-quan-kiem')


def chuyen(so, tram, soan, *, quan_sat, chay):
    from tram.chu.so_cai_tho import SoCai
    with SoCai().giu() as legacy:
        _bo_cu(legacy, tram, soan, quan_sat=quan_sat, chay=chay)
    p = soan / 'quan.sudoers'
    p.write_text('Defaults:tram-quan-kiem !requiretty\n' +
                 dong_sudoers_kiem(tram='tram-quan-kiem', tram_kiem='tram-kiem', co_che='user') + '\n')
    tao(so, tep_root(p, DICH, p.read_bytes(), '0444', truoc=(['sudo', '/usr/sbin/visudo', '-cf', str(p)],)),
        quan_sat=quan_sat, chay=chay)


def _bo_cu(so, tram, soan, *, quan_sat, chay):
    hien = quan_sat('tep', str(LEGACY))
    if hien is not None:
        if not cua_tram(so, 'tep', str(LEGACY), hien):
            raise ValueError('sudoers-cu-khong-khop-so')
        b = chay(['sudo', '/bin/cat', str(LEGACY)], capture_output=True, check=True, timeout=30).stdout
        cu = b.decode().splitlines()
        cam = {dong_sudoers_kiem(tram=tram, tram_kiem='tram-kiem', co_che=k) for k in ('user', 'sandbox')}
        moi = ('\n'.join(x for x in cu if x not in cam) + '\n').encode()
        if any(tram in x and 'tram-kiem' in x for x in moi.decode().splitlines() if not x.startswith('#')):
            raise ValueError('sudoers-cu-khong-nhan-dien')
        p = soan / 'legacy.sudoers'
        p.write_bytes(moi)
        tao(so, tep_root(p, LEGACY, moi, '0440', truoc=(['sudo', '/usr/sbin/visudo', '-cf', str(p)],)),
            quan_sat=quan_sat, chay=chay)
