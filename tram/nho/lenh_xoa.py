"""Lệnh xoá riêng của Đại ca (spec 1b §5, §11): `tram nho xoa-pham-vi` (xoá mềm qua dịch vụ) và `tram nho xoa-cung`
(xoá hẳn, dịch vụ phải dừng). Phạm vi luôn khớp chính xác một trong bốn dạng; liệt kê trước, chờ `dong-y`."""
import sys

SO_VONG_TOI_DA = 50
LO = 1000


def _hoi(args, cau: str) -> bool:
    print(cau)
    if args.dong_y or input("Gõ dong-y để thực hiện: ").strip() == "dong-y":
        return True
    print("Không làm gì.")
    return False


def xoa_pham_vi(pham_vi: str, goi, hoi) -> int:
    """Xoá mềm mọi ký ức chưa xoá của đúng phạm vi `pham_vi` qua `/danh-sach` + `/xoa` (mỗi ký ức một `nho.xoa`)."""
    ds = goi("/danh-sach", {"pham_vi": pham_vi, "gioi_han": LO})
    if not ds["tong"]:
        print(f"Không có ký ức nào (chưa xoá) ở {pham_vi}.")
        return 0
    if not hoi(f"Sẽ xoá mềm {ds['tong']} ký ức ở {pham_vi} (khớp chính xác, không đụng phạm vi khác)."):
        return 0
    da = 0
    for _ in range(SO_VONG_TOI_DA):
        if not ds["ky_uc"]:
            break
        for k in ds["ky_uc"]:
            da += bool(goi("/xoa", {"id": k["id"]}).get("da_xoa"))
        ds = goi("/danh-sach", {"pham_vi": pham_vi, "gioi_han": LO})
    print(f"Đã xoá mềm {da} ký ức ở {pham_vi}.")
    return da


def _xoa_pham_vi(args) -> int:
    from tram.nho.khach import LoiNhoKhach, doc_token, goi_nho
    from tram.nho.pham_vi import la_pham_vi
    if not la_pham_vi(args.pham_vi):
        print("Lỗi: phạm vi phải đầy đủ, ví dụ /du-an/hr-codex/cach-lam, /vai/coder, /chung", file=sys.stderr)
        return 1
    if (token := doc_token()) is None:
        print("Chưa có tram-nho-token trong Keychain — memory service chưa cài.", file=sys.stderr)
        return 1
    try:
        xoa_pham_vi(args.pham_vi, lambda d, t: goi_nho(d, t, token=token, thoi_gian_cho=30.0),
                    lambda cau: _hoi(args, cau))
    except LoiNhoKhach as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    return 0


def _xoa_cung(args) -> int:
    from tram.nho.khoa import thu_muc_nho
    from tram.nho.pham_vi import LoiVungCap
    from tram.nho.xoa_cung import ConThaoTacDo, DichVuDangChay, xoa_cung
    from tram.su_kien.kho import mo_kho
    kw = {"id": args.id, "pham_vi": args.pham_vi}
    try:
        xem = xoa_cung(thu_muc_nho(), mo_kho(), **kw)
        if not xem.hang:
            print("Không có ký ức đã xoá mềm nào khớp — xoá mềm trước (dashboard hoặc tram nho xoa).")
            return 0
        for h in xem.hang:
            print(f"- {h['id']}  [{h['pham_vi']}]")
        if not _hoi(args, f"Sẽ xoá HẲN {len(xem.hang)} ký ức trên (không khôi phục được; bản sao lưu cũ còn tới khi "
                          "xoay vòng 14 ngày)."):
            return 1
        print(f"Đã xoá cứng {len(xoa_cung(thu_muc_nho(), mo_kho(), that=True, **kw).hang)} ký ức.")
    except (DichVuDangChay, ConThaoTacDo, LoiVungCap) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    return 0


def them_lenh_xoa(nho) -> None:
    p = nho.add_parser("xoa-pham-vi", help="Xoá mềm mọi ký ức của ĐÚNG một phạm vi (qua memory service)")
    p.add_argument("pham_vi")
    p.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi")
    p.set_defaults(ham=_xoa_pham_vi)
    c = nho.add_parser("xoa-cung", help="Xoá HẲN ký ức đã xoá mềm (dịch vụ phải dừng)")
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("--id")
    g.add_argument("--pham-vi")
    c.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi")
    c.set_defaults(ham=_xoa_cung)
