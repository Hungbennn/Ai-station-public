"""HTTP nội bộ lát 1b-3 của memory service (spec 1b §9.1): `/ghi` (Đại ca ghi tay) và `/danh-sach` (màn Ký ức).

Cùng Bearer `tram-nho-token` với `/nho-lai`, `/xoa`. `/danh-sach` trả cả `nguon` — chỉ tram-api (màn của Đại ca) gọi;
không có tìm theo nghĩa, không so khớp chéo dự án (§8). Lỗi: 422 `{loi}` phạm vi sai dạng, 422 `{loi, ly_do}` chạm
luật, 503 `{loi: "embedder: …" | "llm: …"}`, 401 thiếu/sai token."""
import json
from collections import Counter
from contextlib import closing
from typing import Annotated

import anthropic
from fastapi import Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from tram.nho.bang import COT, sql
from tram.nho.embed import LoiEmbedder
from tram.nho.ghi_tay import NguCanhGhiTay, TuChoiGhi, XungDotGhi, ghi_tay
from tram.nho.kho import KhoKyUc
from tram.nho.pham_vi import LoiVungCap, la_pham_vi

COT_HIEN = [c for c in COT if c != "vector"]


class ThanGhiTay(BaseModel):
    noi_dung: str = Field(min_length=1, max_length=600)
    pham_vi: str = Field(min_length=1, max_length=200)
    nhan: list[Annotated[str, Field(min_length=1, max_length=30)]] = Field(default_factory=list, max_length=5)
    ma_thao_tac: str = Field(pattern=r"^[A-Za-z0-9-]{8,64}$")


class ThanDanhSach(BaseModel):
    pham_vi: str | None = Field(default=None, max_length=200)
    cho_hieu_luc: bool = False
    gioi_han: int = Field(default=200, ge=1, le=1000)


def _loi(ma: int, **than) -> JSONResponse:
    return JSONResponse(than, status_code=ma)


def danh_sach(kho: KhoKyUc, *, pham_vi: str | None, cho_hieu_luc: bool, gioi_han: int, bay_gio: str) -> dict:
    """Ký ức chưa xoá, mới nhất trước; `cho_hieu_luc` = chỉ bản `hieu_luc_tu > bay_gio` (thăng cấp đang chờ — #19)."""
    if pham_vi is not None and not la_pham_vi(pham_vi):
        raise LoiVungCap(f"Phạm vi phải khớp chính xác một trong bốn dạng: {pham_vi[:80]!r}")
    tat_ca = kho.quet("da_xoa = false", cot=["pham_vi", "hieu_luc_tu"])
    so, cho = Counter(h["pham_vi"] for h in tat_ca), Counter(h["pham_vi"] for h in tat_ca if h["hieu_luc_tu"] > bay_gio)
    dk = "da_xoa = false" + (f" AND pham_vi = {sql(pham_vi)}" if pham_vi else "")
    dk += f" AND hieu_luc_tu > {sql(bay_gio)}" if cho_hieu_luc else ""
    ds = sorted(kho.quet(dk, cot=COT_HIEN), key=lambda h: (h["tao_luc"], h["id"]), reverse=True)
    return {"ky_uc": [{**h, "nhan": json.loads(h["nhan"]), "nguon": json.loads(h["nguon"]),
                       "quan_trong": round(float(h["quan_trong"]), 3)} for h in ds[:gioi_han]],
            "tong": len(ds), "pham_vi": [{"pham_vi": p, "so": n, "so_cho": cho[p]} for p, n in sorted(so.items())]}


def them_tuyen_1b3(app, dv, xac_thuc) -> None:
    """`dv`: DichVuNho (tram/nho/dich_vu.py) — có `client`, `vai_gop`, `mo_nhat_ky` thì `/ghi` mới chạy."""

    @app.post("/ghi", dependencies=[Depends(xac_thuc)])
    def ghi_api(than: ThanGhiTay):
        if dv.client is None or dv.vai_gop is None or dv.mo_nhat_ky is None:
            return _loi(503, loi="llm: memory service chưa cấu hình Claude cho gộp")
        with closing(dv.mo_kho_sk()) as kho_sk, closing(dv.mo_nhat_ky()) as nk:
            nc = NguCanhGhiTay(dv.kho, dv.embedder, dv.client, dv.vai_gop, nk, kho_sk, dv.luat_cua, dv.cac_du_an,
                               dv.luc)
            try:
                kq = ghi_tay(nc, noi_dung=than.noi_dung, pham_vi=than.pham_vi, nhan=than.nhan,
                             ma_thao_tac=than.ma_thao_tac)
            except LoiVungCap as e:
                return _loi(422, loi=str(e))
            except XungDotGhi as e:
                return _loi(409, loi=str(e))
            except TuChoiGhi as e:
                return _loi(422, loi="Chạm luật nghiệp vụ — /vai, /chung không nhận", ly_do=e.ly_do)
            except LoiEmbedder as e:
                return _loi(503, loi=f"embedder: {e}")
            except anthropic.APIError as e:
                return _loi(503, loi=f"llm: {type(e).__name__}")
        return kq.sang_dict()

    @app.post("/danh-sach", dependencies=[Depends(xac_thuc)])
    def danh_sach_api(than: ThanDanhSach):
        try:
            return danh_sach(dv.kho, pham_vi=than.pham_vi, cho_hieu_luc=than.cho_hieu_luc, gioi_han=than.gioi_han,
                             bay_gio=dv.luc())
        except LoiVungCap as e:
            return _loi(422, loi=str(e))
