"""Các GET lát 2a (spec 2 §7) — mọi trạng thái tính lúc đọc từ beads + sự kiện (Q12)."""
from collections import Counter
from contextlib import closing

import yaml
from fastapi import APIRouter, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.beads.bd import LoiBd
from tram.chu import estop
from tram.suy.chi_tiet import chi_tiet_bead
from tram.suy.cot import HANG, hien_tren_bang, the_bead
from tram.suy.lam_sach import lam_sach
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.phe_duyet_khe import muc_cau_dao
from tram.suy.trang_thai import trang_thai_du_an, trang_thai_tram
from tram.thao_tac.loi import KhongThay

router = APIRouter()


def _doc_beads(pt, ten: list[str]) -> tuple[dict, dict]:
    beads, loi = {}, {}
    for t in ten:
        try:
            beads[t] = pt.bo_dem.lay(t)
        except LoiBd as e:
            loi[t] = lam_sach(str(e), 300)
    return beads, loi


def _the(beads: dict) -> list[dict]:
    ra = []
    for du_an, ds in beads.items():
        theo_id = {b.id: b for b in ds}
        ra += [the_bead(du_an, b, theo_id) for b in ds if hien_tren_bang(b)]
    return ra


def _bat_ghi(pt, ten: str) -> bool:
    """Lát 1a-2 (D31, D37): False → dashboard hiện chip "chỉ quét thử". Yaml lỗi/khoá sai → False
    (tuyến ghi cũng không ghi được dự án đó)."""
    try:
        return pt.bat_ghi(ten)
    except (OSError, ValueError, AttributeError, yaml.YAMLError):
        return False


@router.get("/api/du-an")
def du_an(request: Request) -> dict:
    pt = request.app.state.pt
    ten = pt.cac_du_an()
    beads, loi = _doc_beads(pt, ten)
    the, ra = _the(beads), []
    with closing(pt.mo_kho()) as kho:
        for t in ten:
            dem = Counter(x["hang"] for x in the if x["du_an"] == t)
            ra.append({**trang_thai_du_an(kho, t), "bat_ghi": _bat_ghi(pt, t),
                       "so_bead": {h: dem.get(h, 0) for h in HANG}, "loi_doc": loi.get(t)})
    return {"du_an": ra}


@router.get("/api/cong-viec")
def cong_viec(request: Request, du_an: str = "") -> dict:
    pt = request.app.state.pt
    if du_an:
        kiem_du_an_bead(pt, du_an)
    beads, loi = _doc_beads(pt, [du_an] if du_an else pt.cac_du_an())
    return {"the": _the(beads), "loi": loi}


@router.get("/api/bead/{du_an}/{bead_id}")
def bead(du_an: str, bead_id: str, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, du_an, bead_id)
    theo_id = {b.id: b for b in pt.bo_dem.lay(du_an)}
    if bead_id not in theo_id:
        raise KhongThay(f"Không thấy bead {bead_id}")
    with closing(pt.mo_kho()) as kho:
        ra = chi_tiet_bead(du_an, theo_id[bead_id], theo_id, kho)
    if not la_dai_ca_yeu_cau(request):
        for sk in ra["dong_thoi_gian"]:
            if sk["loai"].startswith("nho."):
                sk["tom_tat"] = "Ký ức: chỉ Đại ca xem chi tiết."
    return ra


@router.get("/api/phe-duyet")
def phe_duyet(request: Request) -> dict:
    pt = request.app.state.pt
    ten = pt.cac_du_an()
    beads, loi = _doc_beads(pt, ten)
    them = []
    if pt.mo_kho_phieu is not None:                       # 2b: cầu dao khe đang ngắt (spec 2 §5.2)
        with closing(pt.mo_kho_phieu()) as kp:
            them = muc_cau_dao(kp, pt.dong_ho())
    with closing(pt.mo_kho()) as kho:
        muc = gom_phe_duyet(ten, beads, kho, them)
    return {"muc": muc, "so": len(muc), "loi": loi}


@router.get("/api/chu/trang-thai")
def trang_thai(request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho:
        tt = trang_thai_tram(kho, pt.cac_du_an(), estop_bat=estop.dang_bat())
    return {**tt, "la_dai_ca": la_dai_ca_yeu_cau(request)}
