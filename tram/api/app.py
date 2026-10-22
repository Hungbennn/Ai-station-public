"""tram-api (spec 2 §3, §7). Chỉ chạy qua `tram api` — nghe 127.0.0.1 (tram/cli_dich_vu.py)."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
from tram.api import cai_dat, tong_quan, tuyen_tu_cap_nhat, tuyen_tu_dong, tuyen_yeu_cau, van_phong
from tram.api import tuyen_deploy
from tram.api.bao_mat import them_header_an_toan
from tram.api.passkey import router as passkey_router
from tram.api.phu_thuoc import PhuThuocApi
from tram.api.tuyen_giao import router as tuyen_giao
from tram.beads.bd import KhongThayBead, LoiBd
from tram.nho.khach import LoiNhoKhach
from tram.suy.lam_sach import lam_sach
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay, XungDot

MA_LOI = {XungDot: 409, KhongHopLe: 422, ChuaHoTro: 501, KhongThay: 404, KhongThayBead: 404, LoiBd: 502,
          LoiNhoKhach: 503}
CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router,
             noi_bo.router, doi_ngu.router, usage.router, tho_them.router, ghep.router)
CAC_TUYEN += (passkey_router,)
CAC_TUYEN += (tuyen_deploy.router,)
CAC_TUYEN += (tuyen_giao,)                     # 4a-2: GET /api/giao-viec
CAC_TUYEN += (van_phong.router,)               # 2c: GET /api/van-phong
CAC_TUYEN += (cai_dat.router,)                 # 2f: GET /api/cai-dat, /api/san-sang (chỉ Đại ca)
CAC_TUYEN += (tong_quan.router,)               # 2f: GET /api/tong-quan
CAC_TUYEN += (tuyen_yeu_cau.router,)           # 4d: POST /api/feature/yeu-cau[/xem] — máy A gửi, B tạo feature
CAC_TUYEN += (tuyen_tu_dong.doc, tuyen_tu_dong.ghi)   # TM-1: /api/tu-dong, /api/du-an/{ten}/tu-dong[/…]
CAC_TUYEN += (tuyen_tu_cap_nhat.doc, tuyen_tu_cap_nhat.ghi)   # TC: /api/du-an/{ten}/tu-cap-nhat, …/bead/{id}/de-nghi


def _xu_ly(ma: int):
    async def xu_ly(request: Request, loi: Exception) -> JSONResponse:
        return JSONResponse({"loi": lam_sach(str(loi), 500)}, status_code=ma)
    return xu_ly


def tao_app(pt: PhuThuocApi, *, cong: int = 7700) -> FastAPI:
    app = FastAPI(title="tram-api", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.pt = pt
    from tram.api.passkey_http import GioiHanThan
    app.add_middleware(GioiHanThan)
    them_header_an_toan(app, pt.cau_hinh, cong=cong)          # CSP + Host (spec 2 §4 mục 6)
    for loai, ma in MA_LOI.items():
        app.add_exception_handler(loai, _xu_ly(ma))
    for r in CAC_TUYEN:
        app.include_router(r)
    if pt.thu_muc_tinh is not None:      # mount sau cùng: /api/* khớp trước
        app.mount("/", StaticFiles(directory=pt.thu_muc_tinh, html=True), name="tinh")
    return app
