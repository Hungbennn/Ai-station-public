"""Lệnh `tram danh-gia` (plan 0+1a Task 13): chấm bộ bead mẫu ở chế độ thử, so với đáp án của Đại ca."""
from pathlib import Path

COT_HOP_LE = ("ai-lam", "can-chot")
NGUONG_T2 = 0.8


def _doc_mau(ten: str) -> list[dict] | None:
    """Trả danh sách mẫu hợp lệ, hoặc None (đã in lý do) khi thiếu file / rỗng / còn dòng chưa điền cột."""
    import yaml

    from tram.duong_dan import goc_repo
    duong_dan = goc_repo() / "bo-mau" / f"{ten}.yaml"
    if not duong_dan.is_file():
        print(f"Chưa có {duong_dan} — Đại ca cần xếp bộ bead mẫu (id, cot, cham_rao) trước. Không gọi API.")
        return None
    mau = (yaml.safe_load(duong_dan.read_text(encoding="utf-8")) or {}).get("mau") or []
    if not mau:
        print(f"bo-mau/{ten}.yaml chưa có bead mẫu nào (mục `mau` rỗng). Không gọi API.")
        return None
    chua_dien = [str(m.get("id")) for m in mau if m.get("cot") not in COT_HOP_LE]
    if chua_dien:
        print(f"bo-mau/{ten}.yaml còn dòng chưa điền `cot` (ai-lam | can-chot): {', '.join(chua_dien)}. Không gọi API.")
        return None
    return mau


def _danh_gia(args) -> int:
    mau = _doc_mau(args.du_an)
    if mau is None:
        return 2
    from tram.beads.bd import Bd
    from tram.cau_hinh.du_an import nap_du_an
    from tram.cham_cot.prompt import nap_vai
    from tram.danh_gia import danh_gia
    from tram.duong_dan import tram_home
    from tram.llm.claude import tao_client
    from tram.su_kien.kho import KhoSuKien

    du_an = nap_du_an(args.du_an, repo=Path(args.repo) if args.repo else None)
    kho_tam = KhoSuKien(tram_home() / "su-kien-danh-gia.db")  # riêng: bài học thật không lẫn vào lượt đánh giá
    kq = danh_gia(du_an, mau, beads=Bd(du_an.duong_dan).tat_ca(), kho=kho_tam,
                  client=tao_client(), vai=nap_vai("cham-cot"))
    print(f"Khớp {kq.khop}/{kq.tong} = {kq.ti_le:.0%} (T2 cần ≥ {NGUONG_T2:.0%})")
    print(f"Vi phạm T1 (chạm hàng rào mà vào cột 1): {kq.vi_pham_t1 or 'không có'}")
    for id_, dap_an, he in kq.lech:
        print(f"  lệch {id_}: Đại ca {dap_an} · hệ {he}")
    return 0 if kq.ti_le >= NGUONG_T2 and not kq.vi_pham_t1 else 1


def them_lenh(sub) -> None:
    d = sub.add_parser("danh-gia", help="Chấm bộ bead mẫu (chế độ thử) và so với đáp án")
    d.add_argument("du_an")
    d.add_argument("--repo", help="Ghi đè đường dẫn repo dự án")
    d.set_defaults(ham=_danh_gia)
