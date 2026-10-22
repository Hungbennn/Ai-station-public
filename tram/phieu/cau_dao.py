"""Cầu dao của khe (spec 3 §8.3). Ngắt khi CLI báo hết hạn mức / 429, hoặc N lần chạy liên tiếp lỗi KHÔNG do agent
(`ket_thuc = loi_he`, xem `tram.chay_cli.giao_dien.ket_thuc_tu`). Ngắt tới `reset_luc` của cửa sổ đã cạn; không biết
thì `phut_cau_dao` (60). Hạn mức CHƯA BIẾT không tự làm cầu dao ngắt."""
import json
from dataclasses import dataclass
from datetime import datetime, timedelta

from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhThoTram
from tram.duong_dan import doc_luc
from tram.han_muc.mo_hinh import HanMuc
from tram.phieu.kho import DU_AN_TRAM, KhoPhieu, chuoi_gio
from tram.phieu.khe import cac_khe, su_kien_khe

LOAI = ("khe.cau_dao_ngat", "khe.cau_dao_dong")


@dataclass(frozen=True)
class TrangThaiCauDao:
    ngat: bool
    ly_do: str | None = None
    toi_luc: str | None = None


def trang_thai_cau_dao(kho: KhoPhieu, khe_id: str, bay_gio: datetime) -> TrangThaiCauDao:
    x = su_kien_khe(kho, khe_id, LOAI)
    if x is None or x[1] != "khe.cau_dao_ngat" or doc_luc(x[2]["toi_luc"]) <= bay_gio:
        return TrangThaiCauDao(False)
    return TrangThaiCauDao(True, x[2]["ly_do"], x[2]["toi_luc"])


def ngat_cau_dao(kho: KhoPhieu, khe_id: str, *, ly_do: str, toi_luc: datetime, luc: datetime) -> bool:
    """Trong giao dịch. Đã ngắt tới muộn hơn hoặc bằng → không ghi lại."""
    tt = trang_thai_cau_dao(kho, khe_id, luc)
    if tt.ngat and doc_luc(tt.toi_luc) >= toi_luc:
        return False
    kho.ghi_su_kien(DU_AN_TRAM, "khe.cau_dao_ngat", {"khe_id": khe_id, "ly_do": ly_do,
                                                   "toi_luc": chuoi_gio(toi_luc)}, luc=luc)
    return True


def toi_luc_het_han_muc(han_muc: HanMuc | None, bay_gio: datetime, *, reset_luc: str | None, phut: int,
                        ngung: float) -> datetime:
    moc = [doc_luc(reset_luc)] if reset_luc else []
    moc += [doc_luc(c.reset_luc) for c in (han_muc.cua_so if han_muc else [])
            if c.trang_thai == "biet" and c.reset_luc and c.phan_tram >= ngung]
    moc = [m for m in moc if m > bay_gio]
    return max(moc) if moc else bay_gio + timedelta(minutes=phut)


def _loi_he_lien_tiep(kho: KhoPhieu, khe_id: str, n: int) -> bool:
    moc = su_kien_khe(kho, khe_id, LOAI)
    ds = kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'chay.xong' AND id > ?"
                        " AND json_extract(du_lieu, '$.khe_id') = ? ORDER BY id DESC LIMIT ?",
                        (moc[0] if moc else 0, khe_id, n)).fetchall()
    return len(ds) == n and all(json.loads(d)["ket_thuc"] == "loi_he" for (d,) in ds)


def xet_sau_chay(kho: KhoPhieu, khe_id: str, ket_thuc: str, *, reset_luc: str | None, han_muc: HanMuc | None,
                 bay_gio: datetime, ch: CauHinhThoTram, nguong: CauHinhHanMuc) -> bool:
    """Trong giao dịch, SAU khi đã ghi `chay.xong`. Trả True nếu vừa ngắt."""
    if ket_thuc == "het_han_muc":
        toi = toi_luc_het_han_muc(han_muc, bay_gio, reset_luc=reset_luc, phut=ch.phut_cau_dao, ngung=nguong.ngung)
        return ngat_cau_dao(kho, khe_id, ly_do="het-han-muc", toi_luc=toi, luc=bay_gio)
    if ket_thuc == "loi_he" and _loi_he_lien_tiep(kho, khe_id, ch.loi_he_lien_tiep):
        return ngat_cau_dao(kho, khe_id, ly_do="loi-lien-tiep", toi_luc=bay_gio + timedelta(minutes=ch.phut_cau_dao),
                            luc=bay_gio)
    return False


def dong_cau_dao(kho: KhoPhieu, khe_id: str, *, ly_do: str, luc: datetime, tac_nhan: str = "tram/api",
                 them: dict | None = None) -> None:
    """`them` = `{ma_thao_tac}` khi Đại ca đóng tay từ dashboard 2b (spec 3 §8.3)."""
    kho.ghi_su_kien(DU_AN_TRAM, "khe.cau_dao_dong", {**(them or {}), "khe_id": khe_id, "ly_do": ly_do,
                                                    "toi_luc": None}, luc=luc, tac_nhan=tac_nhan)


def dong_cau_dao_het_gio(kho: KhoPhieu, bay_gio: datetime) -> list[str]:
    """Bộ canh: cầu dao tự đóng khi tới giờ (`khe.cau_dao_dong {ly_do: "het-gio"}`). Trong giao dịch."""
    ra = []
    for khe_id in cac_khe(kho):
        x = su_kien_khe(kho, khe_id, LOAI)
        if x is not None and x[1] == "khe.cau_dao_ngat" and doc_luc(x[2]["toi_luc"]) <= bay_gio:
            dong_cau_dao(kho, khe_id, ly_do="het-gio", luc=bay_gio)
            ra.append(khe_id)
    return ra
