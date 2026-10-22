"""D138/D140: TM/TC giữ ledger nghiệp vụ; phân mức cài đặt dưới khoá thao tác."""
from fastapi import Depends, HTTPException, Request
from tram.api.passkey_phu_thuoc import can_phien_passkey, dich_vu, kiem_r, rang_yeu_cau
from tram.tu_dong.cai_dat import TRUONG_LENH


async def can_p(request: Request, _=Depends(can_phien_passkey)):
    await rang_yeu_cau(request)


async def quyen_cai_dat(request: Request, _=Depends(can_p)):
    than = await request.json()  # Đường thật + toàn thân, kể cả mã và phiên bản kỳ vọng.

    def kiem(cu, moi):
        if (moi.tu_deploy and not cu.tu_deploy) or any(
                getattr(cu, t) != getattr(moi, t) for t in TRUONG_LENH):
            kiem_r(request, than)
    return kiem


def la_chu(request: Request):
    try:
        dich_vu(request)
        return True
    except HTTPException:
        return False
