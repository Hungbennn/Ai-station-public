"""Sự kiện gần đây mọi dự án cho Tổng quan (D17/D38, khảo sát A3): danh sách cho phép từng trường + mô tả từ mẫu cố
định. Bỏ loại ồn (`dieu_phoi.nhip` ~1 dòng/phút — ranh giới 2e/2f; cập nhật hạn mức mỗi nhịp). Sự kiện `nho.*`
chỉ Đại ca thấy mô tả (như dòng thời gian bead của `/api/bead`)."""
from tram.su_kien.kho import KhoSuKien
from tram.suy.lam_sach import lam_sach
from tram.suy.mo_ta_su_kien import ma, mo_ta

QUET = 500                       # đọc tối đa 500 sự kiện mới nhất rồi lọc
BO = frozenset({"dieu_phoi.nhip", "khe.han_muc", "khe.han_muc_khong_ro"})
CHE_NHO = "Ký ức: chỉ Đại ca xem chi tiết."


def dong(s, *, la_dai_ca: bool) -> dict:
    che = s.loai.startswith("nho.") and not la_dai_ca
    return {"id": s.id, "luc": s.luc, "loai": lam_sach(s.loai, 40), "du_an": lam_sach(s.du_an, 64),
            "bead_id": ma(s.bead_id) if s.bead_id else None, "tac_nhan": lam_sach(s.tac_nhan, 80),
            "mo_ta": CHE_NHO if che else mo_ta(s)}


def gan_day(kho: KhoSuKien, gioi_han: int, *, la_dai_ca: bool) -> list[dict]:
    moc = max(0, kho.id_moi_nhat() - QUET)
    ds = [s for s in kho.sau_id(moc, QUET) if s.loai not in BO]
    return [dong(s, la_dai_ca=la_dai_ca) for s in reversed(ds[-gioi_han:])] if gioi_han > 0 else []
