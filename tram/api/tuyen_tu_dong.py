"""Tuyến tự merge / tự deploy (`dieu-khien-tu-dong`, design D-5). GET: ai trong tailnet cũng xem (như `/api/du-an`),
kèm `la_dai_ca` để dashboard khoá nút. POST: danh tính Đại ca, X-Tram, Origin + P/R theo hành vi + mã thao tác;
lỗi thân yêu cầu không vọng lại nội dung (`TuyenEnvelopeKin` — ô lệnh có thể chứa thứ Đại ca lỡ dán).
D138/D140: TẠM DỪNG chỉ danh tính/CSRF; Tiếp tục cần P; cài đặt lấy mức cao nhất theo thay đổi."""
from contextlib import closing

import yaml
from fastapi import APIRouter, Depends, Request

from tram.api.passkey_phu_thuoc import dich_vu
from tram.api.passkey_tu_dong import can_p, quyen_cai_dat, la_chu
from tram.api.loi_envelope import TuyenEnvelopeKin
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanCaiDatTuDong, ThanGhi
from tram.api.doi_soat_deploy import ThanTiepTuc, tiep_tuc
from tram.chu import estop
from tram.suy.tu_dong import chi_tiet_du_an, chung, tom_tat_du_an
from tram.suy.tu_merge import tieu_de_bead  # TM-2
from tram.thao_tac.tu_dong import luu_cai_dat_thao_tac, tam_dung_thao_tac
from tram.tu_dong.cai_dat import tu_api
from tram.tu_dong.luu import DU_AN_TRAM

doc = APIRouter()
ghi = APIRouter(dependencies=[Depends(dich_vu)], route_class=TuyenEnvelopeKin)


def kenh_ghi(request: Request) -> str:
    return getattr(request.app.state, "kenh_ghi", "header")


def _bat_ghi(pt, ten: str) -> bool:
    """Như `tuyen_doc._bat_ghi`: yaml lỗi/khoá sai → False (INV-005: không bật được gì)."""
    try:
        return pt.bat_ghi(ten)
    except (OSError, ValueError, AttributeError, yaml.YAMLError):
        return False


def _chung(request: Request, kho) -> dict:
    return {**chung(kho, kenh_ghi=kenh_ghi(request), la_dai_ca=la_chu(request),
                   estop_bat=estop.dang_bat()), "chi_tam_dung": False}


@doc.get("/api/tu-dong")
def r_tom_tat(request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho:
        ds = [tom_tat_du_an(kho, t, bat_ghi=_bat_ghi(pt, t)) for t in pt.cac_du_an()]
        return {**_chung(request, kho), "du_an": ds}


@doc.get("/api/du-an/{ten}/tu-dong")
def r_chi_tiet(ten: str, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    with closing(pt.mo_kho()) as kho:
        return {**_chung(request, kho), **chi_tiet_du_an(kho, ten, bat_ghi=_bat_ghi(pt, ten),
                                                         tieu_de=tieu_de_bead(pt.bo_dem, ten))}


def _chay(request: Request, lam) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:      # N5: đóng kết nối mỗi yêu cầu
        kq = lam(kho, kho_tt)
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@ghi.post("/api/du-an/{ten}/tu-dong/cai-dat")
def r_cai_dat(ten: str, than: ThanCaiDatTuDong, request: Request,
              quyen=Depends(quyen_cai_dat)) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    cd, bg = tu_api(than.cai_dat.model_dump()), _bat_ghi(pt, ten)
    return _chay(request, lambda k, kt: luu_cai_dat_thao_tac(
        k, kt, ten, cd, bat_ghi=bg, ma=than.ma_thao_tac, expected_version=than.expected_version, kiem_quyen=quyen))


def _tam_dung(request: Request, du_an: str, than: ThanGhi, tam_dung: bool, *, toan_tram: bool = False) -> dict:
    if not toan_tram:                     # `/api/du-an/_tram/…` → 404: tuyến dự án không tạm dừng cả trạm
        kiem_du_an_bead(request.app.state.pt, du_an)
    return _chay(request, lambda k, kt: tam_dung_thao_tac(
        k, kt, du_an, tam_dung=tam_dung, ma=than.ma_thao_tac, expected_version=than.expected_version))


@ghi.post("/api/du-an/{ten}/tu-dong/tam-dung")
def r_tam_dung(ten: str, than: ThanGhi, request: Request) -> dict:
    return _tam_dung(request, ten, than, True)


@ghi.post("/api/du-an/{ten}/tu-dong/tiep-tuc", dependencies=[Depends(can_p)])
def r_tiep_tuc(ten: str, than: ThanTiepTuc, request: Request) -> dict:
    kiem_du_an_bead(request.app.state.pt, ten)
    return _chay(request, lambda k, kt: tiep_tuc(k, kt, ten, than))


@ghi.post("/api/tu-dong/tam-dung")
def r_tam_dung_tram(than: ThanGhi, request: Request) -> dict:
    return _tam_dung(request, DU_AN_TRAM, than, True, toan_tram=True)


@ghi.post("/api/tu-dong/tiep-tuc", dependencies=[Depends(can_p)])
def r_tiep_tuc_tram(than: ThanGhi, request: Request) -> dict:
    return _tam_dung(request, DU_AN_TRAM, than, False, toan_tram=True)
