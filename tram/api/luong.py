"""GET /api/luong (SSE, spec 2 §7): đẩy sự kiện mới theo sau_id, báo bảng / Phê duyệt / Đội ngũ AI đổi (D2 ≤ 10 s)."""
import asyncio
import json
from contextlib import closing
from dataclasses import dataclass, field

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from tram.beads.bd import LoiBd

router = APIRouter()
NHIP_GIAY = 2
NHIP_GIU_KET_NOI = 8          # mỗi 8 nhịp (~16 s) một dòng chú thích giữ kết nối
LOAI_LAM_MOI = {"quet.xong", "quet.loi", "cot.dai_ca_sua", "cot.da_chot", "cot.tra_ve", "escalation.tra_loi",
                "cham_cot.thu_lai", "cham_cot.bo_qua", "estop.bat", "estop.tat",
                "khe.cau_dao_ngat", "khe.cau_dao_dong",                    # 2b: "Hệ cần xem" cầu dao khe
                "pr.mo", "pr.khong_xac_minh", "pr.da_merge"}               # 2d: thẻ cột 3 (PR do trạm mở)
TIEN_TO_DOI_NGU = ("khe.", "chay.", "giao.", "bao.", "tho.")          # 2b: sự kiện phần 3 → trang Đội ngũ AI tải lại


def khung(su_kien: str, du_lieu: dict, id: int | None = None) -> str:
    dong = [f"event: {su_kien}"] + ([f"id: {id}"] if id is not None else [])
    dong.append(f"data: {json.dumps(du_lieu, ensure_ascii=False)}")
    return "\n".join(dong) + "\n\n"


@dataclass
class TrangThaiLuong:
    moc: int
    phien_ban: dict[str, int] = field(default_factory=dict)


def mot_nhip(kho, bo_dem, cac_du_an: list[str], tt: TrangThaiLuong) -> list[str]:
    ra, can_bao, doi_ngu = [], False, False
    for sk in kho.sau_id(tt.moc, 200):
        ra.append(khung("su_kien", {"id": sk.id, "luc": sk.luc, "du_an": sk.du_an, "bead_id": sk.bead_id,
                                    "loai": sk.loai}, sk.id))
        tt.moc = sk.id
        doi_ngu = doi_ngu or sk.loai.startswith(TIEN_TO_DOI_NGU)
        if sk.loai in LOAI_LAM_MOI:
            can_bao = True
            if not sk.du_an.startswith("_"):
                bo_dem.danh_dau_cu(sk.du_an)
    for du_an in cac_du_an:
        try:
            bo_dem.lay(du_an)
        except LoiBd:
            continue
        pb = bo_dem.phien_ban(du_an)
        if tt.phien_ban.get(du_an) not in (None, pb):
            ra.append(khung("cong_viec_doi", {"du_an": du_an}))
            can_bao = True
        tt.phien_ban[du_an] = pb
    if can_bao:
        ra.append(khung("phe_duyet_doi", {}))
    if doi_ngu:
        ra.append(khung("doi_ngu_doi", {}))
    return ra


@router.get("/api/luong")
async def luong(request: Request) -> StreamingResponse:
    pt = request.app.state.pt
    cuoi = request.headers.get("last-event-id", "")

    async def sinh():
        # N5: đóng khi trình duyệt ngắt. run_in_threadpool (anyio) không bỏ rơi luồng khi bị huỷ: chờ luồng đọc xong
        # rồi mới tới close(); asyncio.to_thread thì đóng sqlite khi luồng kia còn dùng → segfault (bs-64w).
        with closing(pt.mo_kho()) as kho:
            moc = int(cuoi) if cuoi.isdigit() else await run_in_threadpool(kho.id_moi_nhat)
            tt, dem = TrangThaiLuong(moc=moc), 0
            while not await request.is_disconnected():
                for k in await run_in_threadpool(mot_nhip, kho, pt.bo_dem, pt.cac_du_an(), tt):
                    yield k
                dem += 1
                if dem % NHIP_GIU_KET_NOI == 0:
                    yield ": nhip\n\n"
                await asyncio.sleep(NHIP_GIAY)

    return StreamingResponse(sinh(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
