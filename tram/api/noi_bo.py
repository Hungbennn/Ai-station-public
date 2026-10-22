"""`GET /api/noi-bo/phieu/{giao_id}` (spec 3 §10) cho memory 1b-2: `{du_an, vai, ma_giao, con_hieu_luc}` — trả cả khi
phiếu đã hết hiệu lực, `ma_giao` CHỈ khi còn hiệu lực. Chỉ nhận TOKEN NỘI BỘ (`tram-noi-bo-token`, Keychain của tài
khoản trạm — khác token máy thợ). Chưa có token (chưa cài 1b-2) → mọi lời gọi 401."""
import hmac
import re
from collections.abc import Callable
from contextlib import closing

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from tram.keychain import doc_muc

KEYCHAIN_NOI_BO = "tram-noi-bo-token"
GIAO_ID_RE = re.compile(r"g-\d{8}-\d{4,}")
router = APIRouter()


def doc_token_noi_bo(*, chay=None) -> str | None:
    return doc_muc(KEYCHAIN_NOI_BO, chay=chay)


def doc_mot_lan(doc: Callable[[], str | None] = doc_token_noi_bo) -> Callable[[], str | None]:
    """Đọc Keychain lần đầu có yêu cầu, rồi giữ trong bộ nhớ tiến trình (khởi động tram-api không đụng Keychain)."""
    nho: list[str | None] = []

    def lay() -> str | None:
        if not nho:
            nho.append(doc())
        return nho[0]
    return lay


@router.get("/api/noi-bo/phieu/{giao_id}")
def phieu_noi_bo(giao_id: str, request: Request):
    pt = request.app.state.pt
    gia_tri = request.headers.getlist("authorization")
    gui = gia_tri[0].removeprefix("Bearer ") if len(gia_tri) == 1 and gia_tri[0].startswith("Bearer ") else ""
    token = pt.doc_token_noi_bo()
    if not token or not gui or not hmac.compare_digest(gui.encode(), token.encode()):
        raise HTTPException(401, "Thiếu hoặc sai token nội bộ")
    if not GIAO_ID_RE.fullmatch(giao_id) or pt.mo_kho_phieu is None:
        raise HTTPException(404, "Không có phiếu này")
    with closing(pt.mo_kho_phieu()) as kho:
        ra = kho.phieu_theo_giao_id(giao_id)
    if ra is None:
        raise HTTPException(404, "Không có phiếu này")
    return JSONResponse(ra, headers={"Cache-Control": "no-store"})
