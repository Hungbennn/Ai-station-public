"""Mục `tram tho kiem` của lát 3b (spec 3 §9.2, §9.3, H7) — nối vào cuối `kiem_may` (3a-1):

- Khe Codex: xác minh UID thực của principal MỘT lần, rồi cả đăng nhập (`codex login status`, bs-863.17) lẫn hạn mức
  (`codex app-server`, bs-78r.10) đều chạy DƯỚI PRINCIPAL ĐÓ. Chưa có principal / UID chưa chứng minh → đăng nhập ĐỎ
  (không dò dưới quản lý, không spawn), hạn mức VÀNG (#15); không xác nhận thu hồi tiến trình (dò UID, đăng nhập hay
  app-server) → ĐỎ và KHÔNG spawn gì thêm dưới principal đó (review vòng 1 A05).
- Máy từ xa (`tram_api` là https): Mac thợ phải gắn tag Tailscale (#3) — chỉ kiểm, không đổi.
Mục cách ly, quyền ghi worktree của principal giữ nguyên như 3a-1/3a-2 (S6)."""
from datetime import datetime, timezone
from pathlib import Path

from tram.chay_cli.codex.app_server import doc_han_muc_ranh
from tram.duong_dan import tram_home
from tram.kiem import danh_tinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.do_may import dang_nhap_codex, do_cli, kiem_tag
from tram.tho.kiem_may import DauDo, MucKiem
from tram.tho.principal_khe import principal_cua


def _principal(ch: CauHinhTho, k: KheCauHinh):
    try:
        pr = principal_cua(ch, k, goc=tram_home(), goc_wt=Path.home() / "tram" / "worktrees", wt=None,
                           ten="han-muc-kiem")
        danh_tinh.xac_minh_uid(pr.user, pr.boc, pr.kill_nhom)
        return pr
    except (ValueError, OSError, danh_tinh.LoiDanhTinh):  # ChuaCoPrincipal là ValueError; LoiThuHoi để nổi lên
        return None


def _han_muc(kid: str, hm, loi: bool) -> MucKiem:
    if loi:
        return MucKiem(f"{kid} hạn mức", "do", "không xác nhận thu hồi tiến trình đọc hạn mức — kiểm principal")
    if hm:
        return MucKiem(f"{kid} hạn mức", "xanh", ", ".join(f"{c.loai} {c.phan_tram:g}%" for c in hm.cua_so))
    return MucKiem(f"{kid} hạn mức", "vang", "chưa đọc được qua `codex app-server` dưới principal của khe (chờ S5/S6) "
                   "— vẫn nhận việc, cảnh báo vàng (#15)")


def bo_sung_3b(ch: CauHinhTho, dd: DauDo, ra: list[MucKiem], *, doc_han_muc=doc_han_muc_ranh,
               bay_gio: datetime | None = None, principal_cua_=_principal, dang_nhap_=dang_nhap_codex) -> list[MucKiem]:
    ra = list(ra)
    for k in (k for k in ch.khe if k.cli == "codex"):
        kid = ch.khe_id(k)
        d = do_cli("codex", k.thu_muc_cau_hinh, which=dd.which, chay=dd.chay)
        hm, loi = None, False
        try:
            pr = principal_cua_(ch, k)
        except LoiThuHoi:
            pr, loi = None, True
        co, chi_tiet = None, "chưa có principal hoặc UID thực chưa chứng minh — không dò đăng nhập (bs-863.17)"
        if pr is not None:
            try:
                co, chi_tiet = dang_nhap_(pr, d.duong_dan or "codex", k.thu_muc_cau_hinh, path=ch.chay.path_cli)
            except LoiThuHoi:                   # A05: không spawn thêm gì (app-server) dưới principal này
                loi, chi_tiet = True, "không xác nhận thu hồi tiến trình `codex login status` — kiểm principal"
        muc = MucKiem(f"{kid} đăng nhập", "xanh" if co else "do", chi_tiet)
        ra = [muc if m.muc == muc.muc else m for m in ra] if any(m.muc == muc.muc for m in ra) else [*ra, muc]
        try:
            hm = None if loi else doc_han_muc(kid, k.thu_muc_cau_hinh, bay_gio=bay_gio or datetime.now(timezone.utc),
                                              principal=pr, path=ch.chay.path_cli, codex=d.duong_dan or "codex")
        except LoiThuHoi:
            loi = True
        except Exception:                                # noqa: BLE001 — dữ liệu app-server hỏng: vàng, không sập lệnh
            pass
        ra.append(_han_muc(kid, hm, loi))
    if ch.tram_api.startswith("https://"):
        co, chi_tiet = kiem_tag(which=dd.which, chay=dd.chay)
        ra.append(MucKiem("tailscale tag", "xanh" if co else "do", chi_tiet))
    return ra
