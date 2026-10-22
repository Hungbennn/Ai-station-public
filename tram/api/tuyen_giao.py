"""`GET /api/giao-viec?du_an=` (4a-2; chỉ đọc như các GET khác của 2a): lý do không giao của bead cột 1 và
lệnh/link tạo PR của bead cột 3, theo khoá "<du_an>/<bead_id>". `bat` = tram-api có đang phát phiếu không."""
from contextlib import closing

from fastapi import APIRouter, Request

from tram.api.phu_thuoc import kiem_du_an_bead
from tram.beads.bd import LoiBd
from tram.suy.giao_viec import suy_giao

router = APIRouter()


@router.get("/api/giao-viec")
def giao_viec(request: Request, du_an: str = "") -> dict:
    pt = request.app.state.pt
    if du_an:
        kiem_du_an_bead(pt, du_an)
    bo, ra = pt.bo_giao, {}
    if bo is None:
        return {"bat": False, "giao": ra}
    ten = set(pt.cac_du_an())
    with closing(pt.mo_kho()) as kho:
        for da in bo.cac_du_an():
            if da.ten not in ten or (du_an and da.ten != du_an):
                continue
            try:
                ra.update(suy_giao(da, pt.bo_dem.lay(da.ten), kho, bo.kho_git(da)))
            except LoiBd:
                continue
    return {"bat": pt.chon_phieu is not None, "giao": ra}
