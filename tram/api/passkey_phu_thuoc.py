"""Cửa người TCP; danh tính mạng là điều kiện phụ, không phải bằng chứng chạm."""
from fastapi import HTTPException, Request
from tram.api.bao_mat import kiem_ghi, HEADER_DANH_TINH
from tram.duong_dan import tram_home
from tram.passkey.chinh_sach import TUYEN, rang_buoc
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import TuChoi
from tram.passkey.thiet_bi import can_r

COOKIE = '__Host-tram-phien'


def dich_vu(request: Request):
    ch = request.app.state.pt.cau_hinh
    hs = request.headers.getlist(HEADER_DANH_TINH)
    if len(hs) != 1 or len(ch.dai_ca_logins) != 1 or hs[0] != ch.dai_ca_logins[0]:
        raise HTTPException(403, 'Danh tính không hợp lệ')
    headers = dict(request.headers)
    if request.method == "GET":
        headers = {**headers, "origin": f"https://{ch.ten_may_b}", "x-tram": "1"}
    loi = kiem_ghi(headers, ch)
    if loi:
        raise HTTPException(403, loi)
    return DichVu(getattr(request.app.state, 'passkey_path', tram_home()/'passkey.db'), hs[0], ch.ten_may_b)


def cookie(request):
    return request.cookies.get(COOKIE, '')


def can_phien_passkey(request: Request):
    try:
        return dich_vu(request).can_phien(cookie(request))
    except TuChoi:
        raise HTTPException(403, 'Cần phiên passkey') from None


def can_ghi(request: Request):
    dv = dich_vu(request)
    path = request.scope['route'].path
    muc = TUYEN.get(path)
    if muc not in ('N', 'P'):
        raise HTTPException(403, 'Tuyến chưa được cấp quyền người')
    if path in ('/api/chu/estop', '/api/feature/yeu-cau/xem'):
        return
    try:
        if muc == 'P':
            dv.can_phien(cookie(request))
        elif not dv.trang_thai(cookie(request))['thiet_bi']:
            raise TuChoi('Cần đăng ký passkey')
    except TuChoi as e:
        raise HTTPException(403, str(e)) from None


async def luon_cham_lai(request: Request):
    """TM/TC: cùng mã/nội dung cho retry; ledger nghiệp vụ vẫn phải chống thực thi lần hai."""
    than = await request.json()
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(kiem_r, request, than)


def kiem_r(request, than):
    dv = dich_vu(request)
    try:
        rang = rang_buoc(request.url.path, than)
        with dv.mo() as (db, u, luc):
            _, q = can_r(db, u, cookie(request), request.headers.get('x-tram-xac-nhan', ''), rang, luc)
            return {'nguoi': u['id'].hex(), 'rang': rang, 'lap_lai': bool(q['dung'])}
    except (TuChoi, ValueError):
        raise HTTPException(403, 'Cần chạm lại cho thao tác này') from None


async def rang_yeu_cau(request: Request):
    import json
    from tram.passkey.thao_tac import rang_ma, XungDotMa
    if request.scope['route'].path in ('/api/chu/estop', '/api/feature/yeu-cau/xem', '/api/feature/yeu-cau'):
        return
    raw = await request.body()
    from tram.api.passkey_http import han_than
    limit = han_than(request.url.path)
    if limit is not None and len(raw) > limit:
        raise HTTPException(413, 'Yêu cầu quá lớn')
    from starlette.concurrency import run_in_threadpool
    await run_in_threadpool(kiem_rang, request, raw)


def kiem_rang(request, raw):
    import json
    from tram.passkey.thao_tac import rang_ma, XungDotMa
    try:
        than = json.loads(raw)
        if not isinstance(than, dict):
            raise ValueError()
        with dich_vu(request).mo() as (db, u, _):
            rang_ma(db, u, request.url.path, than)
    except XungDotMa:
        raise HTTPException(409, 'Mã thao tác đã dùng cho nội dung khác') from None
    except TuChoi:
        raise HTTPException(403, 'Không có quyền') from None
    except ValueError:
        raise HTTPException(422, 'Yêu cầu không hợp lệ') from None
