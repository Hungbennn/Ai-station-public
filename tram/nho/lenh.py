"""Lệnh `tram nho …` (spec 1b §9, §15, §16). Mọi lệnh đọc/ghi ký ức đi qua memory service (một tiến trình ghi)."""
import json
import sys

from tram.nho.lenh_kho import them_lenh_kho
from tram.nho.lenh_xoa import them_lenh_xoa


def _chay(args) -> int:
    from tram.nho.tien_trinh import chay_dich_vu
    return chay_dich_vu(cong=args.cong)


def _token():
    from tram.nho.khach import doc_token
    token = doc_token()
    if token is None:
        print("Chưa có tram-nho-token trong Keychain — memory service chưa cài.", file=sys.stderr)
    return token


def _vung_cap(args) -> list[str] | None:
    """--vung-cap: danh sách JSON gửi THÔ (service tự kiểm — dùng kiểm M1/M2 không cần curl/token)."""
    from tram.nho.pham_vi import goc_du_an
    if args.vung_cap is None:
        return [goc_du_an(args.du_an), f"/vai/{args.vai}", "/chung"]
    try:
        return json.loads(args.vung_cap)
    except ValueError:
        print("Lỗi: --vung-cap phải là JSON, ví dụ '[\"/du-an/hr-codex\", \"/chung\"]'", file=sys.stderr)
        return None


def _tim(args) -> int:
    from tram.nho.khach import LoiNhoKhach, nho_lai_http
    if (vung_cap := _vung_cap(args)) is None or (token := _token()) is None:
        return 1
    try:
        ds = nho_lai_http(args.truy_van, vung_cap, token=token, thoi_gian_cho=30.0)
    except LoiNhoKhach as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    for k in ds:
        print(f"- [{k['pham_vi']}] {k['noi_dung']}  ({k['id']})")
    print(f"{len(ds)} ký ức.")
    return 0


def _xoa(args) -> int:
    from tram.nho.khach import LoiNhoKhach, goi_nho
    if (token := _token()) is None:
        return 1
    try:
        kq = goi_nho("/xoa", {"id": args.id}, token=token, thoi_gian_cho=30.0)
    except LoiNhoKhach as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    print("Đã xoá mềm." if kq.get("da_xoa") else "Ký ức đã bị xoá từ trước.")
    return 0


def _thu(args) -> int:
    from tram.cham_cot.prompt import nap_vai
    from tram.llm.claude import tao_client
    from tram.nho.luat import luat_cua_du_an
    from tram.nho.thu import chay_thu
    from tram.su_kien.kho import mo_kho
    print(chay_thu(mo_kho(), tao_client(), nap_vai("nho-tach"), luat_cua_du_an, du_an=args.du_an,
                   tu_id=args.tu_id, gioi_han=args.gioi_han))
    return 0


def them_lenh_nho(sub) -> None:
    nho = sub.add_parser("nho", help="Memory chung nhiều dự án (lát 1b-1)").add_subparsers(dest="lenh_nho",
                                                                                          required=True)
    c = nho.add_parser("chay", help="Chạy memory service (chỉ nghe 127.0.0.1)")
    c.add_argument("--cong", type=int, default=7710)
    c.set_defaults(ham=_chay)
    t = nho.add_parser("tim", help="Recall thử qua memory service")
    t.add_argument("truy_van")
    nguon = t.add_mutually_exclusive_group(required=True)
    nguon.add_argument("--du-an")
    nguon.add_argument("--vung-cap", help='JSON thô, bỏ qua --du-an/--vai, ví dụ \'["/"]\'')
    t.add_argument("--vai", default="dieu-phoi")
    t.set_defaults(ham=_tim)
    x = nho.add_parser("xoa", help="Xoá mềm một ký ức theo id")
    x.add_argument("id")
    x.set_defaults(ham=_xoa)
    th = nho.add_parser("thu", help="Tách thử từ lịch sử sự kiện — không ghi (gọi Claude API)")
    th.add_argument("--du-an")
    th.add_argument("--tu-id", type=int, default=0)
    th.add_argument("--gioi-han", type=int, default=20)
    th.set_defaults(ham=_thu)
    them_lenh_kho(nho)
    them_lenh_xoa(nho)
