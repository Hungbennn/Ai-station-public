"""1b-3: HTTP `/ghi`, `/danh-sach` của memory service — Bearer, mã lỗi, ký ức thăng cấp đang chờ."""
import pytest

from asgi_gia import goi
from nho_gia import ClientGia, EmbedderGia, ky_uc
from tram.cham_cot.prompt import nap_vai
from tram.nho.dich_vu import DichVuNho, tao_app_nho
from tram.nho.ghi_tay import id_ghi_tay
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.nhat_ky import NhatKy
from tram.nho.nho_lai import BoDemDung
from tram.su_kien.kho import KhoSuKien

TK = {"Authorization": "Bearer bi-mat-1"}
LUC = "2026-10-20T03:00:00Z"
LUAT = {"hr": LuatDuAn(("Pay",), ())}


@pytest.fixture
def mt(tmp_path):
    e = EmbedderGia()
    dv = DichVuNho(KhoKyUc(tmp_path / "lancedb", so_chieu=16), e, lambda: KhoSuKien(tmp_path / "sk.db"), BoDemDung(),
                   "bi-mat-1", client=ClientGia(), vai_gop=nap_vai("nho-gop"),
                   mo_nhat_ky=lambda: NhatKy(tmp_path / "nk.db"), luat_cua=LUAT.__getitem__,
                   cac_du_an=lambda: ["hr"], luc=lambda: LUC)
    return tao_app_nho(dv), dv


def ghi(app, **kw):
    than = {"noi_dung": "Chạy test trước khi bàn giao.", "pham_vi": "/chung", "ma_thao_tac": "ma-ghi-0001", **kw}
    return goi(app, "POST", "/ghi", json_body=than, headers=TK)


def test_ghi_200_roi_gui_lai_cung_ma(mt):
    app, dv = mt
    r = ghi(app, nhan=["test"])
    assert r.status == 200 and r.json() == {"id": id_ghi_tay("ma-ghi-0001"), "pham_vi": "/chung", "xoa": [],
                                            "lap_lai": False}
    assert ghi(app, nhan=["test"]).json()["lap_lai"] is True and dv.kho.dem() == 1


def test_ghi_ep_nghiep_vu_va_tu_choi_ngoai_du_an(mt):
    app, dv = mt
    assert ghi(app, noi_dung="Module Pay chạy migrate trước", pham_vi="/du-an/hr/cach-lam").json()["pham_vi"] == \
        "/du-an/hr/nghiep-vu"
    r = ghi(app, noi_dung="Phí 100k mỗi lần", ma_thao_tac="ma-ghi-0002")
    assert r.status == 422 and r.json() == {"loi": "Chạm luật nghiệp vụ — /vai, /chung không nhận",
                                            "ly_do": ["số tiền (100k)"]}
    r = ghi(app, pham_vi="/du-an/hr", ma_thao_tac="ma-ghi-0003")
    assert r.status == 422 and "bốn dạng" in r.json()["loi"]


def test_ghi_503_khi_chua_cau_hinh_claude_hoac_embedder_loi(mt):
    app, dv = mt
    dv.embedder.loi_tu_lan = 1
    assert ghi(app).status == 503 and ghi(app).json()["loi"].startswith("embedder")
    dv.client = None
    assert ghi(app).json() == {"loi": "llm: memory service chưa cấu hình Claude cho gộp"}


@pytest.mark.parametrize("than", [{"ma_thao_tac": "ngan"}, {"nhan": ["a"] * 6}, {"noi_dung": "x" * 601},
                                  {"pham_vi": "x" * 201}])
def test_than_sai_422(mt, than):
    app, dv = mt
    assert ghi(app, **than).status == 422 and dv.kho.dem() == 0


@pytest.mark.parametrize("hdr", [{}, {"Authorization": "Bearer sai"}])
def test_thieu_token_401(mt, hdr):
    app, dv = mt
    assert goi(app, "POST", "/ghi", json_body={"rac": 1}, headers=hdr).status == 401
    assert goi(app, "POST", "/danh-sach", json_body={}, headers=hdr).status == 401


def test_danh_sach_moi_nhat_truoc_loc_pham_vi_va_dang_cho(mt):
    app, dv = mt
    e = dv.embedder
    dv.kho.them(ky_uc("m-1", "/du-an/hr/cach-lam", vector=e.embed(["1"])[0], tao_luc="2026-10-01T00:00:00Z"))
    dv.kho.them(ky_uc("m-2", "/chung", vector=e.embed(["2"])[0], tao_luc="2026-10-19T00:00:00Z",
                      hieu_luc_tu="2026-10-26T00:00:00Z", nhan=("test",),
                      nguon=({"loai": "thang_cap", "id_goc": "m-a", "du_an": "a"},)))
    dv.kho.them(ky_uc("m-3", "/chung", vector=e.embed(["3"])[0], da_xoa=True))
    r = goi(app, "POST", "/danh-sach", json_body={}, headers=TK).json()
    assert [k["id"] for k in r["ky_uc"]] == ["m-2", "m-1"] and r["tong"] == 2
    assert r["pham_vi"] == [{"pham_vi": "/chung", "so": 1, "so_cho": 1},
                            {"pham_vi": "/du-an/hr/cach-lam", "so": 1, "so_cho": 0}]
    k = r["ky_uc"][0]
    assert "vector" not in k and k["nhan"] == ["test"] and k["nguon"][0]["id_goc"] == "m-a"
    assert k["hieu_luc_tu"] == "2026-10-26T00:00:00Z" and k["quan_trong"] == 0.5
    cho = goi(app, "POST", "/danh-sach", json_body={"cho_hieu_luc": True}, headers=TK).json()
    assert [k["id"] for k in cho["ky_uc"]] == ["m-2"]
    pv = goi(app, "POST", "/danh-sach", json_body={"pham_vi": "/du-an/hr/cach-lam", "gioi_han": 1}, headers=TK).json()
    assert [k["id"] for k in pv["ky_uc"]] == ["m-1"]
    assert goi(app, "POST", "/danh-sach", json_body={"pham_vi": "/du-an/hr"}, headers=TK).status == 422
    assert goi(app, "POST", "/danh-sach", json_body={"gioi_han": 1001}, headers=TK).status == 422


def test_xoa_cho_gop_xong_va_ghi_cung_ma_khac_noi_dung_409(mt):
    from concurrent.futures import ThreadPoolExecutor, TimeoutError
    from threading import Event
    app, dv = mt
    r = ghi(app)
    assert ghi(app, noi_dung="khác").status == 409
    id = r.json()["id"]
    bat_dau = Event()
    def xoa():
        bat_dau.set()
        return goi(app, "POST", "/xoa", json_body={"id": id}, headers=TK)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with dv.kho.khoa_gop:
            f = pool.submit(xoa)
            assert bat_dau.wait(2)
            with pytest.raises(TimeoutError):
                f.result(timeout=0.1)
            assert not dv.kho.lay([id])[id].da_xoa
        assert f.result(timeout=5).status == 200
