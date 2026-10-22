"""`/api/tho/*` thêm ở lát 3a-2 (spec 3 §6.4, §7.1) — cùng xác thực token máy với `tram/api/tho.py`:
- `POST /api/tho/da-push {khe_id, giao_id, luot, commit, ref_tam, request_id}` → công bố (trả `{cong_bo, commit?, ref?,
  ly_do?}`; 503 `{ly_do: chua-chot-phuong-an | chua-co-kho-tram}`; 422 `{ly_do: ref-tam-sai}`; lỗi chung như tho.py);
- `POST /api/tho/da-dong {bead: [{du_an, bead_id}]}` → `{dong: [...]}` các bead đã có `bead.dong` (thợ dọn worktree);
- `GET /api/tho/kiem-am` → `{dai_ca_login, may_b, db_nghiep_vu}` (D54): đích của hai thăm dò khe trong `tram tho kiem`,
  lấy từ CHÍNH cấu hình trạm dùng để kiểm ghi (login Đại ca đầu tiên, `ten_may_b` cho Origin) và `cach_ly.db_nghiep_vu`;
  503 `{ly_do: cach-ly-sai}`. Không chứa bí mật.
Cấu hình công bố đọc mỗi yêu cầu từ `~/.tram/cau-hinh.yaml` (`app.state.cong_bo` thay được trong test)."""
from contextlib import closing

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tram.api.tho import _chay, may_cua_yeu_cau
from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
from tram.cau_hinh.cong_bo import nap_cau_hinh_cong_bo
from tram.cong_bo.da_push import ChuaCongBoDuoc, RefTamSai, ThanDaPush, nhan_da_push
from tram.cong_bo.nguon import chon_nguon

router = APIRouter(prefix="/api/tho", dependencies=[Depends(may_cua_yeu_cau)])


class BeadCuaTho(BaseModel):
    model_config = ConfigDict(extra="forbid")
    du_an: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    bead_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class ThanDaDong(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bead: list[BeadCuaTho] = Field(max_length=200)


def cong_bo_cua(request: Request) -> tuple:
    """(cấu hình, nguồn, kho_cua) — `kho_cua` mặc định là kho kiểm của phần 4 (`~/.tram/kho-kiem/<dự án>`)."""
    if (gia := getattr(request.app.state, "cong_bo", None)) is not None:
        return gia
    from tram.giao_viec.git_kiem import kho_kiem
    cb = nap_cau_hinh_cong_bo()
    return cb, chon_nguon(cb), kho_kiem


@router.post("/da-push")
def da_push(than: ThanDaPush, request: Request, may_id: str = Depends(may_cua_yeu_cau)):
    pt = request.app.state.pt
    cb, nguon, kho_cua = cong_bo_cua(request)
    try:
        with closing(pt.mo_kho_phieu()) as kho:
            return _chay(lambda: nhan_da_push(kho, may_id, than, bay_gio=pt.dong_ho(), cb=cb, nguon=nguon,
                                              kho_cua=kho_cua))
    except ChuaCongBoDuoc as e:
        return JSONResponse({"ly_do": str(e)}, status_code=503)
    except RefTamSai:
        return JSONResponse({"ly_do": "ref-tam-sai"}, status_code=422)


@router.post("/da-dong")
def da_dong(than: ThanDaDong, request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho_phieu()) as kho:
        dong = [b.model_dump() for b in than.bead if kho.db.execute(
            "SELECT 1 FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = 'bead.dong' LIMIT 1",
            (b.du_an, b.bead_id)).fetchone()]
    return {"dong": dong}


@router.get("/kiem-am")
def kiem_am(request: Request):
    ch = request.app.state.pt.cau_hinh
    try:
        db = list(nap_cau_hinh_cach_ly().db_nghiep_vu)
    except ValueError:
        return JSONResponse({"ly_do": "cach-ly-sai"}, status_code=503)
    return {"dai_ca_login": ch.dai_ca_logins[0] if ch.dai_ca_logins else None, "may_b": ch.ten_may_b,
            "db_nghiep_vu": db}
