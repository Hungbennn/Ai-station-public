"""Luật nhận việc `duoc_nhan(han_muc, uu_tien)` (spec 3 §8.2) — phần 4 gọi; phần 3 tự áp lại luật 1 khi cấp phiếu.

Người gọi truyền hạn mức ĐÃ `lam_moi` (số đo quá hạn đã thành chưa biết)."""
from tram.han_muc.mo_hinh import HanMuc


def _biet(hm: HanMuc | None):
    return [c for c in (hm.cua_so if hm else []) if c.trang_thai == "biet"]


def cham_nguong_ngung(han_muc: HanMuc | None, *, ngung: float = 90) -> bool:
    """Luật 1: một cửa sổ ĐÃ BIẾT ≥ `ngung` %."""
    return any(c.phan_tram >= ngung for c in _biet(han_muc))


def duoc_nhan(han_muc: HanMuc | None, uu_tien: int, *, ngung: float = 90, tuan_chi_uu_tien: float = 80) -> bool:
    """Theo thứ tự, luật đầu tiên khớp quyết định:
    1. cửa sổ đã biết ≥ 90% → không; 2. `tuan` đã biết ≥ 80% → chỉ P0–P1;
    3. còn cửa sổ chưa biết → nhận (#15 — cảnh báo vàng ở dashboard); 4. còn lại → nhận."""
    if not isinstance(uu_tien, int) or isinstance(uu_tien, bool) or not 0 <= uu_tien <= 4:
        raise ValueError("uu_tien phải là số 0–4 (priority của bd)")
    if cham_nguong_ngung(han_muc, ngung=ngung):
        return False
    if any(c.loai == "tuan" and c.phan_tram >= tuan_chi_uu_tien for c in _biet(han_muc)):
        return uu_tien <= 1
    return True
