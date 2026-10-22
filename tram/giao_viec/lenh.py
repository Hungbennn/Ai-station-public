"""Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2),
`tram giao mo-cong-kiem` (3C-D4: Đại ca mở lại cổng kiểm lại sau khi xem lý do đóng), `tram giao nghiem-thu-kiem`
(harness S6, `lenh_nghiem_thu.py`) —
chạy ở TÀI KHOẢN TRẠM. `tick` chạy ba pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
import argparse
import sys


def _bo():
    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.giao_viec.noi_that import dung_bo_that
    cg = nap_cau_hinh_giao_viec()
    return cg, dung_bo_that(cg, nap_cau_hinh_tram())


def _tick(args) -> int:
    from tram.giao_viec.luong import KHOA_DEPLOY, KHOA_GIT, KHOA_NHANH, chay_vong
    from tram.giao_viec.tick import vong_deploy, vong_git, vong_nhanh
    cg, bo = _bo()
    if not cg.bat and not args.thu:
        print("giao_viec.bat đang tắt — chỉ chạy được `tram giao tick --thu`.")
        return 1
    pha = [("nhanh", KHOA_NHANH, lambda: vong_nhanh(bo, thu=args.thu))]
    if not args.thu:
        pha += [("git", KHOA_GIT, lambda: vong_git(bo)), ("deploy", KHOA_DEPLOY, lambda: vong_deploy(bo))]
    for ten, khoa, lam in pha:
        kq = chay_vong(khoa, lam)
        print(f"pha {ten}: " + ("đang có vòng khác chạy — bỏ qua" if kq is None else str(kq or "không có việc")))
    return 0


def _kho_kiem(args) -> int:
    from tram.cau_hinh.du_an import nap_du_an
    from tram.giao_viec.kho_kiem_tao import in_ke_hoach, lap_ke_hoach, thuc_hien
    da = nap_du_an(args.du_an)
    try:
        kh = lap_ke_hoach(da)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    print(in_ke_hoach(kh))
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    print(f"Xong: origin/{da.nhanh_chinh} = {thuc_hien(kh, da.nhanh_chinh)}")
    return 0


def _kiem(args) -> int:
    from tram.giao_viec.kiem_san_sang import kiem_giao_viec
    from tram.tho.kiem_may import in_ket_qua
    cg, bo = _bo()
    van_ban, ma = in_ket_qua(kiem_giao_viec(cg, bo.cac_du_an()))
    print(van_ban)
    return ma


def _mo_cong(args) -> int:
    from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
    _, bo = _bo()
    if bo.cong is None:
        print("Chưa khai cach_ly.tram_kiem — không có cổng kiểm lại.")
        return 2
    print(f"Trạng thái hiện tại: {bo.cong.trang_thai()}")
    if not args.dong_y and input("Gõ dong-y để thu hồi, quan sát và mở lại: ").strip() != "dong-y":
        return 1
    try:
        bo.cong.mo_lai()
    except LoiBanChep as e:
        print(f"Vẫn đóng: {e}", file=sys.stderr)
        return 1
    print("Đã mở cổng kiểm lại.")
    return 0


def them_lenh_giao(sub) -> None:
    g = sub.add_parser("giao", help="Bộ giao việc (phần 4)").add_subparsers(dest="lenh_giao", required=True)
    t = g.add_parser("tick", help="Chạy một vòng tick (pha nhanh, pha Git, rồi pha deploy)")
    t.add_argument("--thu", action="store_true", help="Chỉ ghi sự kiện suy từ beads: không ghi beads, không chạy lệnh")
    t.set_defaults(ham=_tick)
    k = g.add_parser("kho-kiem", help="Tạo/cập nhật kho kiểm của trạm từ remote dự án (liệt kê, chờ dong-y)")
    k.add_argument("du_an")
    k.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã đọc kế hoạch)")
    k.set_defaults(ham=_kho_kiem)
    g.add_parser("kiem", help="Kiểm sẵn sàng: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
    c = g.add_parser("mo-cong-kiem", help="Thu hồi + quan sát tram-kiem rồi mở lại cổng kiểm lại (chờ dong-y)")
    c.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã xem lý do đóng)")
    c.set_defaults(ham=_mo_cong)
    _them_nghiem_thu(g)


def _them_nghiem_thu(g) -> None:
    def lenh_nghiem_thu(args):
        print("D159: dùng python -m tram.quan_kiem.g4 qua bộ quản lý system; xem plan G4.")
        return 2
    h = g.add_parser("nghiem-thu-kiem", help="S6: harness kiểm lại trên kho nháp dưới principal thật (mã ≠ 0 nếu đỏ)")
    h.add_argument("--tai-sinh", action="store_true", help="Thử cài lịch cron/at/launchd như mã agent rồi chờ (G4)")
    h.add_argument("--cho", type=float, default=300.0, help="Giây chờ quá giờ hẹn của lịch (mặc định 300, ≥ 240)")
    h.add_argument("--trong", action="store_true", help=argparse.SUPPRESS)
    h.add_argument("--dau-ino", type=int, default=None, help=argparse.SUPPRESS)
    h.add_argument("--cha", type=int, default=None, help=argparse.SUPPRESS)
    h.set_defaults(ham=lenh_nghiem_thu)
