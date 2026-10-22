"""`POST /api/dieu-phoi/nhip` (spec 2 §5.5; plan 2e G3–G13, G23): hook phiên điều phối trên máy A báo nhịp → sự kiện
`dieu_phoi.nhip` của dự án `_tram`. ĐƯỜNG GHI HẸP: chỉ ghi đúng loại sự kiện này; không chạm beads, phiếu, khe, memory.

Kiểm theo thứ tự, rẻ trước: kênh ghi (`cach_ly.kenh_ghi`, 403) → tần suất (429) → danh tính Tailscale + `X-Tram` +
`Origin` (`yeu_cau_danh_tinh` y hệt API ghi dashboard, 403) → mã điều phối (`Authorization: Bearer`, so sha256 với
`dieu_phoi_ma_sha256` — mã RIÊNG theo D24, không phải mã Đại ca; header Tailscale giả được từ TCP localhost, mã thì
không; 401) → thân ≤ 512 byte (413) đúng lược đồ (422). Mã điều phối KHÔNG mở route nào khác: API ghi dashboard bỏ
qua `Authorization`; memory service chỉ so với `ma_dai_ca_sha256`. Thông báo lỗi không chứa mã.
Gộp ghi nguyên tử (review đợt 4 F10): `BEGIN IMMEDIATE` trước khi đọc, nên hai lời gọi song song không cùng ghi."""
import hashlib
import hmac
import time
from collections import deque
from contextlib import closing
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tram.api.bao_mat import yeu_cau_danh_tinh
from tram.api.kenh_ghi import kenh_hop_le
from tram.chu.ma_dieu_phoi import doc_bam
from tram.suy.dieu_phoi import DU_AN_HE, LOAI, TAC_NHAN, can_ghi
from tram.suy.kho_nhip import doc_nhip

router = APIRouter()
TOI_DA_BYTE = 512
TOI_DA_LOI_GOI, CUA_SO_GIAY = 30, 60.0


class ThanNhipDieuPhoi(BaseModel):
    model_config = ConfigDict(extra="forbid")
    su_kien: Literal["SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"]
    phien: str = Field(pattern=r"^[0-9a-f]{16}$")


class GioiHan:
    """Cửa sổ trượt trong bộ nhớ tiến trình tram-api (mất khi khởi động lại — chấp nhận, G10)."""

    def __init__(self, toi_da: int = TOI_DA_LOI_GOI, cua_so: float = CUA_SO_GIAY, dong_ho=time.monotonic):
        self.toi_da, self.cua_so, self.dong_ho, self.moc = toi_da, cua_so, dong_ho, deque()

    def cho_phep(self) -> bool:
        bay_gio = self.dong_ho()
        while self.moc and bay_gio - self.moc[0] >= self.cua_so:
            self.moc.popleft()
        if len(self.moc) >= self.toi_da:
            return False
        self.moc.append(bay_gio)
        return True


def gioi_han(request: Request) -> GioiHan:
    gh = getattr(request.app.state, "gioi_han_dieu_phoi", None)
    if gh is None:
        gh = request.app.state.gioi_han_dieu_phoi = GioiHan()
    return gh


def kiem_ma_dieu_phoi(request: Request) -> None:
    gt = request.headers.getlist("authorization")
    ma = gt[0].removeprefix("Bearer ") if len(gt) == 1 and gt[0].startswith("Bearer ") else ""
    bam = doc_bam()                                  # đọc mỗi lời gọi: `tram chu dat-ma-dieu-phoi` có hiệu lực ngay
    gui = hashlib.sha256(ma.encode()).hexdigest()
    if not ma or not bam or not hmac.compare_digest(gui.encode(), bam.encode()):
        raise HTTPException(401, "Thiếu hoặc sai mã điều phối (hoặc trạm chưa đặt mã — tram chu dat-ma-dieu-phoi)")


async def doc_than(request: Request) -> ThanNhipDieuPhoi:
    cl = request.headers.get("content-length")
    if cl is not None and (not cl.isdigit() or int(cl) > TOI_DA_BYTE):
        raise HTTPException(413, f"Thân quá {TOI_DA_BYTE} byte")
    than = b""
    async for phan in request.stream():
        than += phan
        if len(than) > TOI_DA_BYTE:
            raise HTTPException(413, f"Thân quá {TOI_DA_BYTE} byte")
    try:
        return ThanNhipDieuPhoi.model_validate_json(than)
    except ValidationError:
        raise HTTPException(422, "Thân phải là {su_kien, phien} đúng dạng") from None


def ghi_nhip(pt, than: ThanNhipDieuPhoi) -> bool:
    """Đọc + quyết + ghi trong MỘT giao dịch ghi (`BEGIN IMMEDIATE`): lời gọi thứ hai chờ khoá (busy_timeout của
    `mo_ket_noi`) rồi mới đọc, nên thấy nhịp vừa ghi. `KhoSuKien.ghi` commit giao dịch này; nhánh không ghi rollback."""
    with closing(pt.mo_kho()) as kho:
        kho._db.execute("BEGIN IMMEDIATE")
        try:
            luc = pt.dong_ho()
            if not can_ghi(doc_nhip(kho, luc), than.phien, than.su_kien, luc):
                return False
            kho.ghi(DU_AN_HE, LOAI, {"su_kien": than.su_kien, "phien": than.phien}, tac_nhan=TAC_NHAN)
            return True
        finally:
            if kho._db.in_transaction:
                kho._db.rollback()


@router.post("/api/dieu-phoi/nhip")
async def nhip_dieu_phoi(request: Request) -> dict:
    if not kenh_hop_le(request):
        raise HTTPException(403, "API ghi chỉ nhận qua kênh đã xác thực (cach_ly.kenh_ghi)")
    if not gioi_han(request).cho_phep():
        raise HTTPException(429, "Quá nhiều nhịp — thử lại sau")
    yeu_cau_danh_tinh(request)
    await run_in_threadpool(kiem_ma_dieu_phoi, request)
    than = await doc_than(request)
    return {"ghi": await run_in_threadpool(ghi_nhip, request.app.state.pt, than)}
