from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from tho_gia import ChayCLIGia, NguonHanMucGia
from tram.chay_cli.giao_dien import ChayCLI, KetQuaChay, ket_thuc_tu
from tram.han_muc.luat import cham_nguong_ngung, duoc_nhan
from tram.han_muc.mo_hinh import CuaSo, HanMuc, co_chua_biet, doi_dang_ke, lam_moi, ten_cua_so
from tram.han_muc.nguon import NguonHanMuc

KHE = "B/claude-1"
LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


def cs(loai, pt, *, reset="2026-10-13T05:00:00Z", doc="2026-10-13T02:41:10Z", **kw):
    return CuaSo(loai=loai, trang_thai="biet", phan_tram=pt, reset_luc=reset, doc_luc=doc, **kw)


def hm(*cua_so):
    return HanMuc(khe_id=KHE, cua_so=list(cua_so), nguon="stream")


@pytest.mark.parametrize("han_muc, uu_tien, mong", [
    (hm(cs("5h", 90.0)), 0, False),                                      # luật 1, kể cả P0
    (hm(cs("5h", 10.0), cs("tuan", 95.0)), 0, False),
    (hm(cs("5h", 10.0), cs("tuan", 80.0)), 1, True),                     # luật 2: P0–P1 vẫn nhận
    (hm(cs("5h", 10.0), cs("tuan", 80.0)), 2, False),
    (hm(cs("5h", 89.9), cs("tuan", 79.9)), 4, True),
    (hm(cs("5h", 50.0), CuaSo(loai="tuan", trang_thai="chua_biet")), 4, True),   # luật 3 (#15)
    (None, 3, True),                                                     # chưa có số đo nào
    (hm(cs("x:60m", 95.0)), 2, False),                                   # cửa sổ lạ vẫn áp luật 1
])
def test_duoc_nhan_moi_nhanh(han_muc, uu_tien, mong):
    assert duoc_nhan(han_muc, uu_tien) is mong


def test_nguong_cau_hinh_duoc_va_uu_tien_sai():
    assert duoc_nhan(hm(cs("5h", 85.0)), 2, ngung=80) is False
    assert cham_nguong_ngung(hm(cs("5h", 85.0)), ngung=80) and not cham_nguong_ngung(None)
    for sai in (-1, 5, True, "1"):
        with pytest.raises(ValueError):
            duoc_nhan(None, sai)


def test_lam_moi_qua_reset_hoac_qua_tuoi_thanh_chua_biet_khong_phai_0():
    moi = lam_moi(hm(cs("5h", 62.0, reset="2026-10-13T02:59:59Z")), KHE, LUC)
    c = {x.loai: x for x in moi.cua_so}
    assert c["5h"].trang_thai == "chua_biet" and c["5h"].phan_tram is None and c["5h"].doc_luc
    assert c["tuan"].trang_thai == "chua_biet"                          # thiếu trong số đo → chưa biết
    cu = hm(cs("5h", 62.0, reset="2026-10-14T00:00:00Z", doc="2026-10-12T20:59:00Z"))
    assert lam_moi(cu, KHE, LUC).cua_so[0].trang_thai == "chua_biet"     # quá 6 giờ
    assert lam_moi(cu, KHE, LUC, tuoi_toi_da_gio=7).cua_so[0].trang_thai == "biet"
    het = hm(cs("5h", 1.0, reset=None, het_hieu_luc="2026-10-13T03:00:00Z"))
    assert lam_moi(het, KHE, LUC).cua_so[0].trang_thai == "chua_biet"
    assert co_chua_biet(lam_moi(None, KHE, LUC)) and lam_moi(None, KHE, LUC).nguon == "chua_co"


def test_ten_cua_so_theo_thoi_luong_khong_theo_primary():
    assert ten_cua_so(300, "primary") == "5h" and ten_cua_so(10080, "secondary") == "tuan"
    assert ten_cua_so(60, "primary") == "primary:60m"


def test_doi_dang_ke():
    a = hm(cs("5h", 60.0), cs("tuan", 10.0))
    assert doi_dang_ke(None, a)
    assert not doi_dang_ke(a, hm(cs("5h", 64.9), cs("tuan", 10.0)))
    assert doi_dang_ke(a, hm(cs("5h", 65.0), cs("tuan", 10.0)))
    assert doi_dang_ke(a, hm(cs("5h", 60.0, reset="2026-10-13T10:00:00Z"), cs("tuan", 10.0)))
    assert doi_dang_ke(a, hm(cs("5h", 60.0), CuaSo(loai="tuan", trang_thai="chua_biet")))
    assert doi_dang_ke(a, hm(cs("5h", 60.0)))


@pytest.mark.parametrize("sai", [
    {"loai": "5h", "trang_thai": "biet", "phan_tram": None, "doc_luc": "2026-10-13T00:00:00Z"},
    {"loai": "5h", "trang_thai": "biet", "phan_tram": 101, "doc_luc": "2026-10-13T00:00:00Z"},
    {"loai": "5h", "trang_thai": "biet", "phan_tram": 1, "doc_luc": "2026-10-13 00:00"},
    {"loai": "5h", "trang_thai": "biet", "phan_tram": 1, "doc_luc": "2026-10-13T00:00:00Z", "la": 1},
])
def test_cua_so_sai_dang(sai):
    with pytest.raises(ValidationError):
        CuaSo.model_validate(sai)


def test_han_muc_loai_trung_va_khe_sai():
    with pytest.raises(ValidationError):
        hm(cs("5h", 1.0), cs("5h", 2.0))
    with pytest.raises(ValidationError):
        HanMuc(khe_id="B claude", cua_so=[])


@pytest.mark.parametrize("kq, mong", [
    (KetQuaChay(0, True, False, False, False), "xong"),
    (KetQuaChay(1, True, False, False, False), "loi"),
    (KetQuaChay(1, False, False, False, False), "loi_he"),           # thoát ≠ 0, không có assistant
    (KetQuaChay(0, False, False, True, False), "loi_he"),            # chưa đăng nhập
    (KetQuaChay(1, True, True, False, False), "het_han_muc"),
    (KetQuaChay(None, True, False, False, True), "dung"),
])
def test_ket_thuc_tu(kq, mong):
    assert ket_thuc_tu(kq) == mong


def test_ban_gia_dung_giao_dien():
    assert isinstance(NguonHanMucGia(), NguonHanMuc) and isinstance(ChayCLIGia(), ChayCLI)
    h = NguonHanMucGia().doc_dong({"gia_han_muc": {"5h": 91.0}, "doc_luc": "2026-10-13T02:59:00Z"},
                                  khe_id=KHE, bay_gio=LUC)
    assert not duoc_nhan(lam_moi(h, KHE, LUC), 0)
