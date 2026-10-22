from datetime import datetime, timedelta, timezone

import pytest

from nho_gia import EmbedderGia, ky_uc
from tram.nho.embed import LoiEmbedder
from tram.nho.kho import KhoKyUc
from tram.nho.nho_lai import BoDemDung, KyUcTra, nho_lai
from tram.nho.pham_vi import LoiVungCap

BAY_GIO = datetime(2026, 10, 13, tzinfo=timezone.utc)
VUNG_X = ["/du-an/x", "/vai/coder", "/chung"]


@pytest.fixture
def moi_truong(tmp_path):
    e = EmbedderGia()
    return KhoKyUc(tmp_path / "lancedb", so_chieu=e.so_chieu), e


def them(kho, e, id, pham_vi, giong=None, **kw):
    kho.them(ky_uc(id, pham_vi, vector=e.embed([giong or id])[0], **kw))


def test_vung_cap_sai_tu_choi_truoc_khi_embed(moi_truong):
    kho, e = moi_truong
    for vung in ([], ["/"], ["/du-an"], None):
        with pytest.raises(LoiVungCap):
            nho_lai(kho, e, "q", vung, bay_gio=BAY_GIO)
    assert e.goi == []


def test_100_ky_uc_y_va_3_ky_uc_x_recall_x_du_3(moi_truong):
    kho, e = moi_truong
    for i in range(100):
        them(kho, e, f"y-{i}", "/du-an/y/cach-lam", giong="truy vấn")
    for i in range(3):
        them(kho, e, f"x-{i}", "/du-an/x/nghiep-vu")
    kq = nho_lai(kho, e, "truy vấn", VUNG_X, bay_gio=BAY_GIO)
    assert sorted(k.id for k in kq) == ["x-0", "x-1", "x-2"]
    assert all(isinstance(k, KyUcTra) and set(k.sang_dict()) == {"id", "noi_dung", "pham_vi"} for k in kq)


def test_ung_vien_rieng_tung_nhom_va_khong_bu_cheo(moi_truong):
    kho, e = moi_truong
    for i in range(60):                                       # 60 ký ức dự án rất giống truy vấn
        them(kho, e, f"x-{i:02d}", "/du-an/x/cach-lam", giong="truy vấn")
    them(kho, e, "c-1", "/chung")                             # khác hẳn truy vấn vẫn lọt nhóm chung
    them(kho, e, "v-khac", "/vai/qc")                         # vai khác không được cấp
    kq = nho_lai(kho, e, "truy vấn", VUNG_X, bay_gio=BAY_GIO)
    assert [k.pham_vi for k in kq] == ["/du-an/x/cach-lam"] * 3 + ["/chung"]   # vai trống: không bù


def test_han_muc_nhom_tuy_chinh_va_thu_tu(moi_truong):
    kho, e = moi_truong
    for p in ("/du-an/x/cach-lam", "/vai/coder", "/chung"):
        them(kho, e, p, p)
    kq = nho_lai(kho, e, "q", VUNG_X, nhom={"du-an": 1, "vai": 0, "chung": 1}, bay_gio=BAY_GIO)
    assert [k.pham_vi for k in kq] == ["/du-an/x/cach-lam", "/chung"]


def test_loc_model_khac_va_chua_hieu_luc(moi_truong):
    kho, e = moi_truong
    them(kho, e, "cu", "/du-an/x/cach-lam", mo_hinh="bge-m3@cu")
    them(kho, e, "cho", "/chung", hieu_luc_tu="2026-10-20T00:00:00Z")
    them(kho, e, "ok", "/du-an/x/cach-lam")
    assert [k.id for k in nho_lai(kho, e, "q", VUNG_X, bay_gio=BAY_GIO)] == ["ok"]


def test_embedder_loi_thi_bao_loi(moi_truong):
    kho, _ = moi_truong
    with pytest.raises(LoiEmbedder):
        nho_lai(kho, EmbedderGia(loi_tu_lan=1), "q", VUNG_X, bay_gio=BAY_GIO)
    with pytest.raises(ValueError):
        nho_lai(kho, EmbedderGia(), "  ", VUNG_X, bay_gio=BAY_GIO)


def test_dem_dung_gom_10_phut(moi_truong):
    kho, e = moi_truong
    them(kho, e, "a", "/chung")
    dem = BoDemDung()
    nho_lai(kho, e, "q", VUNG_X, bay_gio=BAY_GIO, dem_dung=dem)
    nho_lai(kho, e, "q", VUNG_X, bay_gio=BAY_GIO, dem_dung=dem)
    assert dem.xa_neu_den_han(kho, BAY_GIO) == 0                              # lần đầu chỉ đặt mốc
    assert dem.xa_neu_den_han(kho, BAY_GIO + timedelta(minutes=9)) == 0
    assert dem.xa_neu_den_han(kho, BAY_GIO + timedelta(minutes=10)) == 2
    a = kho.lay(["a"])["a"]
    assert a.so_lan_dung == 2 and a.dung_luc == "2026-10-13T00:10:00Z"
    assert dem.xa_neu_den_han(kho, BAY_GIO + timedelta(hours=1), ep=True) == 0  # hết việc
