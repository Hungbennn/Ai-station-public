"""Công tắc TC (design D-8/D-9): đọc cho tailnet; mọi ghi cần phiên P theo D138.
Giữ mã thao tác, expected_version, bat_ghi và ledger; D113 về kênh tạm đã được D138 thay thế."""
from contextlib import closing

from fastapi import APIRouter, Depends, Request

from tram.api.passkey_phu_thuoc import dich_vu
from tram.api.passkey_tu_dong import can_p, la_chu
from tram.api.loi_envelope import TuyenEnvelopeKin
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanTuCapNhat
from tram.api.tuyen_tu_dong import kenh_ghi
from tram.de_nghi.cai_dat import CaiDatTuCapNhat, bat_ghi_an_toan
from tram.suy.tu_cap_nhat import chi_tiet, de_nghi_cua_bead
from tram.thao_tac.tu_cap_nhat import luu_tu_cap_nhat_thao_tac

doc = APIRouter()
ghi = APIRouter(dependencies=[Depends(dich_vu), Depends(can_p)], route_class=TuyenEnvelopeKin)


@doc.get("/api/du-an/{ten}/tu-cap-nhat")
def r_xem(ten: str, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    with closing(pt.mo_kho()) as kho:
        return {**chi_tiet(kho.db, ten, bat_ghi=bat_ghi_an_toan(pt.bat_ghi, ten), kenh_ghi=kenh_ghi(request),
                        la_dai_ca=la_chu(request)), "chi_tat": False}


@doc.get("/api/du-an/{ten}/bead/{bead_id}/de-nghi")
def r_de_nghi(ten: str, bead_id: str, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten, bead_id)
    with closing(pt.mo_kho()) as kho:
        return {"du_an": ten, "bead_id": bead_id,
                "de_nghi": de_nghi_cua_bead(kho.db, ten, bead_id, bat_ghi=bat_ghi_an_toan(pt.bat_ghi, ten))}


@ghi.post("/api/du-an/{ten}/tu-cap-nhat")
def r_luu(ten: str, than: ThanTuCapNhat, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    cd = CaiDatTuCapNhat(**than.cai_dat.model_dump())
    with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:      # N5: đóng kết nối mỗi yêu cầu
        kq = luu_tu_cap_nhat_thao_tac(kho, kho_tt, ten, cd, bat_ghi=bat_ghi_an_toan(pt.bat_ghi, ten),
                                      ma=than.ma_thao_tac, expected_version=than.expected_version)
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}
