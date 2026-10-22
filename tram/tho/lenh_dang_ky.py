"""Lệnh `tram tho dang-ky` (spec 3 §9.2; kiến trúc §7 "Mac thợ") — chạy ở TÀI KHOẢN QUẢN LÝ THỢ của Mac thợ từ xa:
dò, in danh sách thay đổi, chờ gõ `dong-y` (Q15), rồi mới làm."""
import subprocess
import sys
from pathlib import Path


def _dang_ky(args) -> int:
    from tram.tho import ke_hoach_dk, thuc_hien_dk
    from tram.tho.khach import LoiKhachTram
    from tram.tho.khai_khe import doc_khe
    try:
        khe = [doc_khe(s) for s in args.khe]
        kh = ke_hoach_dk.lap_ke_hoach_dk(args.tram_chu, khe, thu_muc_khe=Path(args.thu_muc_khe),
                                         nho=not args.khong_nho, dd=ke_hoach_dk.DauDoDK())
    except ValueError as e:
        print(f"Không đăng ký: {e}", file=sys.stderr)
        return 2
    print(ke_hoach_dk.in_ke_hoach_dk(kh))
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    try:
        import getpass
        ma = getpass.getpass("Mã ghép (ẩn): ").strip()
        may_id = thuc_hien_dk.thuc_hien_dk(kh, ma, thuc_hien_dk.hieu_ung_that())
    except (LoiKhachTram, ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as e:
        print(f"Dừng giữa chừng: {e}. Xin mã ghép mới (`tram chu cap-ma`; nếu máy đã nhận token thì "
              "`tram chu go-may <máy>` trước) rồi chạy lại.", file=sys.stderr)
        return 2
    print(f"Đã đăng ký máy {may_id}. Kiểm: tram tho kiem")
    return 0


def them_lenh_dang_ky(tho) -> None:
    d = tho.add_parser("dang-ky", help="Ghép Mac thợ từ xa với trạm chủ (liệt kê thay đổi, chờ dong-y)")
    d.add_argument("--tram-chu", required=True, help="https://<máy B>.<tailnet>.ts.net")
    d.add_argument("--khe", action="append", required=True, help="<ten>:<cli>:<vai,…>:<tên gợi nhớ> — lặp được")
    d.add_argument("--thu-muc-khe", default="~/tram/khe", help="Thư mục cha của CLAUDE_CONFIG_DIR/CODEX_HOME các khe")
    d.add_argument("--khong-nho", action="store_true", help="Không ghi cấu hình memory MCP")
    d.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi")
    d.set_defaults(ham=_dang_ky)
