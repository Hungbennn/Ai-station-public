"""Nhịp tim kiêm xin việc — `POST /api/tho/nhip` (spec 3 §6.2, §6.3), mỗi 30 giây kể cả khi rảnh.
Khe rảnh → hỏi phần 4 (`chon`) chỉ khi đủ điều kiện của phần 3, rồi cấp phiếu trong giao dịch (Task 17).
Khe giữ phiếu → thẻ chắn; hợp lệ thì `han_giu = bây giờ + 10 phút`; trả lệnh dừng mềm nếu có (khe-tat, estop,
cau-dao, can-hoi); `giao_id`/`luot` cũ → `{tiep_tuc: false, ly_do: luot-cu | thu-hoi}` (dừng cứng)."""
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tram.cau_hinh.tram import CauHinhTram
from tram.chu import estop
from tram.han_muc.mo_hinh import HanMuc, co_chua_biet, doi_dang_ke, lam_moi
from tram.phieu.cap import cap_phieu, ly_do_khong_cap
from tram.phieu.cau_dao import trang_thai_cau_dao
from tram.phieu.ghi import gia_han
from tram.phieu.kho import DU_AN_TRAM, BanGhiPhieu, KhoPhieu, LuotCu, chuoi_gio
from tram.phieu.khe import dang_mat_ket_noi, khe_dang_bat, su_kien_khe
from tram.phieu.mo_hinh import DeXuatPhieu
from tram.phieu.nhip_tim import ghi_nhip, han_muc_hieu_luc
from tram.phieu.yeu_cau_tho import kiem_thuoc_may

ChonPhieu = Callable[[str, HanMuc], DeXuatPhieu | None]     # phần 4: chọn bead/bước cho khe rảnh


class ThanNhip(BaseModel):
    model_config = ConfigDict(extra="forbid")
    khe_id: str = Field(max_length=70)
    giao_id: str | None = Field(default=None, max_length=40)
    luot: int | None = Field(default=None, ge=1)
    buoc_tho: Literal["ranh", "chuan_bi", "chay", "kiem", "push", "dung"]
    han_muc: HanMuc | None = None

    @model_validator(mode="after")
    def _nhat_quan(self):
        if (self.giao_id is None) != (self.luot is None):
            raise ValueError("giao_id và luot đi cùng nhau")
        if self.han_muc is not None and self.han_muc.khe_id != self.khe_id:
            raise ValueError("han_muc.khe_id khác khe_id")
        return self


def _ghi_trang_thai_khe(kho: KhoPhieu, than: ThanNhip, bay_gio: datetime, ch: CauHinhTram) -> None:
    k, tuoi = than.khe_id, ch.han_muc.tuoi_toi_da_gio
    ghi_nhip(kho, k, luc=bay_gio, giao_id=than.giao_id, luot=than.luot, buoc_tho=than.buoc_tho, han_muc=than.han_muc)
    if dang_mat_ket_noi(kho, k):
        kho.ghi_su_kien(DU_AN_TRAM, "khe.ket_noi", {"khe_id": k}, luc=bay_gio)
    if than.han_muc is not None:              # so với `khe.han_muc` đã ghi gần nhất — trôi chậm vẫn được ghi
        moi = lam_moi(than.han_muc, k, bay_gio, tuoi_toi_da_gio=tuoi)
        cu = su_kien_khe(kho, k, ("khe.han_muc",))
        if doi_dang_ke(lam_moi(HanMuc.model_validate(cu[2]), k, bay_gio, tuoi_toi_da_gio=tuoi) if cu else None, moi):
            kho.ghi_su_kien(DU_AN_TRAM, "khe.han_muc", moi.model_dump(), luc=bay_gio)
    if co_chua_biet(han_muc_hieu_luc(kho, k, bay_gio, ch.han_muc)) and _nen_bao_khong_ro(kho, k):
        kho.ghi_su_kien(DU_AN_TRAM, "khe.han_muc_khong_ro", {"khe_id": k}, luc=bay_gio)


def _nen_bao_khong_ro(kho: KhoPhieu, khe_id: str) -> bool:
    """§8.2 luật 3: lần đầu khe ở trạng thái "còn cửa sổ chưa biết" SAU KHI đã chạy — một lần mỗi đợt."""
    if kho.db.execute("SELECT 1 FROM lan_chay WHERE khe_id = ? LIMIT 1", (khe_id,)).fetchone() is None:
        return False
    x = su_kien_khe(kho, khe_id, ("khe.han_muc_khong_ro",))
    if x is None:
        return True
    return any(not co_chua_biet(HanMuc.model_validate_json(d)) for (d,) in kho.db.execute(
        "SELECT du_lieu FROM su_kien WHERE du_an = ? AND loai = 'khe.han_muc' AND id > ?"
        " AND json_extract(du_lieu, '$.khe_id') = ?", (DU_AN_TRAM, x[0], khe_id)))


def _ly_do_dung(kho: KhoPhieu, b: BanGhiPhieu, bay_gio: datetime) -> str | None:
    if not khe_dang_bat(kho, b.phieu.khe_id):
        return "khe-tat"
    if estop.dang_bat():
        return "estop"
    if trang_thai_cau_dao(kho, b.phieu.khe_id, bay_gio).ngat:
        return "cau-dao"
    return b.dung_mem


def xu_ly_nhip(kho: KhoPhieu, may_id: str, than: ThanNhip, *, bay_gio: datetime, ch: CauHinhTram,
               chon: ChonPhieu | None = None,
               con_hop_le: Callable[[DeXuatPhieu], bool] = lambda d: True) -> dict:
    kiem_thuoc_may(kho, may_id, than.khe_id, than.giao_id)
    with kho.giao_dich() as db:
        _ghi_trang_thai_khe(kho, than, bay_gio, ch)
        if than.giao_id is not None:
            try:
                b = kho.kiem_the_chan(than.khe_id, than.giao_id, than.luot)
            except LuotCu as e:
                kho.ghi_tu_choi(e, khe_id=than.khe_id, giao_id=than.giao_id, luot=than.luot, luc=bay_gio)
                return {"tiep_tuc": False, "ly_do": "thu-hoi" if e.thu_hoi else "luot-cu"}
            han = bay_gio + timedelta(minutes=ch.tho.han_giu_phut)
            gia_han(db, than.giao_id, han_giu=han, nhip=bay_gio)
            ly_do = _ly_do_dung(kho, b, bay_gio)
            return {"tiep_tuc": ly_do is None, "han_giu": chuoi_gio(han), **({"ly_do": ly_do} if ly_do else {})}
    if chon is None or ly_do_khong_cap(kho, than.khe_id, bay_gio=bay_gio, ch=ch) is not None:
        return {"tiep_tuc": True, "phieu": None}
    de_xuat = chon(than.khe_id, han_muc_hieu_luc(kho, than.khe_id, bay_gio, ch.han_muc))
    kq = cap_phieu(kho, than.khe_id, de_xuat, bay_gio=bay_gio, ch=ch, con_hop_le=con_hop_le) if de_xuat else None
    return {"tiep_tuc": True, "phieu": kq.phieu.model_dump() if kq and kq.phieu else None}
