"""Trạng thái lỗi của vòng nạp ký ức (plan 1b-1 G9): một `nho.loi_<loai>` mỗi đợt lỗi, `nho.phuc_hoi {loai}` khi hết."""
from tram.nho.ap_dung import TAC_NHAN
from tram.nho.cac_nguon import doc_nguon
from tram.su_kien.kho import KhoSuKien, SuKien

LOI_NHO = {"llm": "nho.loi_llm", "embedder": "nho.loi_embedder"}


def dang_loi(kho_sk: KhoSuKien, du_an: str, loai: str) -> SuKien | None:
    """`nho.loi_<loai>` mới nhất của dự án nếu chưa có `nho.phuc_hoi {loai}` mới hơn (lọc `loai` ngay trong SQL)."""
    ln = kho_sk.gan_day(du_an, LOI_NHO[loai], 1)
    ph = kho_sk.gan_day(du_an, "nho.phuc_hoi", 1, du_lieu_co={"loai": loai})
    return ln[0] if ln and (not ph or ln[0].id > ph[0].id) else None


def phuc_hoi(kho_sk: KhoSuKien, du_an: str) -> None:
    for loai in LOI_NHO:
        if (ln := dang_loi(kho_sk, du_an, loai)) is not None:
            kho_sk.ghi(du_an, "nho.phuc_hoi", {"loai": loai}, bead_id=ln.bead_id, tac_nhan=TAC_NHAN)


def la_nguon(sk: SuKien, kho_sk: KhoSuKien) -> bool:
    try:
        return doc_nguon(sk, kho_sk) is not None
    except Exception:                                      # noqa: BLE001 — sự kiện độc: sẽ bị bỏ, không phải chỗ kẹt
        return False
