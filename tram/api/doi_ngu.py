"""Lát 2b (spec 2 §5.4, §7): `GET /api/doi-ngu`; `POST /api/khe/{may_id}/{ten}/tat|bat|cau-dao-dong` với
`khe_id = <may_id>/<ten>` (spec 3 §4 — URL đúng dạng `/api/khe/B/claude-1/tat`). POST cần danh tính Đại ca +
CSRF như mọi API ghi (spec 2 §4) và `ma_thao_tac` + `expected_version` (§12.3); Bearer token máy thợ không mở
được nhóm này (spec 3 §5.1)."""
import re
from collections.abc import Callable
from contextlib import closing

from fastapi import APIRouter, Depends, Request
from pydantic import Field

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanGhi
from tram.phieu.khe import KheLa
from tram.suy.doi_ngu import SO_NGAY_BANG_DIEM, doi_ngu
from tram.thao_tac.khe import bat_khe_thao_tac, dong_cau_dao_thao_tac, tat_khe_thao_tac
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay

KHE_RE = re.compile(r"[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}")
SO_NGAY_TOI_DA = 92                       # như /api/usage
router = APIRouter()


class ThanKhe(ThanGhi):
    vi_sao: str | None = Field(default=None, max_length=500)


@router.get("/api/doi-ngu")
def r_doi_ngu(request: Request, du_an: str = "", so_ngay: int = SO_NGAY_BANG_DIEM) -> dict:
    """`?du_an=` (rỗng = mọi dự án; dự án lạ → 404) và `?so_ngay=` (1–92, mặc định 30) chỉ lọc bảng điểm (D14)."""
    pt = request.app.state.pt
    if not 1 <= so_ngay <= SO_NGAY_TOI_DA:
        raise KhongHopLe(f"so_ngay phải trong 1–{SO_NGAY_TOI_DA}")
    if du_an:
        kiem_du_an_bead(pt, du_an)
    if pt.mo_kho_phieu is None:
        return {"bat": False, "khe": [], "luat_vai": None, "bang_diem": []}
    with closing(pt.mo_kho_phieu()) as kho:
        return doi_ngu(kho, bay_gio=pt.dong_ho(), ch=pt.cau_hinh, du_an=du_an or None, so_ngay=so_ngay)


def _ghi(request: Request, may_id: str, ten: str, lam: Callable) -> dict:
    pt, khe_id = request.app.state.pt, f"{may_id}/{ten}"
    if not KHE_RE.fullmatch(khe_id):
        raise KhongHopLe("Mã khe không hợp lệ")
    if pt.mo_kho_phieu is None:
        raise ChuaHoTro("Kho phiếu chưa bật (phần 3)")
    try:
        with closing(pt.mo_kho_phieu()) as kho, closing(pt.mo_kho_tt()) as kho_tt:
            kq = lam(kho, kho_tt, khe_id, pt.dong_ho())
    except KheLa as e:                                   # khe bị gỡ giữa lúc kiểm và lúc ghi
        raise KhongThay(str(e)) from None
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@router.post("/api/khe/{may_id}/{ten}/tat", dependencies=[Depends(yeu_cau_ghi)])
def r_tat(may_id: str, ten: str, than: ThanKhe, request: Request) -> dict:
    return _ghi(request, may_id, ten, lambda kho, kt, khe_id, luc: tat_khe_thao_tac(
        kho, kt, khe_id, vi_sao=than.vi_sao, ma=than.ma_thao_tac, expected_version=than.expected_version, luc=luc))


@router.post("/api/khe/{may_id}/{ten}/bat", dependencies=[Depends(yeu_cau_ghi)])
def r_bat(may_id: str, ten: str, than: ThanKhe, request: Request) -> dict:
    return _ghi(request, may_id, ten, lambda kho, kt, khe_id, luc: bat_khe_thao_tac(
        kho, kt, khe_id, vi_sao=than.vi_sao, ma=than.ma_thao_tac, expected_version=than.expected_version, luc=luc))


@router.post("/api/khe/{may_id}/{ten}/cau-dao-dong", dependencies=[Depends(yeu_cau_ghi)])
def r_cau_dao_dong(may_id: str, ten: str, than: ThanGhi, request: Request) -> dict:
    return _ghi(request, may_id, ten, lambda kho, kt, khe_id, luc: dong_cau_dao_thao_tac(
        kho, kt, khe_id, ma=than.ma_thao_tac, expected_version=than.expected_version, luc=luc))
