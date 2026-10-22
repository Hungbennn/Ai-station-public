"""`GET /api/van-phong` (spec 2 §5.5, §7 lát 2c): phòng + nhân vật + trạng thái đã suy, chỉ đọc.

Số việc chờ Đại ca và "Hệ cần xem" lấy bằng CHÍNH route `/api/phe-duyet` (`tuyen_doc.phe_duyet`) — badge Phòng giám
đốc luôn khớp trang Phê duyệt, kể cả khi phần 4 thêm hàng mới (plan 2c G6). Nhân vật suy từ `trang_thai_khe`."""
from contextlib import closing

from fastapi import APIRouter, Request

from tram.api import dieu_phoi
from tram.api.tuyen_doc import phe_duyet
from tram.chu import estop
from tram.phieu.trang_thai import trang_thai_khe
from tram.suy.dieu_phoi import den_dieu_phoi
from tram.suy.kho_nhip import doc_nhip
from tram.suy.nhan_vat import nhan_vat
from tram.suy.van_phong import cac_phong, suc_khoe

router = APIRouter()
router.include_router(dieu_phoi.router)          # plan 2e: POST /api/dieu-phoi/nhip — đăng ký qua đây, không sửa app.py


@router.get("/api/van-phong")
def r_van_phong(request: Request) -> dict:
    pt = request.app.state.pt
    cac_du_an = pt.cac_du_an()
    pd = phe_duyet(request)
    nv = []
    if pt.mo_kho_phieu is not None:
        with closing(pt.mo_kho_phieu()) as kho:
            nv = nhan_vat(kho, trang_thai_khe(kho, bay_gio=pt.dong_ho(), ch=pt.cau_hinh), cac_du_an)
    sk = suc_khoe(estop_bat=estop.dang_bat(), muc=pd["muc"], loi_doc=pd["loi"], nhan_vat=nv)
    with closing(pt.mo_kho()) as kho:                       # plan 2e: đèn Điều phối từ nhịp hook máy A
        luc = pt.dong_ho()
        dp = den_dieu_phoi(doc_nhip(kho, luc), luc)
    return {"phong": cac_phong(cac_du_an, so_cho=pd["so"], suc_khoe=sk, dieu_phoi=dp), "nhan_vat": nv,
            "kho_phieu": pt.mo_kho_phieu is not None}
