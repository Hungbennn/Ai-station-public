"""`POST /api/ghep-may {ma}` (spec 3 §9.2): Mac thợ từ xa đổi mã ghép dùng một lần lấy token máy. KHÔNG nằm trong
nhóm `/api/tho/*` (chưa có token máy để gửi) — bằng chứng duy nhất là mã ghép. Phản hồi `Cache-Control: no-store`;
lỗi không bao giờ nói mã thuộc máy nào. Không dùng danh tính Tailscale (Mac thợ là thiết bị gắn tag)."""
from contextlib import closing

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tram.phieu.ma_ghep import GhepBiKhoa, MaGhepSai, doi_ma_ghep

router = APIRouter()


class ThanGhep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ma: str = Field(min_length=1, max_length=64)


@router.post("/api/ghep-may")
def ghep_may(than: ThanGhep, request: Request):
    pt = request.app.state.pt
    if pt.mo_kho_phieu is None:
        return JSONResponse({"loi": "Kho phiếu chưa bật"}, status_code=503)
    with closing(pt.mo_kho_phieu()) as kho:
        try:
            may_id, token = doi_ma_ghep(kho, than.ma, luc=pt.dong_ho())
        except GhepBiKhoa as e:
            return JSONResponse({"loi": str(e)}, status_code=429)
        except MaGhepSai as e:
            return JSONResponse({"loi": str(e)}, status_code=403)
    return JSONResponse({"may_id": may_id, "token": token}, headers={"Cache-Control": "no-store"})
