"""Giao thức WebAuthn: không đưa lỗi schema/thư viện và dữ liệu ceremony ra log."""
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from tram.api.passkey_phu_thuoc import COOKIE, cookie, dich_vu
from tram.passkey.chinh_sach import rang_buoc
from tram.passkey.kho import TuChoi
from tram.passkey.thao_tac import XungDotMa
from starlette.concurrency import run_in_threadpool

router = APIRouter()


async def than_kin(request):
    raw = b''
    async for chunk in request.stream():
        raw += chunk
        if len(raw) > 65536:
            raise HTTPException(413, 'Yêu cầu quá lớn')
    try:
        b = json.loads(raw)
        if not isinstance(b, dict):
            raise ValueError()
        return b
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'Yêu cầu không hợp lệ') from None


def tra(b):
    r = JSONResponse({k:v for k,v in b.items() if k != 'cookie'}, headers={'Cache-Control':'no-store'})
    if 'cookie' in b:
        r.set_cookie(COOKIE, b['cookie'], max_age=28800, path='/', secure=True, httponly=True, samesite='strict')
    return r


@router.get('/api/passkey/trang-thai')
def trang_thai(request: Request):
    return tra(dich_vu(request).trang_thai(cookie(request)))


@router.post('/api/passkey/{viec}')
async def ghi(viec: str, request: Request):
    dv = dich_vu(request)
    b = await than_kin(request)
    return await run_in_threadpool(thuc_hien, viec, request, dv, b)


def thuc_hien(viec, request, dv, b):
    try:
        if viec == 'bat-dau':
            loai = b['loai']
            rang = rang_buoc(b['duong'], b['than']) if loai == 'r' else ''
            out = dv.bat_dau(loai, cookie=cookie(request), ma=b.get('ma',''), rang=rang)
        elif viec == 'ket-thuc':
            out = dv.ket_thuc(b['id'], b['credential'], b.get('ten','Thiết bị'))
        elif viec in ('moi', 'thu-hoi'):
            than = b['than']
            out = dv.quan_ly(cookie(request), b['quyen'], viec, than)
        else:
            raise HTTPException(404, 'Không có thao tác')
        return tra(out)
    except XungDotMa:
        return JSONResponse({'loi':'Mã thao tác đã dùng cho nội dung khác'}, status_code=409,
                            headers={'Cache-Control':'no-store'})
    except TuChoi as e:
        return JSONResponse({'loi':str(e)}, status_code=429 if str(e).startswith('Quá nhiều') else 403,
                            headers={'Cache-Control':'no-store'})
    except (KeyError, TypeError, ValueError, AttributeError):
        return JSONResponse({'loi':'Yêu cầu không hợp lệ'}, status_code=422, headers={'Cache-Control':'no-store'})
