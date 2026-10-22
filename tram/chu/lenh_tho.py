"""Lệnh phía TÀI KHOẢN TRẠM cho máy thợ (lát 3a-2): `tram chu cai-dat-tho`, `tram chu cap-token-may`,
`tram chu kiem-cach-ly` (spec 3 §5.1, §7.3 mục 5, 7; H9). Mọi thay đổi hệ thống: liệt kê trước, chờ `dong-y`.
Lát 3c: principal kiểm lại chỉ đọc từ `cach_ly.tram_kiem` (`doc_principal_kiem`) — bỏ cờ `--tram-kiem`."""
import shutil
import subprocess
import sys
from contextlib import ExitStack, closing
from datetime import datetime, timezone


def _hoi(args, cau: str = "Gõ dong-y để thực hiện: ") -> bool:
    return bool(args.dong_y) or input(cau).strip() == "dong-y"


def _cai_dat_tho(args) -> int:
    import getpass

    from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
    from tram.cau_hinh.principal_kiem import doc_principal_kiem
    from tram.chu.cai_dat import in_ke_hoach, thuc_hien
    from tram.chu.cai_dat_tho import lap_ke_hoach_tho
    from tram.chu.so_cai_tho import SoCai
    from tram.chu.tai_nguyen import LoiCaiDat
    from tram.duong_dan import goc_repo
    khe = dict(x.split("=", 1) for x in args.khe)
    so, khoa = SoCai(), ExitStack()
    try:
        khoa.enter_context(so.giu())          # R4: cả lần cài (kế hoạch → dong-y → chạy) giữ khoá sổ, không chờ
        kh = lap_ke_hoach_tho(uv=shutil.which("uv") or "uv", repo=goc_repo(), tram=getpass.getuser(),
                              quan_ly=args.quan_ly, khe=khe, co_che=args.co_che,
                              kiem=None if args.chi_tho else doc_principal_kiem(),
                              thu_muc_kiem=None if args.chi_tho else nap_cau_hinh_giao_viec().thu_muc_kiem,
                              db_nghiep_vu=() if args.chi_tho else nap_cau_hinh_cach_ly().db_nghiep_vu, so=so,
                              chi_tho=args.chi_tho, giu_tat=args.giu_tat)
    except (ValueError, OSError) as e:         # cấu hình/sổ lỗi, tài nguyên lạ, SoCaiDangBan, dscl lỗi
        khoa.close()
        print(f"Không cài: {e}", file=sys.stderr)
        return 2
    with khoa:
        print(in_ke_hoach(kh))
        if not _hoi(args):
            print("Không làm gì.")
            return 1
        try:
            thuc_hien(kh)
        except (LoiCaiDat, OSError, ValueError, subprocess.SubprocessError) as e:
            print(f"Dừng giữa chừng: {e}\nSổ cài đặt đã ghi đúng phần đã tạo — `tram chu go-cai-dat-tho` gỡ được.",
                  file=sys.stderr)
            return 1
    print("Đã cài. Tiếp theo: các bước trong mục Cảnh báo ở trên.")
    return 0


def _cap_token_may(args) -> int:
    from tram.phieu.kho import mo_kho_phieu
    from tram.phieu.may import cap_token_may
    if sys.stdout.isatty():
        print("Token máy chỉ được in vào ống (pipe) tới `tram tho nhan-token` — không hiện ra màn hình:\n"
              f"  tram chu cap-token-may {args.may_id} --dong-y | sudo -u <tài khoản quản lý thợ> -H … tram tho "
              "nhan-token", file=sys.stderr)
        return 2
    print(f"Sẽ cấp token mới cho máy {args.may_id} (token cũ hết hiệu lực).", file=sys.stderr)
    if not args.dong_y:
        print("Cần --dong-y khi chạy trong ống.", file=sys.stderr)
        return 1
    with closing(mo_kho_phieu()) as kho:
        print(cap_token_may(kho, args.may_id, luc=datetime.now(timezone.utc)))
    return 0


def _kiem_cach_ly(args) -> int:
    from tram.chu.kiem_cach_ly import kiem_cach_ly
    van_ban, ma = kiem_cach_ly(args.principal)
    print(van_ban)
    return ma


def _go_cai_dat_tho(args) -> int:
    from tram.chu.lenh_go_tho import lenh_cli
    return lenh_cli(args, hoi=_hoi)


def them_lenh_chu_tho(chu) -> None:
    c = chu.add_parser("cai-dat-tho", help="Kế hoạch cài máy thợ B: user, sudoers, launchd (chờ dong-y, chờ S6)")
    c.add_argument("--quan-ly", default="tram-tho", help="User macOS của tiến trình quản lý thợ")
    c.add_argument("--khe", action="append", required=True, help="<tên khe>=<user principal>, lặp lại mỗi khe")
    c.add_argument("--co-che", required=True, choices=("user", "sandbox"), help="Cơ chế cách ly (chốt sau S6)")
    c.add_argument("--chi-tho", action="store_true", help="Không cài lại phần kiểm")
    c.add_argument("--giu-tat", action="store_true", help="Chỉ cài file, không nạp dịch vụ")
    c.add_argument("--dong-y", action="store_true")
    c.set_defaults(ham=_cai_dat_tho)
    t = chu.add_parser("cap-token-may", help="Cấp token máy thợ, chỉ in vào ống tới `tram tho nhan-token`")
    t.add_argument("may_id")
    t.add_argument("--dong-y", action="store_true")
    t.set_defaults(ham=_cap_token_may)
    k = chu.add_parser("kiem-cach-ly", help="Kiểm chứng âm H9 dưới cach_ly.tram_kiem; khe: `tram tho kiem` (D54)")
    k.add_argument("--principal", action="append", default=[],
                   help="principal khe user:<tên> | sandbox:<tên> — chỉ in hướng dẫn sang `tram tho kiem` (D54)")
    k.set_defaults(ham=_kiem_cach_ly)
    g = chu.add_parser("go-cai-dat-tho", help="Gỡ đúng thứ cai-dat-tho đã tạo theo sổ (chờ dong-y)")
    g.add_argument("--xoa-nha", action="store_true", help="Xoá luôn thư mục nhà của user (mặc định giữ)")
    g.add_argument("--dong-y", action="store_true")
    g.set_defaults(ham=_go_cai_dat_tho)
