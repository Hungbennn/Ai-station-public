"""Mục "Hệ cần xem" cho cầu dao khe đang ngắt (spec 2 §5.2 — nguồn "cầu dao khe (phần 3)"; spec 3 §8.3).
Không có nút "thử lại": Đại ca đóng cầu dao ở trang Đội ngũ AI hoặc chờ cầu dao tự đóng khi tới giờ."""
from datetime import datetime

from tram.phieu.cau_dao import LOAI, trang_thai_cau_dao
from tram.phieu.khe import cac_khe, su_kien_khe
from tram.phieu.kho import DU_AN_TRAM, KhoPhieu
from tram.suy.lam_sach import lam_sach

LY_DO = {"het-han-muc": "hết hạn mức", "loi-lien-tiep": "lỗi không do agent liên tiếp"}


def muc_cau_dao(kho: KhoPhieu, bay_gio: datetime) -> list[dict]:
    ra = []
    for khe_id in sorted(cac_khe(kho)):
        cd = trang_thai_cau_dao(kho, khe_id, bay_gio)
        if not cd.ngat:
            continue
        luc = su_kien_khe(kho, khe_id, LOAI)[3]
        loi = f"Cầu dao khe {khe_id} ngắt tới {cd.toi_luc} — {LY_DO.get(cd.ly_do, cd.ly_do)}"
        ra.append({"loai": "he", "du_an": DU_AN_TRAM, "bead_id": None, "tieu_de": f"Khe {khe_id}", "uu_tien": None,
                   "updated_at": None, "chi_tiet": {"su_kien": "khe.cau_dao_ngat", "luc": luc, "khe_id": khe_id,
                                                    "toi_luc": cd.toi_luc, "loi": lam_sach(loi, 300)}})
    return ra
