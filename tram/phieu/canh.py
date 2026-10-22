"""Bộ canh hợp đồng (spec 3 §6.3, §8.3), chạy trong tiến trình tram-api mỗi 60 giây:
- nhịp tim cuối của khe > 90 giây (khe chưa có nhịp nào cũng tính) → `khe.mat_ket_noi` (một lần mỗi đợt);
- phiếu quá `han_giu` (10 phút sau nhịp tim hợp lệ cuối) → thu hồi `mat-nhip` (H3: ≤ 11 phút);
- cầu dao ngắt đã tới giờ → `khe.cau_dao_dong`."""
import sys
import threading
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from tram.cau_hinh.tram import CauHinhTram, nap_cau_hinh_tram
from tram.duong_dan import doc_luc
from tram.phieu.cau_dao import dong_cau_dao_het_gio
from tram.phieu.kho import DU_AN_TRAM, KhoPhieu, mo_kho_phieu
from tram.phieu.ket_thuc import thu_hoi
from tram.phieu.khe import cac_khe, dang_mat_ket_noi
from tram.phieu.nhip_tim import doc_nhip

CHU_KY_GIAY = 60


def mot_vong_canh(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram) -> dict[str, list[str]]:
    ra: dict[str, list[str]] = {"mat_ket_noi": [], "thu_hoi": [], "cau_dao_dong": []}
    nguong = timedelta(seconds=ch.tho.mat_ket_noi_giay)
    with kho.giao_dich():
        for khe_id in cac_khe(kho):
            nhip = doc_nhip(kho, khe_id)
            if (nhip is None or bay_gio - doc_luc(nhip.luc) > nguong) and not dang_mat_ket_noi(kho, khe_id):
                kho.ghi_su_kien(DU_AN_TRAM, "khe.mat_ket_noi", {"khe_id": khe_id}, luc=bay_gio)
                ra["mat_ket_noi"].append(khe_id)
        for b in kho.cac_phieu_hieu_luc():
            if doc_luc(b.phieu.han_giu) < bay_gio:
                thu_hoi(kho, b, ly_do="mat-nhip", luc=bay_gio)
                ra["thu_hoi"].append(b.phieu.giao_id)
        ra["cau_dao_dong"] = dong_cau_dao_het_gio(kho, bay_gio)
    return ra


def chay_canh(dung: threading.Event, *, mo_kho: Callable[[], KhoPhieu] = mo_kho_phieu,
              nap_ch: Callable[[], CauHinhTram] = nap_cau_hinh_tram, chu_ky: float = CHU_KY_GIAY,
              dong_ho: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
    """Vòng lặp tới khi `dung` được đặt; lỗi một vòng không làm chết vòng sau."""
    while not dung.is_set():
        try:
            kho = mo_kho()
            try:
                mot_vong_canh(kho, bay_gio=dong_ho(), ch=nap_ch())
            finally:
                kho.close()
        except Exception as e:                       # noqa: BLE001 — ghi log rồi thử vòng sau
            print(f"[tram-canh] lỗi: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        dung.wait(chu_ky)


def bat_dau_canh(dung: threading.Event, **kw) -> threading.Thread:
    t = threading.Thread(target=chay_canh, args=(dung,), kwargs=kw, name="tram-canh", daemon=True)
    t.start()
    return t
