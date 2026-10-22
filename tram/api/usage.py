"""`GET /api/usage?so_ngay=14` (spec 2 §5.4, §7): token + chi phí theo ngày / tuần / khe / dự án từ sự kiện của
trạm, và theo ngày từ `ccusage --json` (toàn bộ Claude Code của tài khoản trạm trên máy B — CHỜ CHẠY THẬT,
plan 2b G6). Chỉ đọc; không nội dung nghiệp vụ."""
from contextlib import closing
from dataclasses import asdict
from datetime import timedelta

from fastapi import APIRouter, Request

from tram.cham_cot.ghi import GIO_VN
from tram.thao_tac.loi import KhongHopLe
from tram.usage.ccusage import KetQuaCcusage
from tram.usage.su_kien import doc_dong_usage, tong_hop

router = APIRouter()
SO_NGAY_TOI_DA = 92


@router.get("/api/usage")
def r_usage(request: Request, so_ngay: int = 14) -> dict:
    if not 1 <= so_ngay <= SO_NGAY_TOI_DA:
        raise KhongHopLe(f"so_ngay phải trong 1–{SO_NGAY_TOI_DA}")
    pt = request.app.state.pt
    den = pt.dong_ho().astimezone(GIO_VN).date()
    tu = den - timedelta(days=so_ngay - 1)
    dong = []
    if pt.mo_kho_phieu is not None:
        with closing(pt.mo_kho_phieu()) as kho:
            dong = doc_dong_usage(kho.db, tu, den)
    cc = pt.doc_ccusage(tu, den) if pt.doc_ccusage is not None else KetQuaCcusage("chua_cau_hinh")
    return {"tu": tu.isoformat(), "den": den.isoformat(), **tong_hop(dong, pt.usage.gia),
            "co_bang_gia": bool(pt.usage.gia), "ccusage": {**asdict(cc), "theo_ngay": list(cc.theo_ngay)}}
