"""Lệnh `tram du-an them|go` (spec 0+1a §4.7) — tách khỏi cli.py cho gọn (lát 1a-2)."""
from pathlib import Path


def _du_an(args) -> int:
    from tram.du_an.lenh import chay
    them = args.lenh_du_an == "them"
    return chay(Path(args.repo), them=them, dong_y=args.dong_y, ten=getattr(args, "ten", None),
                gitnexus=getattr(args, "gitnexus", None), ghi_de=getattr(args, "ghi_de_cau_hinh", False))


def them_lenh(sub) -> None:
    da = sub.add_parser("du-an", help="Đưa dự án vào / gỡ khỏi trạm").add_subparsers(dest="lenh_du_an", required=True)
    t = da.add_parser("them", help="Tạo du-an/<ten>.yaml, chèn khối trạm, in bước trỏ beads (chờ đồng ý)")
    t.add_argument("--ten", help="Tên dự án (mặc định: tên thư mục repo, bỏ dấu, chữ thường)")
    t.add_argument("--gitnexus", help="Tên repo trong gitnexus (gitnexus_repo)")
    t.add_argument("--ghi-de-cau-hinh", action="store_true", help="Thay du-an/<ten>.yaml đã có bằng bản nháp mới")
    g = da.add_parser("go", help="Gỡ khối trạm (giữ du-an/<ten>.yaml)")
    for x in (t, g):
        x.add_argument("repo")
        x.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ dùng khi Đại ca đã đọc kế hoạch)")
        x.set_defaults(ham=_du_an)
