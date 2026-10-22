"""Thanh trạng thái trạm chủ (spec 2 §5.3) và trang Dự án: lần quét cuối, lỗi gần nhất."""
from tram.suy.lam_sach import lam_sach


def _loi_gan_nhat(kho, du_an: str) -> dict | None:
    ds = [s for loai in ("cham_cot.loi", "quet.loi") for s in kho.gan_day(du_an, loai, 1)]
    if not ds:
        return None
    s = max(ds, key=lambda x: x.id)
    return {"luc": s.luc, "loai": s.loai, "loi": lam_sach(s.du_lieu.get("loi"), 200), "bead_id": s.bead_id}


def trang_thai_du_an(kho, du_an: str) -> dict:
    cuoi = kho.gan_day(du_an, "quet.xong", 1)
    return {"ten": du_an, "quet_cuoi": cuoi[0].luc if cuoi else None, "loi_gan_nhat": _loi_gan_nhat(kho, du_an)}


def trang_thai_tram(kho, cac_du_an: list[str], *, estop_bat: bool) -> dict:
    return {"estop": estop_bat, "du_an": [trang_thai_du_an(kho, t) for t in cac_du_an]}
