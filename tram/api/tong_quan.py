"""Trang Tổng quan (D17, D38 Q12): `GET /api/tong-quan` gom dữ liệu bằng CHÍNH các hàm route có sẵn (như
`/api/van-phong` gọi `phe_duyet` — 2c G6), nên số trên Tổng quan luôn khớp từng trang. Công khai như
`/api/phe-duyet`: dịch vụ launchd chỉ trả boolean (G24), sự kiện `nho.*` che mô tả khi không phải Đại ca. Chỉ đọc —
không gọi ccusage, không chạy lệnh có tác dụng phụ. (`GET /api/su-kien/gan-day` đã bỏ — bs-2bd.1.6.)"""
from contextlib import closing

from fastapi import APIRouter, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau
from tram.api.doi_ngu import r_doi_ngu
from tram.api.tuyen_doc import du_an, phe_duyet
from tram.beads.bd import LoiBd
from tram.cham_cot.ghi import GIO_VN
from tram.chu import estop
from tram.suy import he_thong
from tram.suy.moi_xong import moi_xong
from tram.suy.su_kien_gan_day import gan_day
from tram.usage.su_kien import doc_dong_usage, tong_hop

router = APIRouter()
SO_SU_KIEN = 18                                   # mockup: "18 dòng mới nhất"
TRUONG_DICH_VU = ("nhan", "viec", "da_cai", "dang_chay")


def _moi_xong(pt, ten: str) -> dict | None:
    try:
        return moi_xong(pt.bo_dem.lay(ten))
    except LoiBd:                                 # lỗi đọc đã nằm ở `loi_doc` của dự án
        return None


def _usage_hom_nay(pt) -> dict:
    nay = pt.dong_ho().astimezone(GIO_VN).date()
    dong = []
    if pt.mo_kho_phieu is not None:
        with closing(pt.mo_kho_phieu()) as kho:
            dong = doc_dong_usage(kho.db, nay, nay)
    th = tong_hop(dong, pt.usage.gia)
    return {"theo_nguon": th["theo_nguon"], "theo_ngay": th["theo_ngay"]}


@router.get("/api/tong-quan")
def r_tong_quan(request: Request) -> dict:
    pt = request.app.state.pt
    dn = r_doi_ngu(request, du_an="", so_ngay=30)
    with closing(pt.mo_kho()) as kho:
        sk = gan_day(kho, SO_SU_KIEN, la_dai_ca=la_dai_ca_yeu_cau(request))
    return {"phe_duyet": phe_duyet(request),
            "du_an": [{**d, "moi_xong": _moi_xong(pt, d["ten"])} for d in du_an(request)["du_an"]],
            "tram": {"estop": estop.dang_bat(), "la_dai_ca": la_dai_ca_yeu_cau(request)},
            "doi_ngu": {"bat": dn["bat"], "khe": dn["khe"]}, "usage": _usage_hom_nay(pt),
            "dich_vu": [{k: d[k] for k in TRUONG_DICH_VU} for d in he_thong.doc_he_thong().dich_vu()],
            "su_kien": sk, "doc_luc": pt.dong_ho().isoformat()}
