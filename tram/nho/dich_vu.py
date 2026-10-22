"""HTTP nội bộ của memory service — 127.0.0.1:7710 (spec 1b §9.1). Lát 1b-1: `/nho-lai`, `/xoa`; 1b-3: `/ghi`,
`/danh-sach` (tram/nho/dich_vu_ghi.py).

Mọi lời gọi cần `Authorization: Bearer <tram-nho-token>` (so hằng thời gian). Người gọi truyền vùng cấp tường minh;
service vẫn kiểm dạng (§4). MCP (`/mcp`) thuộc lát 1b-2."""
import hmac
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from tram.cau_hinh.du_an import liet_ke_du_an
from tram.duong_dan import bay_gio
from tram.nho.dich_vu_ghi import them_tuyen_1b3
from tram.nho.embed import Embedder, LoiEmbedder
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn, luat_cua_du_an
from tram.nho.nhat_ky import NhatKy
from tram.nho.nho_lai import BoDemDung, nho_lai
from tram.nho.pham_vi import LoiVungCap, du_an_cua
from tram.su_kien.kho import KhoSuKien

TAC_NHAN = "tram/nho"


class ThanNhoLai(BaseModel):
    truy_van: str = Field(min_length=1, max_length=4000)
    vung_cap: list[str] = Field(min_length=1, max_length=10)


class ThanXoa(BaseModel):
    id: str = Field(pattern=r"^[A-Za-z0-9-]{1,64}$")


@dataclass
class DichVuNho:
    kho: KhoKyUc
    embedder: Embedder
    mo_kho_sk: Callable[[], KhoSuKien]
    dem_dung: BoDemDung
    token: str
    client: object | None = None                              # 1b-3: Claude cho bước gộp của `/ghi`
    vai_gop: tuple[str, str] | None = None
    mo_nhat_ky: Callable[[], NhatKy] | None = None            # mỗi yêu cầu `/ghi` một kết nối SQLite riêng
    luat_cua: Callable[[str], LuatDuAn] = luat_cua_du_an
    cac_du_an: Callable[[], list[str]] = liet_ke_du_an
    luc: Callable[[], str] = bay_gio


def _loi(ma: int, thong_bao: str) -> JSONResponse:
    return JSONResponse({"loi": thong_bao}, status_code=ma)


def tao_app_nho(dv: DichVuNho) -> FastAPI:
    if not dv.token:
        raise ValueError("Thiếu tram-nho-token — memory service không chạy khi không có token")
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    def xac_thuc(authorization: str | None = Header(default=None)) -> None:
        gui = (authorization or "").removeprefix("Bearer ").encode()
        if not authorization or not authorization.startswith("Bearer ") or not hmac.compare_digest(
                gui, dv.token.encode()):
            raise HTTPException(401, "Thiếu hoặc sai token")

    @app.post("/nho-lai", dependencies=[Depends(xac_thuc)])
    def nho_lai_api(than: ThanNhoLai):
        try:
            ds = nho_lai(dv.kho, dv.embedder, than.truy_van, than.vung_cap, dem_dung=dv.dem_dung)
        except LoiVungCap as e:
            return _loi(422, str(e))
        except LoiEmbedder as e:
            return _loi(503, f"embedder: {e}")
        return {"ky_uc": [k.sang_dict() for k in ds]}

    @app.post("/xoa", dependencies=[Depends(xac_thuc)])
    def xoa_api(than: ThanXoa):
        """Xoá mềm theo id (§5) + sự kiện `nho.xoa`. Xoá cứng chỉ bằng lệnh riêng của Đại ca (1b-3)."""
        with dv.kho.khoa_gop:  # thứ tự khoá: khoa_gop → khoa; không xoá giữa lúc LLM đang gộp
            k = dv.kho.lay([than.id]).get(than.id)
            if k is None:
                return _loi(404, "Không có ký ức này")
            da_xoa = dv.kho.xoa_mem([k.id]) > 0
            if da_xoa:
                with closing(dv.mo_kho_sk()) as kho_sk:
                    kho_sk.ghi(du_an_cua(k.pham_vi) or "_tram", "nho.xoa", {"id": k.id, "pham_vi": k.pham_vi},
                               tac_nhan=TAC_NHAN)
            return {"da_xoa": da_xoa}

    them_tuyen_1b3(app, dv, xac_thuc)
    return app
