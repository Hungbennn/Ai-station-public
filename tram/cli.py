import argparse
import sys
from pathlib import Path


def _quet(args) -> int:
    from tram.beads.bd import Bd
    from tram.cau_hinh.bat_ghi import bat_ghi
    from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
    from tram.cham_cot.prompt import nap_vai
    from tram.cham_cot.quet import quet, xuat_bao_cao
    from tram.chu import estop
    from tram.llm.claude import tao_client
    from tram.nho.khach import tao_nho_lai
    from tram.su_kien.kho import mo_kho

    if estop.dang_bat():
        print("estop đang bật — không quét")
        return 0
    kho, client, vai = mo_kho(), tao_client(), nap_vai("cham-cot")
    nho = tao_nho_lai()  # None khi chưa cài memory service (chưa có tram-nho-token) — 1a dùng cách cũ
    for ten in args.du_an or liet_ke_du_an():
        du_an = nap_du_an(ten, repo=Path(args.repo) if args.repo else None)
        if args.ghi and not bat_ghi(ten):  # lát 1a-2 (D31): dự án chưa bật ghi chỉ được quét thử
            print(f"{ten}: bỏ qua --ghi — du-an/{ten}.yaml chưa khai bat_ghi: true (quét thử: chạy lại không có --ghi)")
            continue
        bc = quet(du_an, bd=Bd(du_an.duong_dan), kho=kho, client=client, vai=vai,
                  tat_ca=args.tat_ca, thu=not args.ghi, gioi_han=args.gioi_han, nho=nho)
        if bc is None:
            print(f"{ten}: bỏ qua (estop hoặc đang có lượt quét khác)")
            continue
        md = xuat_bao_cao(bc)
        if args.bao_cao:
            Path(args.bao_cao).parent.mkdir(parents=True, exist_ok=True)
            Path(args.bao_cao).write_text(md, encoding="utf-8")
        print(md if args.bao_cao is None and args.tat_ca else md.splitlines()[2])
    return 0


def _estop(args) -> int:
    from tram.chu.dieu_khien import bat_estop
    from tram.su_kien.kho import mo_kho
    bat_estop(mo_kho(), args.ly_do, tac_nhan="dai-ca")
    print("Đã bật estop: mọi lượt quét dừng cho tới khi chạy `tram chu tiep-tuc`.")
    return 0


def _tiep_tuc(args) -> int:
    from tram.chu.dieu_khien import tat_estop
    from tram.su_kien.kho import mo_kho
    tat_estop(mo_kho(), tac_nhan="dai-ca")
    print("Đã tắt estop.")
    return 0


def _trang_thai(args) -> int:
    from tram.chu.trang_thai import trang_thai
    from tram.su_kien.kho import mo_kho
    print(trang_thai(mo_kho()))
    return 0


def tao_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tram", description="ben-station — trạm điều phối")
    sub = p.add_subparsers(dest="lenh", required=True)

    q = sub.add_parser("quet", help="Chấm cột các bead đã đổi")
    q.add_argument("du_an", nargs="*", help="Tên dự án trong du-an/ (mặc định: tất cả)")
    q.add_argument("--tat-ca", action="store_true", help="Chấm mọi bead mở, bỏ qua mốc")
    q.add_argument("--ghi", action="store_true", help="Ghi thật vào beads (mặc định: chế độ thử)")
    q.add_argument("--repo", help="Ghi đè đường dẫn repo dự án")
    q.add_argument("--gioi-han", type=int, help="Chấm tối đa N bead")
    q.add_argument("--bao-cao", help="Ghi báo cáo markdown ra file")
    q.set_defaults(ham=_quet)

    chu = sub.add_parser("chu", help="Lệnh trạm chủ").add_subparsers(dest="lenh_chu", required=True)
    from tram.chu.passkey import them_lenh as them_passkey
    them_passkey(chu)
    e = chu.add_parser("estop", help="Dừng khẩn cấp mọi lượt quét")
    e.add_argument("--ly-do", default="Đại ca bấm estop")
    e.set_defaults(ham=_estop)
    chu.add_parser("tiep-tuc", help="Tắt estop").set_defaults(ham=_tiep_tuc)
    from tram.chu.lenh_cai_dat import them_lenh_cai_dat           # bs-2bd.1.23: cài từng dịch vụ
    them_lenh_cai_dat(chu)
    chu.add_parser("trang-thai", help="Dịch vụ, lần quét cuối, lỗi gần nhất").set_defaults(ham=_trang_thai)
    from tram.cli_dich_vu import them_lenh
    them_lenh(sub, chu)
    from tram.cli_danh_gia import them_lenh as them_danh_gia
    them_danh_gia(sub)

    from tram.cli_du_an import them_lenh as them_du_an
    them_du_an(sub)
    return p


def main(argv: list[str] | None = None) -> int:
    from tram.tho.bao_lenh import chan_ngoai_bao
    if (ma := chan_ngoai_bao(sys.argv[1:] if argv is None else argv)) is not None:
        return ma
    args = tao_parser().parse_args(argv)
    return args.ham(args)


if __name__ == "__main__":
    sys.exit(main())
