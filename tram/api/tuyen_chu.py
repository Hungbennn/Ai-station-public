"""POST estop / tiếp tục từ thanh trạng thái (spec 2 §5.3) — cùng logic `tram chu estop`."""
from contextlib import closing

from fastapi import APIRouter, Depends, Request

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.than import ThanEstop, ThanGhi
from tram.thao_tac.estop import bat_estop_thao_tac, tiep_tuc_thao_tac

router = APIRouter(dependencies=[Depends(yeu_cau_ghi)])


@router.post("/api/chu/estop")
def r_estop(than: ThanEstop, request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:
        kq = bat_estop_thao_tac(kho, kho_tt, ly_do=than.ly_do, ma=than.ma_thao_tac,
                                expected_version=than.expected_version)
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@router.post("/api/chu/tiep-tuc")
def r_tiep_tuc(than: ThanGhi, request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:
        kq = tiep_tuc_thao_tac(kho, kho_tt, ma=than.ma_thao_tac, expected_version=than.expected_version)
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}
