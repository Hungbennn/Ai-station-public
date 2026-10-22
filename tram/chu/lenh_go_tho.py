"""`tram chu go-cai-dat-tho` — phần dòng lệnh (tách khỏi `go_cai_dat_tho.py` — bs-2bd.1.20, chỉ dời chỗ)."""
import subprocess
from collections.abc import Callable

from tram.chu.go_cai_dat_tho import lap_ke_hoach_go
from tram.chu.so_cai_tho import SoCai


def lenh_cli(args, *, hoi: Callable) -> int:
    """`tram chu go-cai-dat-tho`: 0 không còn gì / đã chạy; 1 không dong-y / dừng giữa chừng; 2 sổ hỏng / đang bận."""
    import getpass
    import sys

    from tram.chu.cai_dat import in_ke_hoach, thuc_hien
    so = SoCai()
    try:
        with so.giu():                         # R4: gỡ và cài không chạy đồng thời (khoá TRƯỚC khi xem sổ)
            kh = lap_ke_hoach_go(so, toi=getpass.getuser(), xoa_nha=args.xoa_nha) if so.p.exists() else None
            if kh is None or not kh.buoc:
                print("Không còn gì để gỡ." if kh else f"Không còn gì để gỡ (chưa có sổ {so.p}).")
                return 0
            print(in_ke_hoach(kh))
            if not hoi(args):
                print("Không làm gì.")
                return 1
            try:
                thuc_hien(kh)
            except (OSError, ValueError, subprocess.CalledProcessError) as e:
                print(f"Dừng giữa chừng: {e}\nChạy lại `tram chu go-cai-dat-tho` sau khi xem lỗi.", file=sys.stderr)
                return 1
    except (ValueError, OSError) as e:         # sổ hỏng, SoCaiDangBan, dscl lỗi lúc lập kế hoạch
        print(f"Không gỡ gì: {e}", file=sys.stderr)
        return 2
    print("Đã chạy kế hoạch gỡ. Chạy lại `tram chu go-cai-dat-tho`: phải báo không còn gì để gỡ.")
    return 0
