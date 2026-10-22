"""Cấp phiếu (spec 3 §6.2, §6.6): MỘT giao dịch SQLite tuần tự hoá — kiểm lại mọi điều kiện của phần 3 (khe bật,
khe không giữ phiếu, cầu dao đóng, không estop, không cửa sổ đã biết ≥ ngưỡng, trần lần chạy còn chỗ), bead chưa có
phiếu hiệu lực, khoá chống trùng chưa dùng, rồi điều kiện của phần 4 (`con_hop_le`) → giữ trước ngân sách → tăng
`luot` → lưu phiếu đầy đủ (gồm `ma_giao`) → `giao.nhan` (KHÔNG có `ma_giao`)."""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from tram.cau_hinh.tram import CauHinhTram
from tram.chu import estop
from tram.han_muc.luat import cham_nguong_ngung
from tram.phieu.cau_dao import trang_thai_cau_dao
from tram.phieu.ghi import giao_id_moi, tang_luot, them_phieu
from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.khe import con_cho_chay, khe_dang_bat, cac_khe
from tram.phieu.mo_hinh import DeXuatPhieu, Phieu, sinh_ma_giao
from tram.phieu.nhip_tim import han_muc_hieu_luc


@dataclass(frozen=True)
class KetQuaCap:
    phieu: Phieu | None
    ly_do: str | None = None     # vì sao không cấp


def ly_do_khong_cap(kho: KhoPhieu, khe_id: str, *, bay_gio: datetime, ch: CauHinhTram) -> str | None:
    """Điều kiện 1–6 của §6.2 (luật cứng của phần 3, không phụ thuộc phần 4)."""
    if not khe_dang_bat(kho, khe_id):
        return "khe-tat"
    if kho.phieu_hieu_luc_cua_khe(khe_id) is not None:
        return "khe-dang-giu-phieu"
    if trang_thai_cau_dao(kho, khe_id, bay_gio).ngat:
        return "cau-dao"
    if estop.dang_bat():
        return "estop"
    if cham_nguong_ngung(han_muc_hieu_luc(kho, khe_id, bay_gio, ch.han_muc), ngung=ch.han_muc.ngung):
        return "han-muc"
    if not con_cho_chay(kho, khe_id, bay_gio, ch.tho):
        return "tran-lan-chay"
    return None


def cap_phieu(kho: KhoPhieu, khe_id: str, de_xuat: DeXuatPhieu, *, bay_gio: datetime, ch: CauHinhTram,
              con_hop_le: Callable[[DeXuatPhieu], bool] = lambda d: True) -> KetQuaCap:
    with kho.giao_dich() as db:
        if (ly_do := ly_do_khong_cap(kho, khe_id, bay_gio=bay_gio, ch=ch)) is not None:
            return KetQuaCap(None, ly_do)
        if kho.phieu_hieu_luc(de_xuat.du_an, de_xuat.bead_id) is not None:
            return KetQuaCap(None, "bead-dang-co-phieu")
        if db.execute("SELECT 1 FROM phieu WHERE khoa_chong_trung = ? AND trang_thai = 'hieu_luc'",
                      (de_xuat.khoa_chong_trung,)).fetchone():
            return KetQuaCap(None, "trung-khoa")
        dk = cac_khe(kho).get(khe_id, {})
        if de_xuat.co and (dk.get("cli") != "claude" or de_xuat.co["model"] not in dk.get("models", [])):
            return KetQuaCap(None, "cho-model")
        if not con_hop_le(de_xuat):
            return KetQuaCap(None, "phan-4-tu-choi")
        p = Phieu(**de_xuat.model_dump(), giao_id=giao_id_moi(db, bay_gio),
                  luot=tang_luot(db, de_xuat.du_an, de_xuat.bead_id), khe_id=khe_id,
                  han_giu=chuoi_gio(bay_gio + timedelta(minutes=ch.tho.han_giu_phut)), ma_giao=sinh_ma_giao())
        them_phieu(db, p, may_id=khe_id.split("/")[0], cap_luc=bay_gio)
        kho.ghi_su_kien(p.du_an, "giao.nhan", {
            "giao_id": p.giao_id, "luot": p.luot, "khe_id": khe_id, "bead_id": p.bead_id, "buoc": p.buoc,
            "vai": p.vai, "cha": p.repo.cha, "khoa_chong_trung": p.khoa_chong_trung,
            "ngan_sach": p.ngan_sach.model_dump(), "ref_phieu": p.giao_id,
            **({"co": p.co} if p.co else {})}, luc=bay_gio, bead_id=p.bead_id)
    return KetQuaCap(p)
