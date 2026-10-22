"""`tram tho them-khe` / `bot-khe` (spec 3 §9.1): sửa `~/.tram/tho.yaml` rồi `POST /api/tho/dang-ky {may_id, khe[]}`.
Liệt kê trước, chờ `dong-y` (Q15). Ghi lại file bằng YAML chuẩn (chú thích tay bị mất — in rõ trong kế hoạch). Tạo
principal + thư mục cấu hình + đăng nhập CLI là việc của Đại ca (`tram chu cai-dat-tho`, S2, S6) — chỉ in nhắc."""
import sys
import tempfile
from pathlib import Path

import yaml

from tram.duong_dan import tram_home
from tram.tho.cau_hinh import nap_cau_hinh_tho


def sua_khe(p: Path, *, them: dict | None = None, bot: str | None = None) -> str:
    """Trả nội dung `tho.yaml` mới đã kiểm bằng chính `nap_cau_hinh_tho` (sai → ValueError, không ghi gì)."""
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    khe = [k for k in (raw.get("khe") or []) if k.get("ten") != bot and k.get("ten") != (them or {}).get("ten")]
    if bot is not None and len(khe) == len(raw.get("khe") or []):
        raise ValueError(f"Không có khe {bot}")
    raw["khe"] = khe + ([them] if them else [])
    moi = yaml.safe_dump(raw, allow_unicode=True, sort_keys=False)
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "tho.yaml").write_text(moi, encoding="utf-8")
        nap_cau_hinh_tho(Path(d) / "tho.yaml")
    return moi


def _ap_dung(args, moi: str, ke_hoach: list[str]) -> int:
    from tram.tho.khach import KhachTram, doc_token_may
    print("\n".join(ke_hoach))
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    p = tram_home() / "tho.yaml"
    p.write_text(moi, encoding="utf-8")
    ch = nap_cau_hinh_tho(p)
    ma, kq = KhachTram(ch.tram_api, doc_token_may(tren_may_b=ch.tren_may_b) or "").goi(
        "POST", "/api/tho/dang-ky",
        {"may_id": ch.may_id, "khe": [{"ten": k.ten, "cli": k.cli, "ten_goi_nho": k.ten_goi_nho,
                                       "vai_uu_tien": list(k.vai_uu_tien)} for k in ch.khe]})
    print(f"Đã ghi {p}; đăng ký với trạm: {ma}")
    return 0 if ma == 200 else 2


def _them_khe(args) -> int:
    k = {"ten": args.ten, "cli": "claude", "principal": args.principal, "thu_muc_cau_hinh": args.thu_muc_cau_hinh,
         "ten_goi_nho": args.ten_goi_nho, "vai_uu_tien": args.vai}
    try:
        moi = sua_khe(tram_home() / "tho.yaml", them=k)
    except (ValueError, OSError) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    return _ap_dung(args, moi, [f"Sẽ ghi lại ~/.tram/tho.yaml (mất chú thích tay) với khe {args.ten}: {k}",
                                "Sẽ gửi POST /api/tho/dang-ky với toàn bộ danh sách khe.",
                                f"Đại ca tự: tạo principal {args.principal} (tram chu cai-dat-tho), thư mục cấu hình "
                                "thuộc principal, đăng nhập CLI dưới principal đó (S2)."])


def _bot_khe(args) -> int:
    try:
        moi = sua_khe(tram_home() / "tho.yaml", bot=args.ten)
    except (ValueError, OSError) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    return _ap_dung(args, moi, [f"Sẽ ghi lại ~/.tram/tho.yaml (mất chú thích tay), bỏ khe {args.ten}.",
                                "Trạm vẫn giữ khe đã đăng ký: Đại ca chạy `tram tho tat-khe <máy>/<khe>` ở tài khoản "
                                "trạm để trạm ngừng giao việc cho khe này."])


def them_lenh_khe(tho) -> None:
    t = tho.add_parser("them-khe", help="Thêm/sửa một khe trong tho.yaml rồi đăng ký với trạm (chờ dong-y)")
    t.add_argument("ten")
    t.add_argument("--principal", required=True, help="user:<tên> | sandbox:<tên> (chốt sau S6)")
    t.add_argument("--thu-muc-cau-hinh", required=True, help="CLAUDE_CONFIG_DIR của khe (tuyệt đối)")
    t.add_argument("--ten-goi-nho", required=True)
    t.add_argument("--vai", nargs="+", required=True, choices=("spec", "coder", "qc"))
    t.add_argument("--dong-y", action="store_true")
    t.set_defaults(ham=_them_khe)
    b = tho.add_parser("bot-khe", help="Bỏ một khe khỏi tho.yaml (chờ dong-y)")
    b.add_argument("ten")
    b.add_argument("--dong-y", action="store_true")
    b.set_defaults(ham=_bot_khe)
