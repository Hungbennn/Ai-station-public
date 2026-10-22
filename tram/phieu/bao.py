"""Nhận `POST /api/tho/bao` (spec 3 §6.3, §6.6, §7.4, §7.6). Thứ tự: kiểm cấu trúc (422) → thuộc máy (403) → trong
MỘT giao dịch: request_id đã có → kết quả cũ / 409; thẻ chắn (409 `luot-cu` + `tho.tu_choi`); ghi `bao.<loại>`;
`can_hoi` → dừng mềm `can-hoi` (4a: mọi phiếu chưa có `pham_vi_doc_lap`); báo kết thúc → phiếu hết hiệu lực (tối đa
MỘT lần); `het_han_muc` → cầu dao. Estop KHÔNG chặn báo cáo — dừng mềm phải hoàn tất được."""
from collections.abc import Callable
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tram.ban_giao.cau_truc import kiem_cau_truc
from tram.cau_hinh.tram import CauHinhTram
from tram.de_nghi.nhan import TuChoiDeNghi, ghi_bo, ghi_tu_choi, xet_de_nghi
from tram.phieu.cau_dao import ngat_cau_dao, toi_luc_het_han_muc
from tram.phieu.ghi import dat_dung_mem
from tram.phieu.kho import KhoPhieu, LuotCu
from tram.phieu.ket_thuc import ket_thuc_phieu
from tram.phieu.nhip_tim import han_muc_hieu_luc
from tram.phieu.yeu_cau_tho import digest_than, ket_qua_cu, kiem_thuoc_may, luu_ket_qua

KET_THUC = {"bi": "bi", "xong": "xong", "het_han_muc": "het_han_muc"}
LY_DO_BI = ("agent", "het-ngan-sach", "khe-tat", "estop", "cau-dao", "can-hoi", "thieu-moi-truong-kiem",
            "nhanh-bi-day-ngoai-luong", "loi-may-tho", "sai-model")


class ThanBao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    khe_id: str = Field(max_length=70)
    giao_id: str = Field(max_length=40)
    luot: int = Field(ge=1)
    loai: Literal["moc", "can_hoi", "bi", "xong", "het_han_muc", "tien_do", "viec_moi"]
    noi_dung: str = Field(default="", max_length=4000)
    ban_giao: dict | None = None
    commit: str | None = Field(default=None, pattern=r"^[0-9a-f]{7,40}$")
    request_id: str = Field(pattern=r"^[A-Za-z0-9_-]{8,64}$")
    loi_ban_giao: list[str] = Field(default_factory=list, max_length=50)
    ly_do: str | None = None
    loai_hoi: Literal["can_quyet_dinh", "thao_tac_nguy_hiem"] | None = None
    viec_moi: dict | None = None                # TC: khối việc mới — `tram.de_nghi.loc` kiểm cấu trúc (422 + sự kiện)

    @model_validator(mode="after")
    def _theo_loai(self):
        if (self.loai == "bi") != (self.ly_do is not None) or (self.ly_do and self.ly_do not in LY_DO_BI):
            raise ValueError(f"ly_do chỉ đi với bi và thuộc {LY_DO_BI}")
        if (self.loai == "can_hoi") != (self.loai_hoi is not None) or (self.loai == "can_hoi" and self.ban_giao):
            raise ValueError("can_hoi cần loai_hoi, không kèm bàn giao")
        if self.loai == "xong" and self.ban_giao is None or self.loai != "xong" and self.loi_ban_giao:
            raise ValueError("xong phải kèm bàn giao; loi_ban_giao chỉ đi với xong")
        if self.viec_moi is not None and self.loai not in ("tien_do", "viec_moi"):
            raise ValueError("viec_moi chỉ đi với đề nghị")
        if self.ban_giao is not None:
            if kiem_cau_truc(self.ban_giao, can_chinh_thuc=self.loai == "xong").luot != self.luot:
                raise ValueError("luot trong bàn giao khác luot của phiếu")
        return self


def nhan_bao(kho: KhoPhieu, may_id: str, than: ThanBao, *, bay_gio: datetime, ch: CauHinhTram,
             bat_ghi: Callable[[str], bool] = lambda _ten: False) -> dict:
    """TC: `bat_ghi` đọc `bat_ghi` của dự án cho đề nghị (thiếu → coi như khoá ghi, INV-005)."""
    kiem_thuoc_may(kho, may_id, than.khe_id, than.giao_id)
    dg, loi = digest_than(than.model_dump()), None
    with kho.giao_dich():
        if (cu := ket_qua_cu(kho, than.request_id, dg)) is not None:
            return cu
        try:
            b = kho.kiem_the_chan(than.khe_id, than.giao_id, than.luot)
            dn = xet_de_nghi(kho, b.phieu, than.model_dump(), bat_ghi=bat_ghi)      # TC: lọc, đếm, nút (D-4)
        except LuotCu as e:
            kho.ghi_tu_choi(e, khe_id=than.khe_id, giao_id=than.giao_id, luot=than.luot, luc=bay_gio)
            loi = e
        except TuChoiDeNghi as e:
            ghi_tu_choi(kho, b.phieu, e, luot=than.luot, luc=bay_gio)
            loi = e
        else:
            p = b.phieu
            du_lieu = than.model_dump(exclude={"khe_id", "loai"}, exclude_none=True)
            if than.loai != "xong":
                du_lieu.pop("loi_ban_giao", None)
            if dn is not None:
                du_lieu["ma_de_nghi"] = dn.ma
            sk = kho.ghi_su_kien(p.du_an, f"bao.{than.loai}", du_lieu, luc=bay_gio, bead_id=p.bead_id,
                                 tac_nhan=f"tho/{than.khe_id}")
            if dn is not None and dn.bo:
                ghi_bo(kho, p, dn, luc=bay_gio)
            if than.loai == "can_hoi":
                dat_dung_mem(kho.db, p.giao_id, "can-hoi")
            if than.loai in KET_THUC:
                ket_thuc_phieu(kho, b, ket_thuc=KET_THUC[than.loai], su_kien_id=sk, luc=bay_gio, moc_cuoi=bay_gio)
            if than.loai == "het_han_muc":
                hm = han_muc_hieu_luc(kho, than.khe_id, bay_gio, ch.han_muc)
                ngat_cau_dao(kho, than.khe_id, ly_do="het-han-muc", luc=bay_gio, toi_luc=toi_luc_het_han_muc(
                    hm, bay_gio, reset_luc=None, phut=ch.tho.phut_cau_dao, ngung=ch.han_muc.ngung))
            kq = {"da_nhan": True, "su_kien_id": sk, **(dn.ket_qua() if dn is not None else {})}
            luu_ket_qua(kho, than.request_id, giao_id=p.giao_id, loai=than.loai, digest=dg, ket_qua=kq, luc=bay_gio)
    if loi is not None:
        raise loi
    return kq
