"""Lệnh `tram tho kiem|tat-khe|bat-khe` và `tram chu go-may` (spec 3 §6.2 điều kiện 1, §5.1, §9.3).
`tat-khe`/`bat-khe`/`go-may` chạy ở TÀI KHOẢN TRẠM (ghi thẳng kho sự kiện); `kiem` chạy ở tài khoản quản lý thợ."""
import sys
from contextlib import closing
from datetime import datetime, timezone


def _kiem(args) -> int:
    from tram.tho.cau_hinh import nap_cau_hinh_tho
    from tram.tho.khach import KhachTram, doc_token_may
    from tram.tho.kiem_cong import dau_do_that
    from tram.tho.kiem_may import in_ket_qua, kiem_may
    try:
        ch = nap_cau_hinh_tho()
    except ValueError as e:
        print(f"[ĐỎ] tho.yaml: {e}")
        return 1
    khach = KhachTram(ch.tram_api, doc_token_may(tren_may_b=ch.tren_may_b) or "")
    try:
        dd = dau_do_that(ch, khach, du_an=tuple(args.du_an))
        van_ban, ma = in_ket_qua(kiem_may(ch, dd))
    except (ValueError, OSError):
        print("Không xác nhận được phạm vi kiểm máy thợ.")
        return 2
    print(van_ban)
    return ma


def _bat_tat(args) -> int:
    from tram.phieu.kho import mo_kho_phieu
    from tram.phieu.khe import KheLa, bat_tat_khe
    bat = args.lenh_tho == "bat-khe"
    try:
        with closing(mo_kho_phieu()) as kho, kho.giao_dich():
            bat_tat_khe(kho, args.khe, bat=bat, vi_sao=args.vi_sao, tac_nhan="dai-ca",
                        luc=datetime.now(timezone.utc))
    except KheLa as e:
        print(e, file=sys.stderr)
        return 2
    print(f"Đã {'bật' if bat else 'tắt'} khe {args.khe}" + ("" if bat else " — phiếu đang chạy sẽ dừng mềm."))
    return 0


def _go_may(args) -> int:
    from tram.phieu.kho import mo_kho_phieu
    from tram.phieu.may import go_may
    print(f"Sẽ thu hồi token máy {args.may_id} và mọi phiếu đang hiệu lực của máy đó (thợ dừng cứng).")
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    try:
        with closing(mo_kho_phieu()) as kho:
            n = go_may(kho, args.may_id, luc=datetime.now(timezone.utc))
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    print(f"Đã gỡ máy {args.may_id}; thu hồi {n} phiếu.")
    return 0


def them_lenh_tho(sub, chu) -> None:
    tho = sub.add_parser("tho", help="Máy thợ (phần 3)").add_subparsers(dest="lenh_tho", required=True)
    k = tho.add_parser("kiem", help="Kiểm máy thợ: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ")
    k.add_argument("--du-an", action="append", default=[])
    k.set_defaults(ham=_kiem)
    from tram.tho.lenh_dang_ky import them_lenh_dang_ky
    them_lenh_dang_ky(tho)
    from tram.tho.dang_ky_b import them_lenh
    them_lenh(tho)
    for ten, mo_ta in (("tat-khe", "Tắt khe (phiếu đang chạy dừng mềm)"), ("bat-khe", "Bật lại khe")):
        x = tho.add_parser(ten, help=mo_ta)
        x.add_argument("khe", help="khe_id, vd B/claude-1")
        x.add_argument("--vi-sao", default="")
        x.set_defaults(ham=_bat_tat)
    g = chu.add_parser("go-may", help="Thu hồi token máy thợ + mọi phiếu hiệu lực của máy")
    g.add_argument("may_id")
    g.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi")
    g.set_defaults(ham=_go_may)
    from tram.chu.cap_ma import them_lenh_cap_ma
    them_lenh_cap_ma(chu)
    from tram.chu.lenh_tho import them_lenh_chu_tho
    from tram.tho.lenh_chay import them_lenh_chay
    from tram.tho.lenh_khe import them_lenh_khe
    them_lenh_chay(tho)                       # 3a-2: tram tho chay | nhan-token
    them_lenh_khe(tho)                        # 3a-2: tram tho them-khe | bot-khe
    them_lenh_chu_tho(chu)                    # 3a-2: tram chu cai-dat-tho | cap-token-may | kiem-cach-ly
