import pytest

from asgi_gia import goi
from nho_gia import EmbedderGia, ky_uc
from tram.nho.dich_vu import DichVuNho, tao_app_nho
from tram.nho.kho import KhoKyUc
from tram.nho.nho_lai import BoDemDung
from tram.su_kien.kho import KhoSuKien

TK = {"Authorization": "Bearer bi-mat-1"}
VUNG = ["/du-an/hr-codex", "/vai/cham-cot", "/chung"]


@pytest.fixture
def mt(tmp_path):
    e = EmbedderGia()
    kho = KhoKyUc(tmp_path / "lancedb", so_chieu=e.so_chieu)
    kho.them(ky_uc("m-x", "/du-an/hr-codex/cach-lam", vector=e.embed(["m-x"])[0], noi_dung="Test bằng artisan",
                   nguon=({"loai": "agent", "du_an": "hr-codex", "bead_id": "hr-1"},)))
    kho.them(ky_uc("m-y", "/du-an/khac/cach-lam", vector=e.embed(["m-y"])[0]))
    e.goi.clear()
    dv = DichVuNho(kho, e, lambda: KhoSuKien(tmp_path / "sk.db"), BoDemDung(), "bi-mat-1")
    return tao_app_nho(dv), dv, tmp_path


def test_nho_lai_tra_ba_truong_trong_vung_cap(mt):
    app, dv, _ = mt
    r = goi(app, "POST", "/nho-lai", json_body={"truy_van": "chạy test", "vung_cap": VUNG}, headers=TK)
    assert r.status == 200 and r.json() == {"ky_uc": [
        {"id": "m-x", "noi_dung": "Test bằng artisan", "pham_vi": "/du-an/hr-codex/cach-lam"}]}


@pytest.mark.parametrize("hdr", [{}, {"Authorization": "Bearer sai"}, {"Authorization": "bi-mat-1"},
                                 {"Authorization": "Basic bi-mat-1"}, {"Authorization": "Bearer "}])
def test_thieu_hoac_sai_token_401_ke_ca_khi_than_sai(mt, hdr):
    app, dv, _ = mt
    for than in ({"truy_van": "q", "vung_cap": VUNG}, {"rac": 1}):
        assert goi(app, "POST", "/nho-lai", json_body=than, headers=hdr).status == 401
    assert goi(app, "POST", "/xoa", json_body={"id": "m-x"}, headers=hdr).status == 401
    assert dv.embedder.goi == [] and not dv.kho.lay(["m-x"])["m-x"].da_xoa


@pytest.mark.parametrize("vung", [["/"], ["/du-an"], ["/vai"], [""], ["/du-an/hr", "/"], []])
def test_vung_cap_sai_hoac_rong_422(mt, vung):
    app, dv, _ = mt
    r = goi(app, "POST", "/nho-lai", json_body={"truy_van": "q", "vung_cap": vung}, headers=TK)
    assert r.status == 422 and dv.embedder.goi == []


def test_vung_cap_tien_to_khong_lo_du_an_khac(mt):
    app, _, _ = mt
    r = goi(app, "POST", "/nho-lai", json_body={"truy_van": "q", "vung_cap": ["/du-an/hr"]}, headers=TK)
    assert r.status == 200 and r.json() == {"ky_uc": []}


def test_embedder_loi_503(mt):
    app, dv, _ = mt
    dv.embedder.loi_tu_lan = 1
    r = goi(app, "POST", "/nho-lai", json_body={"truy_van": "q", "vung_cap": VUNG}, headers=TK)
    assert r.status == 503 and r.json()["loi"].startswith("embedder")


def test_xoa_mem_va_su_kien(mt):
    app, dv, tmp_path = mt
    assert goi(app, "POST", "/xoa", json_body={"id": "m-x"}, headers=TK).json() == {"da_xoa": True}
    assert goi(app, "POST", "/xoa", json_body={"id": "m-x"}, headers=TK).json() == {"da_xoa": False}
    assert goi(app, "POST", "/xoa", json_body={"id": "m-khong"}, headers=TK).status == 404
    assert goi(app, "POST", "/xoa", json_body={"id": "x' OR '1'='1"}, headers=TK).status == 422
    ds = KhoSuKien(tmp_path / "sk.db").gan_day("hr-codex", "nho.xoa", 9)
    assert [s.du_lieu for s in ds] == [{"id": "m-x", "pham_vi": "/du-an/hr-codex/cach-lam"}]
    assert dv.kho.dem() == 2 and dv.kho.lay(["m-x"])["m-x"].da_xoa


def test_khong_token_khong_chay(mt):
    _, dv, _ = mt
    dv.token = ""
    with pytest.raises(ValueError):
        tao_app_nho(dv)


def test_tat_trang_tai_lieu(mt):
    app, _, _ = mt
    assert all(goi(app, "GET", p).status == 404 for p in ("/docs", "/openapi.json", "/redoc"))
