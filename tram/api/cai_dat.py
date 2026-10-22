"""Trang Cài đặt (D19, D38/Q13; khảo sát §1.10 A1, A2): `GET /api/cai-dat`, `GET /api/san-sang` — CHỈ Đại ca, chỉ đọc.

Quyền giống `/api/nho` (`la_dai_ca_yeu_cau`: đúng một `Tailscale-User-Login` thuộc `dai_ca_logins`, đúng kênh) →
khác thì 403. Không ghi, không `ma_thao_tac`, không chạy lệnh có tác dụng phụ. Route `def` đồng bộ (threadpool).
Đăng ký router riêng trong app.py ở Task 6; Task 8 giữ đăng ký này khi thêm tong_quan.router."""
from fastapi import APIRouter, Depends, HTTPException, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau
from tram.suy import he_thong, san_sang
from tram.suy.cai_dat import gom_cai_dat


def yeu_cau_dai_ca(request: Request) -> None:
    """Như `tuyen_nho.yeu_cau_dai_ca`, câu 403 riêng cho trang Cài đặt."""
    if not la_dai_ca_yeu_cau(request):
        raise HTTPException(status_code=403, detail="Cài đặt chỉ Đại ca xem được (cần danh tính Tailscale của Đại ca)")


router = APIRouter(dependencies=[Depends(yeu_cau_dai_ca)])


@router.get("/api/cai-dat")
def r_cai_dat(request: Request) -> dict:
    pt = request.app.state.pt
    return gom_cai_dat(pt.cau_hinh, pt.usage, pt.cac_du_an, he_thong.doc_he_thong())


@router.get("/api/san-sang")
def r_san_sang() -> dict:
    return san_sang.CHUNG.lay(he_thong.doc_he_thong())
