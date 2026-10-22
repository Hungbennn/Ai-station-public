"""Nhóm `/api/tho/*` (spec 3 §5.1, §6.2–§6.6, §7.4, §9): MỌI lời gọi mang `Authorization: Bearer <token máy>` —
kể cả từ máy B. Không dùng danh tính Tailscale, không áp `X-Tram`/`Origin` của dashboard; ngược lại API dashboard bỏ
qua Bearer — token máy thợ không bao giờ có quyền của Đại ca. Lỗi: 401 token, 403 khe/phiếu không thuộc máy,
409 `{ly_do: "luot-cu"}` / `{ly_do: "request-id-trung"}`, 400 loại sự kiện lạ, 422 sai cấu trúc."""
from collections.abc import Callable
from contextlib import closing
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tram.de_nghi.cai_dat import bat_ghi_an_toan
from tram.de_nghi.nhan import TuChoiDeNghi
from tram.phieu.bao import ThanBao, nhan_bao
from tram.phieu.cau_dao import trang_thai_cau_dao
from tram.phieu.kho import LuotCu
from tram.phieu.lan_chay import LanChaySai
from tram.phieu.khe import cac_khe, dang_ky_khe
from tram.phieu.may import xac_thuc_may
from tram.phieu.nhip import ThanNhip, xu_ly_nhip
from tram.phieu.su_kien_chay import LoaiLa, ThanSuKien, nhan_su_kien_chay
from tram.phieu.yeu_cau_tho import KhongThuocMay, TrungRequest


def may_cua_yeu_cau(request: Request) -> str:
    pt = request.app.state.pt
    gia_tri = request.headers.getlist("authorization")
    if pt.mo_kho_phieu is None:
        raise HTTPException(503, "Kho phiếu chưa bật")
    token = gia_tri[0].removeprefix("Bearer ") if len(gia_tri) == 1 and gia_tri[0].startswith("Bearer ") else None
    with closing(pt.mo_kho_phieu()) as kho:
        may_id = xac_thuc_may(kho, token)
    if may_id is None:
        raise HTTPException(401, "Thiếu hoặc sai token máy")
    return may_id


router = APIRouter(prefix="/api/tho", dependencies=[Depends(may_cua_yeu_cau)])


class KheDangKy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ten: str = Field(pattern=r"^[a-z0-9-]{1,32}$")
    cli: Literal["claude", "codex"]                         # Gemini: ngoài phạm vi (spec 3 §16)
    models: list[Literal["sonnet", "opus"]] = Field(default_factory=list, max_length=2)
    ten_goi_nho: str = Field(min_length=1, max_length=64, pattern=r"^[^@]*$")
    vai_uu_tien: list[Literal["spec", "coder", "qc"]] = Field(min_length=1, max_length=3)


class ThanDangKy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    may_id: str = Field(pattern=r"^[A-Za-z0-9-]{1,32}$")
    khe: list[KheDangKy] = Field(min_length=1, max_length=16)


def _chay(lam: Callable[[], dict]):
    try:
        return lam()
    except KhongThuocMay as e:
        return JSONResponse({"loi": str(e)}, status_code=403)
    except LuotCu:
        return JSONResponse({"ly_do": "luot-cu"}, status_code=409)
    except TrungRequest:
        return JSONResponse({"ly_do": "request-id-trung"}, status_code=409)
    except TuChoiDeNghi as e:                               # TC: chỉ mã lý do, không vọng lại nội dung
        return JSONResponse({"ly_do": e.ly_do}, status_code=422)
    except LanChaySai:
        return JSONResponse({"ly_do": "lan-chay-sai"}, status_code=422)
    except LoaiLa as e:
        return JSONResponse({"loi": str(e)}, status_code=400)
    except ValidationError as e:
        return JSONResponse({"loi": f"Sai cấu trúc: {e.error_count()} lỗi"}, status_code=422)


@router.get("/ping")
def ping(request: Request, may_id: str = Depends(may_cua_yeu_cau)) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho_phieu()) as kho:
        khe = [{"khe_id": k, "cau_dao": vars(trang_thai_cau_dao(kho, k, pt.dong_ho()))}
               for k in cac_khe(kho) if k.startswith(f"{may_id}/")]
    return {"may_id": may_id, "khe": khe}


@router.post("/dang-ky")
def dang_ky(than: ThanDangKy, request: Request, may_id: str = Depends(may_cua_yeu_cau)):
    pt = request.app.state.pt
    if than.may_id != may_id:
        return JSONResponse({"loi": "may_id khác máy của token"}, status_code=403)
    with closing(pt.mo_kho_phieu()) as kho, kho.giao_dich():
        ds = dang_ky_khe(kho, may_id, [k.model_dump() for k in than.khe], luc=pt.dong_ho())
    return {"khe_id": ds}


@router.post("/nhip")
def nhip(than: ThanNhip, request: Request, may_id: str = Depends(may_cua_yeu_cau)):
    pt = request.app.state.pt
    with closing(pt.mo_kho_phieu()) as kho:
        return _chay(lambda: xu_ly_nhip(kho, may_id, than, bay_gio=pt.dong_ho(), ch=pt.cau_hinh, chon=pt.chon_phieu,
                                          con_hop_le=pt.con_hop_le_phieu))


@router.post("/bao")
def bao(than: ThanBao, request: Request, may_id: str = Depends(may_cua_yeu_cau)):
    pt = request.app.state.pt
    with closing(pt.mo_kho_phieu()) as kho:
        return _chay(lambda: nhan_bao(kho, may_id, than, bay_gio=pt.dong_ho(), ch=pt.cau_hinh,
                                      bat_ghi=lambda ten: bat_ghi_an_toan(pt.bat_ghi, ten)))


@router.post("/su-kien")
def su_kien(than: ThanSuKien, request: Request, may_id: str = Depends(may_cua_yeu_cau)):
    pt = request.app.state.pt
    with closing(pt.mo_kho_phieu()) as kho:
        return _chay(lambda: nhan_su_kien_chay(kho, may_id, than, bay_gio=pt.dong_ho(), ch=pt.cau_hinh))
