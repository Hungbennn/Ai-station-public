"""Bảng `nhip_tim` — GHI ĐÈ, không phải lịch sử (spec 3 §10, §13 mục 3) — và hạn mức hiệu lực của khe."""
import json
from dataclasses import dataclass
from datetime import datetime

from tram.cau_hinh.tram import CauHinhHanMuc
from tram.han_muc.mo_hinh import HanMuc, lam_moi
from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.khe import su_kien_khe


@dataclass(frozen=True)
class NhipTim:
    khe_id: str
    luc: str
    giao_id: str | None
    luot: int | None
    buoc_tho: str
    han_muc: HanMuc | None


def doc_nhip(kho: KhoPhieu, khe_id: str) -> NhipTim | None:
    h = kho.db.execute("SELECT luc, giao_id, luot, buoc_tho, han_muc FROM nhip_tim WHERE khe_id = ?",
                       (khe_id,)).fetchone()
    if h is None:
        return None
    return NhipTim(khe_id, h[0], h[1], h[2], h[3], HanMuc.model_validate_json(h[4]) if h[4] else None)


def ghi_nhip(kho: KhoPhieu, khe_id: str, *, luc: datetime, giao_id: str | None, luot: int | None, buoc_tho: str,
             han_muc: HanMuc | None) -> None:
    kho.db.execute(
        "INSERT INTO nhip_tim (khe_id, luc, giao_id, luot, buoc_tho, han_muc) VALUES (?,?,?,?,?,?)"
        " ON CONFLICT(khe_id) DO UPDATE SET luc = excluded.luc, giao_id = excluded.giao_id, luot = excluded.luot,"
        " buoc_tho = excluded.buoc_tho, han_muc = excluded.han_muc",
        (khe_id, chuoi_gio(luc), giao_id, luot, buoc_tho, han_muc.model_dump_json() if han_muc else None))


def han_muc_hieu_luc(kho: KhoPhieu, khe_id: str, bay_gio: datetime, nguong: CauHinhHanMuc) -> HanMuc:
    """`nhip_tim.han_muc` mới nhất; không có thì `khe.han_muc`; số đo quá hạn/quá tuổi → chưa biết (§8.1, §10.1)."""
    nhip = doc_nhip(kho, khe_id)
    hm = nhip.han_muc if nhip else None
    if hm is None and (sk := su_kien_khe(kho, khe_id, ("khe.han_muc",))) is not None:
        hm = HanMuc.model_validate(sk[2])
    return lam_moi(hm, khe_id, bay_gio, tuoi_toi_da_gio=nguong.tuoi_toi_da_gio)
