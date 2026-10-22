"""POST ghi trên bead (spec 2 §7): cần danh tính Đại ca + CSRF; idempotent theo ma_thao_tac (§12.3)."""
from collections.abc import Callable
from contextlib import closing

from fastapi import APIRouter, Depends, Request

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanChot, ThanCot, ThanDuyet, ThanGhi, ThanTraLoi, ThanTraVe
from tram.thao_tac.chay import KetQuaThaoTac
from tram.thao_tac.chot import chot
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.cot import keo_cot, thu_lai
from tram.thao_tac.loi import KhongHopLe
from tram.thao_tac.phe_duyet import duyet, tra_loi_decision, tra_ve

router = APIRouter(dependencies=[Depends(yeu_cau_ghi)])


def _nguon(request: Request, du_an: str):
    """4b: nguồn cho Duyệt/Trả về spec, đóng feature (`tram/thao_tac/spec.py`); None → giữ 501 của 2a."""
    pt = request.app.state.pt
    return pt.nguon_spec(du_an) if pt.nguon_spec is not None else None


def _chay(request: Request, du_an: str, bead_id: str, lam: Callable[[NguCanhGhi], KetQuaThaoTac]) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, du_an, bead_id)
    if not pt.bat_ghi(du_an):  # lát 1a-2 (D31): dự án mới thêm chỉ xem được tới khi Đại ca sửa bat_ghi: true
        raise KhongHopLe(f"Dự án {du_an} chưa bật ghi (bat_ghi: false trong du-an/{du_an}.yaml) — chỉ xem được")
    try:
        with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:     # N5: đóng kết nối mỗi yêu cầu
            kq = lam(NguCanhGhi(bd=pt.tao_bd(du_an), kho=kho, kho_tt=kho_tt, du_an=du_an,
                               nguon_duyet=pt.nguon_duyet))
    finally:
        pt.bo_dem.danh_dau_cu(du_an)               # kể cả khi lỗi giữa chừng: beads có thể đã đổi
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@router.post("/api/bead/{du_an}/{bead_id}/cot")
def r_cot(du_an: str, bead_id: str, than: ThanCot, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: keo_cot(
        nc, bead_id, cot=than.cot, vi_sao=than.vi_sao, ma=than.ma_thao_tac, expected_version=than.expected_version))


@router.post("/api/bead/{du_an}/{bead_id}/chot")
def r_chot(du_an: str, bead_id: str, than: ThanChot, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: chot(
        nc, bead_id, tra_loi=than.tra_loi, adr=than.adr, ma=than.ma_thao_tac, expected_version=than.expected_version))


@router.post("/api/bead/{du_an}/{bead_id}/thu-lai")
def r_thu_lai(du_an: str, bead_id: str, than: ThanGhi, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: thu_lai(
        nc, bead_id, ma=than.ma_thao_tac, expected_version=than.expected_version))


@router.post("/api/phe-duyet/{du_an}/{bead_id}/duyet")
def r_duyet(du_an: str, bead_id: str, than: ThanDuyet, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: duyet(
        nc, bead_id, ma=than.ma_thao_tac, expected_version=than.expected_version,
        expected_commit=than.expected_commit, digest_bead=than.digest_bead, nguon_spec=_nguon(request, du_an)))


@router.post("/api/phe-duyet/{du_an}/{bead_id}/tra-ve")
def r_tra_ve(du_an: str, bead_id: str, than: ThanTraVe, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: tra_ve(
        nc, bead_id, gop_y=than.gop_y, ma=than.ma_thao_tac, expected_version=than.expected_version,
        nguon_spec=_nguon(request, du_an)))


@router.post("/api/phe-duyet/{du_an}/{bead_id}/tra-loi")
def r_tra_loi(du_an: str, bead_id: str, than: ThanTraLoi, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: tra_loi_decision(
        nc, bead_id, tra_loi=than.tra_loi, ma=than.ma_thao_tac, expected_version=than.expected_version))
