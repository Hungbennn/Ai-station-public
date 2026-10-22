"""D155: đóng lối CLI cấp mã ghép máy cũ; luồng dashboard có passkey thuộc lát sau."""
import sys


def _cap_ma(args) -> int:
    print("Đã đóng cấp mã ghép máy cũ; chờ luồng dashboard có passkey (D155).", file=sys.stderr)
    return 2


def them_lenh_cap_ma(chu) -> None:
    c = chu.add_parser("cap-ma", help="In mã ghép dùng một lần (10 phút) cho Mac thợ từ xa")
    c.add_argument("may_id", help="Tên máy thợ mới, vd C")
    c.set_defaults(ham=_cap_ma)
