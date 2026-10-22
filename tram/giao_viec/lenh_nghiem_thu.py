"""`tram giao nghiem-thu-kiem [--tai-sinh] [--cho GIÂY]` (lát 3c S6 — thay r47 T12; hợp đồng P1 H5). Trước mọi thứ:
`xac_minh_uid` của principal — sai UID, UID người vận hành/root, thiếu cấu hình, `--cho` không hữu hạn → mã 2, không
spawn gì. CLI cha KHÔNG chạy harness trong luồng: chạy lại chính CLI bằng `python -I` (không nạp mã từ thư mục hiện
tại) với `--trong --dau-ino <inode dấu> --cha <pid cha>` làm TIẾN TRÌNH CON qua `chay_han_tong` — hạn tổng `cho +
900`, quá hạn thu hồi cả cây (kill gộp principal + cục bộ). Con chỉ chạy khi cha của nó đúng là pid đó VÀ dấu
`~/.tram/kiem-lai.dong` còn, đúng inode cha vừa tạo (gọi `--trong` tay, dấu cũ → mã 2). Cổng và quan sát của harness
là cổng THẬT với mọi dự án thật (`env_kin` đủ). Sau đó `_don` dưới khoá kiểm lại: thu hồi theo UID + HAI lượt mọi quan
sát cách `cho` của cổng (kể cả launchd — thiếu G3.9 thì ném); lỗi hay ngắt → `cong.dong` rồi ném. Chỉ khi xác nhận
mới xoá dấu; còn dấu thì kiểm lại, `tram giao kiem`, `mo-cong-kiem` từ chối. Ctrl-C/SIGTERM ở cha (bs-863.19, B03):
`term_thanh_ngat` cài TỪ ĐẦU lệnh cha — phủ preflight (tiến trình dò UID, bọc `hoan()`: ngắt chờ nó thu hồi xong) lẫn
tạo dấu + spawn harness (`chay_han_tong` tự hoãn tới khi con có chủ) — rồi thu hồi + dọn trong `finally` mới trả. Con
`--trong` giữ tín hiệu mặc định (cha thu hồi cả cây). Mã: 0 không đỏ, 1 đỏ/quá hạn/chưa dọn, 2 không chạy, 130
Ctrl-C, 143 SIGTERM (dấu còn hay đã xoá in ra stderr)."""
import math
import os
import sys
from functools import partial

from tram.duong_dan import tram_home

CHAY_CON = "import sys; from tram.cli import main; sys.exit(main(sys.argv[1:]))"


def _pk_goc():
    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
    cg = nap_cau_hinh_giao_viec()
    if cg.principal_kiem is None or cg.thu_muc_kiem is None:
        raise ValueError("cần cach_ly.tram_kiem và giao_viec.thu_muc_kiem trong ~/.tram/cau-hinh.yaml")
    return cg.principal_kiem, cg.thu_muc_kiem


def _don(pk, goc) -> bool:
    from tram.giao_viec import cong_that
    from tram.giao_viec.ban_chep import giu_khoa
    from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
    c = cong_that.dung_cong(pk, goc, cac_du_an=cac_du_an_quan_sat)
    with giu_khoa():
        try:
            c.thu_hoi()
            for i in range(2):
                if i:
                    c.ngu(c.cho)                     # tái sinh trễ phải lộ ra giữa hai lượt quan sát
                for q in c.quan_sat:
                    q()
        except BaseException as e:                   # noqa: BLE001 — dọn không xác nhận (kể cả ngắt): cổng đóng
            c.dong(f"nghiệm thu S6: dọn không xác nhận ({type(e).__name__})")
            raise
    return True


def _trong(args, pk, goc) -> int:
    from tram.giao_viec.cong_that import dung_cong, thu_hoi_theo_uid
    from tram.giao_viec.nghiem_thu_kiem import nghiem_thu
    from tram.giao_viec.du_an_quan_sat import cac_du_an_quan_sat
    from tram.tho.kiem_may import in_ket_qua
    dau = tram_home() / "kiem-lai.dong"
    if os.getppid() != args.cha or args.dau_ino is None or not dau.exists() or dau.stat().st_ino != args.dau_ino:
        print("Không chạy: --trong chỉ dành cho tiến trình con của CLI cha đang giữ dấu kiem-lai.dong", file=sys.stderr)
        return 2
    cong = dung_cong(pk, goc, cac_du_an=cac_du_an_quan_sat)
    van_ban, ma = in_ket_qua(nghiem_thu(pk, goc, cong=cong, boc_luot=pk.boc_luot,
                                        thu_hoi=partial(thu_hoi_theo_uid, pk), tai_sinh=args.tai_sinh, cho=args.cho))
    print(van_ban)
    return ma


def _trang_thai(dau) -> str:
    return ("dấu kiem-lai.dong CÒN — xem ~/.tram/log/nghiem-thu, `tram giao mo-cong-kiem` hiện trạng thái"
            if dau.exists() else "đã thu hồi + dọn (hoặc chưa chạy harness), dấu đã xoá")


def lenh_nghiem_thu(args, *, han_tong=None, xac_minh=None) -> int:
    from tram.kiem.ngat import NgatTerm, term_thanh_ngat
    if args.trong:                          # con: tín hiệu mặc định — cha thu hồi cả cây của nó
        return _chay(args, han_tong, xac_minh)
    try:
        with term_thanh_ngat():             # B03: phủ preflight có spawn lẫn tạo dấu + spawn harness
            return _chay(args, han_tong, xac_minh)
    except KeyboardInterrupt as e:          # NgatTerm là KeyboardInterrupt
        ngat, ma = ("SIGTERM", 143) if isinstance(e, NgatTerm) else ("Ctrl-C", 130)
        print(f"[ĐỎ] bị ngắt ({ngat}) — {_trang_thai(tram_home() / 'kiem-lai.dong')}", file=sys.stderr)
        return ma


def _chay(args, han_tong, xac_minh) -> int:
    from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
    from tram.kiem.han_tong import chay_han_tong, gop_kill
    from tram.kiem.ngat import hoan
    from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo
    dau = tram_home() / "kiem-lai.dong"
    try:
        with hoan():                        # tiến trình dò UID (hữu hạn): ngắt tới lúc này chờ nó thu hồi xong
            pk, goc = _pk_goc()
            if not (math.isfinite(args.cho) and args.cho > 0) or (args.tai_sinh and args.cho < 240):
                raise ValueError("--cho phải hữu hạn, > 0, và ≥ 240 giây với --tai-sinh (lịch hẹn 121–180 s)")
            (xac_minh or xac_minh_uid)(pk.ten, pk.boc_lenh, pk.kill_nhom)
    except (ValueError, LoiDanhTinh, LoiThuHoi) as e:
        print(f"Không chạy nghiệm thu: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if args.trong:
        return _trong(args, pk, goc)
    argv = [sys.executable, "-I", "-c", CHAY_CON, "giao", "nghiem-thu-kiem", "--trong", "--cho", str(args.cho),
            *(["--tai-sinh"] if args.tai_sinh else [])]
    try:
        return (han_tong or chay_han_tong)(argv, han=args.cho + 900, kill=gop_kill(pk.kill_nhom, kill_cuc_bo), dau=dau,
                                           don=partial(_don, pk, goc), khoi=lambda a, **kw: khoi_chay(
                                               [*a, "--dau-ino", str(dau.stat().st_ino), "--cha", str(os.getpid())],
                                               **kw))
    except LoiThuHoi as e:                  # HetHanTong là LoiThuHoi
        print(f"[ĐỎ] {e} — {_trang_thai(dau)}", file=sys.stderr)
        return 1


def them(g) -> None:
    """Giữ đường gọi cũ; phần khai tham số thuộc module lenh."""
    from tram.giao_viec.lenh import _them_nghiem_thu
    _them_nghiem_thu(g)
