"""Lệnh `tram bao …` và luật "trong phiếu chỉ chạy `tram bao`" (spec 3 §7.3 mục 3 — lớp bổ sung, không phải
hàng rào)."""
import os
import subprocess
import sys
from pathlib import Path

from tram.ban_giao.cau_truc import LoiCauTruc
from tram.de_nghi.loc import LOAI_VIEC
from tram.tho.bao import LOAI_HOI, LoiBao, _git, bao


def chan_ngoai_bao(argv: list[str]) -> int | None:
    """Có `TRAM_GIAO_ID` (môi trường CLI của phiếu) → mọi lệnh con khác `bao` bị từ chối (mã 2)."""
    if os.environ.get("TRAM_GIAO_ID") and (not argv or argv[0] != "bao"):
        print("Trong phiếu chỉ được chạy `tram bao …`.", file=sys.stderr)
        return 2
    return None


def _bao(args) -> int:
    hang_doi = os.environ.get("TRAM_HANG_DOI")
    if not os.environ.get("TRAM_GIAO_ID") or not hang_doi:
        print("`tram bao` chỉ chạy trong phiếu (thiếu TRAM_GIAO_ID / TRAM_HANG_DOI).", file=sys.stderr)
        return 2
    try:
        wt = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel"))
        vm = None if args.loai != "viec_moi" else {"tieu_de": args.tieu_de, "mo_ta": args.mo_ta,
                                                   "loai_viec": args.loai_phu,
                                                   **({"tieu_chi": args.tieu_chi} if args.tieu_chi else {})}
        bao(args.loai, args.noi_dung, wt=wt, hang_doi=Path(hang_doi), ban_giao=args.ban_giao,
            loai_hoi=args.loai_phu if vm is None else None, viec_moi=vm)
    except (LoiBao, LoiCauTruc, subprocess.CalledProcessError, OSError) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    print(f"Đã ghi báo {args.loai}.")
    return 0


def them_lenh_bao(sub) -> None:
    b = sub.add_parser("bao", help="Agent báo trạng thái phiếu (chỉ trong phiếu — cần TRAM_GIAO_ID)")
    g = b.add_mutually_exclusive_group(required=True)
    for co, loai in (("--moc", "moc"), ("--can-hoi", "can_hoi"), ("--bi", "bi"), ("--xong", "xong"),
                     ("--tien-do", "tien_do"), ("--viec-moi", "viec_moi")):
        g.add_argument(co, dest="loai", action="store_const", const=loai)
    b.add_argument("--loai", dest="loai_phu", choices=(*LOAI_HOI, *LOAI_VIEC),
                   help="Loại câu hỏi (với --can-hoi) hoặc loại việc bug|task|chore (với --viec-moi)")
    b.add_argument("--tieu-de", help="Tiêu đề việc mới (với --viec-moi; một dòng, ≤ 200 ký tự)")
    b.add_argument("--mo-ta", help="Mô tả việc mới (với --viec-moi; ≤ 4.000 ký tự)")
    b.add_argument("--tieu-chi", help="Tiêu chí nghiệm thu việc mới (tuỳ chọn; ≤ 2.000 ký tự)")
    b.add_argument("--ban-giao", help="File bàn giao chứa khối <!-- ban-giao -->")
    b.add_argument("noi_dung", nargs="?", default="", help="Nội dung / câu hỏi / lý do")
    b.set_defaults(ham=_bao)
