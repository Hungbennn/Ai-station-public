"""Nhận `POST /api/tho/su-kien` (spec 3 §7.4, §7.6, §8.3, §10): chỉ `chay.bat_dau`, `chay.xong`, `chay.don_rac`
(loại khác → 400). `chay.bat_dau` ghi bảng `lan_chay` (đếm lần chạy, duy nhất theo request_id — trần §8.3, quyết
toán §7.6); `chay.xong` xét cầu dao. Idempotent theo request_id; thẻ chắn như `bao`."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tram.cau_hinh.tram import CauHinhTram
from tram.chay_cli.giao_dien import KET_THUC
from tram.phieu.cau_dao import xet_sau_chay
from tram.phieu.lan_chay import kiem_lan_chay
from tram.phieu.kho import KhoPhieu, LuotCu, chuoi_gio
from tram.phieu.nhip_tim import han_muc_hieu_luc
from tram.phieu.yeu_cau_tho import digest_than, ket_qua_cu, kiem_thuoc_may, luu_ket_qua


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DuLieuBatDau(_M):
    lan: int = Field(ge=1, le=3)


class DuLieuXong(_M):
    lan: int = Field(ge=1, le=3)
    ket_thuc: Literal[KET_THUC]
    ma_thoat: int | None = None
    mo_hinh: str | None = Field(default=None, max_length=100)
    token_vao: int = Field(default=0, ge=0)
    token_ra: int = Field(default=0, ge=0)
    token_cache_doc: int = Field(default=0, ge=0)
    token_cache_ghi: int = Field(default=0, ge=0)
    thoi_gian_ms: int = Field(default=0, ge=0)
    digest_log: str = Field(default="", max_length=80)
    reset_luc: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class DuLieuDonRac(_M):
    nhanh_rac: str = Field(pattern=r"^rac/[A-Za-z0-9._-]{1,100}$")


LOAI_CHAY = {"chay.bat_dau": DuLieuBatDau, "chay.xong": DuLieuXong, "chay.don_rac": DuLieuDonRac}


class ThanSuKien(_M):
    khe_id: str = Field(max_length=70)
    giao_id: str = Field(max_length=40)
    luot: int = Field(ge=1)
    loai: str = Field(max_length=40)
    du_lieu: dict
    request_id: str = Field(pattern=r"^[A-Za-z0-9_-]{8,64}$")


class LoaiLa(ValueError):
    """400: loại sự kiện thợ không được gửi."""


def nhan_su_kien_chay(kho: KhoPhieu, may_id: str, than: ThanSuKien, *, bay_gio: datetime,
                      ch: CauHinhTram) -> dict:
    if than.loai not in LOAI_CHAY:
        raise LoaiLa(f"Thợ chỉ gửi {sorted(LOAI_CHAY)}")
    dl = LOAI_CHAY[than.loai].model_validate(than.du_lieu)        # ValidationError → 422
    kiem_thuoc_may(kho, may_id, than.khe_id, than.giao_id)
    dg, loi = digest_than(than.model_dump()), None
    with kho.giao_dich():
        if (cu := ket_qua_cu(kho, than.request_id, dg)) is not None:
            return cu
        try:
            b = kho.kiem_the_chan(than.khe_id, than.giao_id, than.luot)
        except LuotCu as e:
            kho.ghi_tu_choi(e, khe_id=than.khe_id, giao_id=than.giao_id, luot=than.luot, luc=bay_gio)
            loi = e
        else:
            p, d = b.phieu, dl.model_dump()
            kiem_lan_chay(kho, p, than.loai, d)
            cot = {k: d[k] for k in ("token_vao", "token_ra", "mo_hinh", "thoi_gian_ms") if k in d}
            sk = kho.ghi_su_kien(p.du_an, than.loai, {"giao_id": p.giao_id, "luot": p.luot, "khe_id": than.khe_id,
                                                      "request_id": than.request_id, **d},
                                 luc=bay_gio, bead_id=p.bead_id, tac_nhan=f"tho/{than.khe_id}", **cot)
            if than.loai == "chay.bat_dau":
                kho.db.execute("INSERT INTO lan_chay (request_id, khe_id, giao_id, lan, luc) VALUES (?,?,?,?,?)",
                               (than.request_id, than.khe_id, p.giao_id, d["lan"], chuoi_gio(bay_gio)))
            if than.loai == "chay.xong":
                xet_sau_chay(kho, than.khe_id, d["ket_thuc"], reset_luc=d["reset_luc"], bay_gio=bay_gio,
                             han_muc=han_muc_hieu_luc(kho, than.khe_id, bay_gio, ch.han_muc), ch=ch.tho,
                             nguong=ch.han_muc)
            kq = {"da_nhan": True, "su_kien_id": sk}
            luu_ket_qua(kho, than.request_id, giao_id=p.giao_id, loai=than.loai, digest=dg, ket_qua=kq, luc=bay_gio)
    if loi is not None:
        raise loi
    return kq
