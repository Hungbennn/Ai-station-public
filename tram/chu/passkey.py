"""CLI cứu hộ chỉ ở Terminal của chủ trạm; TTY không thay cách ly quyền OS."""
import select
import sys
from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.duong_dan import tram_home
from tram.passkey.dich_vu import DichVu


def thuc_hien(dv, khoi_phuc, vao, ra, *, doi=select.select):
    if not vao.isatty() or not ra.isatty():
        return 1
    ra.write('Sẽ thu hồi mọi passkey, phiên và mã cũ.\n' if khoi_phuc else 'Sẽ cấp mã mới, huỷ mã cũ.\n')
    ra.write('Gõ dong-y trong 120 giây: ')
    ra.flush()
    if not doi([vao], [], [], 120)[0] or vao.readline(32).strip() != 'dong-y':
        ra.write('Chưa đổi gì.\n')
        return 1
    ma = dv.cap_ma(khoi_phuc=khoi_phuc)
    ra.write('Mã đăng ký dùng một lần, hạn 10 phút:\n'+ma+'\n')
    ra.flush()
    return 0


def chay(args):
    try:
        ch = nap_cau_hinh_tram()
        if len(ch.dai_ca_logins) != 1 or not ch.ten_may_b:
            raise ValueError()
        dv = DichVu(tram_home()/'passkey.db', ch.dai_ca_logins[0], ch.ten_may_b)
        return thuc_hien(dv, args.viec_passkey == 'khoi-phuc', sys.stdin, sys.stdout)
    except Exception:
        print('Không hoàn tất. Kiểm trạng thái trước khi cấp mã lại.', file=sys.stderr)
        return 2


def them_lenh(chu):
    nhom = chu.add_parser('passkey', help='Mã đăng ký và khôi phục passkey tại máy B')
    sub = nhom.add_subparsers(dest='viec_passkey', required=True)
    for ten in ('cap-ma', 'khoi-phuc'):
        sub.add_parser(ten).set_defaults(ham=chay)
