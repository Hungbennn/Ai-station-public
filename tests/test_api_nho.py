"""1b-3: /api/nho/* — chỉ Đại ca xem/ghi, lỗi memory service ánh xạ đúng mã, idempotent theo ma_thao_tac."""
from contextlib import closing

import pytest

from api_gia import DAI_CA, LOGIN, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.nho.khach import LoiNhoKhach

KY_UC = {"id": "m-1", "noi_dung": "Chạy test‮ trước", "pham_vi": "/chung", "nhan": ["test"], "quan_trong": 0.8,
         "nguon": [{"loai": "thang_cap", "id_goc": "m-a", "du_an": "hr"}], "nguon_dai_ca": False,
         "hieu_luc_tu": "2999-01-01T00:00:00Z", "tao_luc": "2026-10-13T00:00:00Z", "dung_luc": None, "so_lan_dung": 0,
         "mo_hinh_embed": "bge-m3@x", "da_xoa": False}


class KhachGia:
    def __init__(self, **tra):
        self.tra, self.goi_ = tra, []

    def goi(self, duong, than, *, thoi_gian_cho):
        self.goi_.append((duong, than, thoi_gian_cho))
        x = self.tra[duong]
        if isinstance(x, Exception):
            raise x
        return x


def _app(tmp_path, **tra):
    app, pt = tao_app_gia(tmp_path, {"hr": BdGia([])})
    pt.nho = KhachGia(**tra)
    return app, pt


def _than(**kw):
    return {"ma_thao_tac": "ma-nho-00001", "expected_version": "", **kw}


def test_xem_can_danh_tinh_dai_ca(tmp_path):
    app, pt = _app(tmp_path, **{"/danh-sach": {"ky_uc": [KY_UC], "tong": 1,
                                              "pham_vi": [{"pham_vi": "/chung", "so": 1, "so_cho": 1}]}})
    for h in ({}, {"Tailscale-User-Login": "nguoi-la@example.com"}):
        assert goi(app, "GET", "/api/nho", headers=h).status == 403
        assert goi(app, "GET", "/api/nho/su-kien", headers=h).status == 403
    assert pt.nho.goi_ == []
    r = goi(app, "GET", "/api/nho?pham_vi=/chung&cho=1", headers={"Tailscale-User-Login": LOGIN})
    assert r.status == 200 and "content-security-policy" in r.headers
    k = r.json()["ky_uc"][0]
    assert k["noi_dung"] == "Chạy test trước" and k["dang_cho"] is True and k["nguon"][0]["id_goc"] == "m-a"
    assert r.json()["pham_vi"] == [{"pham_vi": "/chung", "so": 1, "so_cho": 1}] and r.json()["tong"] == 1
    assert pt.nho.goi_ == [("/danh-sach", {"pham_vi": "/chung", "cho_hieu_luc": True, "gioi_han": 200}, 10.0)]


def test_memory_chua_noi_hoac_tat_thi_503(tmp_path):
    app, pt = _app(tmp_path, **{"/danh-sach": LoiNhoKhach("không gọi được memory service: URLError")})
    r = goi(app, "GET", "/api/nho", headers=DAI_CA)
    assert r.status == 503 and "memory service" in r.json()["loi"]
    pt.nho = None
    assert goi(app, "GET", "/api/nho", headers=DAI_CA).status == 503


def test_xoa_can_csrf_idempotent_va_404(tmp_path):
    app, pt = _app(tmp_path, **{"/xoa": {"da_xoa": True}})
    h = {k: v for k, v in DAI_CA.items() if k != "X-Tram"}
    assert goi(app, "POST", "/api/nho/xoa", json_body=_than(id="m-1"), headers=h).status == 403
    for lap in (False, True):
        r = goi(app, "POST", "/api/nho/xoa", json_body=_than(id="m-1"), headers=DAI_CA)
        assert r.status == 200 and r.json() == {"ket_qua": {"xoa": {"da_xoa": True}}, "lap_lai": lap}
    assert len(pt.nho.goi_) == 1
    assert goi(app, "POST", "/api/nho/xoa", json_body=_than(id="m-2"), headers=DAI_CA).status == 409
    pt.nho.tra["/xoa"] = LoiNhoKhach("memory service trả 404", ma=404, than={"loi": "Không có ký ức này"})
    r = goi(app, "POST", "/api/nho/xoa", json_body=_than(id="m-9", ma_thao_tac="ma-nho-00002"), headers=DAI_CA)
    assert r.status == 404 and r.json() == {"loi": "Không có ký ức này"}


def test_ghi_kiem_du_an_gui_ma_va_bao_ly_do_tu_choi(tmp_path):
    kq = {"id": "m-g", "pham_vi": "/chung", "xoa": [], "lap_lai": False}
    app, pt = _app(tmp_path, **{"/ghi": kq})
    r = goi(app, "POST", "/api/nho/ghi", json_body=_than(noi_dung="x", pham_vi="/du-an/khac/cach-lam", ma_thao_tac="ma-nho-la-01"), headers=DAI_CA)
    assert r.status == 404 and pt.nho.goi_ == []
    r = goi(app, "POST", "/api/nho/ghi", json_body=_than(noi_dung="Chạy test", pham_vi="/chung", nhan=["test"]),
            headers=DAI_CA)
    assert r.status == 200 and r.json()["ket_qua"] == {"ghi": kq}
    assert pt.nho.goi_ == [("/ghi", {"noi_dung": "Chạy test", "pham_vi": "/chung", "nhan": ["test"],
                                     "ma_thao_tac": "ma-nho-00001"}, 60.0)]
    pt.nho.tra["/ghi"] = LoiNhoKhach("memory service trả 422", ma=422,
                                     than={"loi": "Chạm luật nghiệp vụ", "ly_do": ["số tiền (10k)"]})
    r = goi(app, "POST", "/api/nho/ghi", json_body=_than(noi_dung="Phí 10k", pham_vi="/chung",
                                                        ma_thao_tac="ma-nho-00002"), headers=DAI_CA)
    assert r.status == 422 and r.json() == {"loi": "Chạm luật nghiệp vụ; số tiền (10k)"}


@pytest.mark.parametrize("than", [{"noi_dung": "x" * 601, "pham_vi": "/chung"}, {"noi_dung": "x"},
                                  {"noi_dung": "x", "pham_vi": "/chung", "nhan": ["a"] * 6}])
def test_ghi_than_sai_422(tmp_path, than):
    app, pt = _app(tmp_path, **{"/ghi": {}})
    assert goi(app, "POST", "/api/nho/ghi", json_body=_than(**than), headers=DAI_CA).status == 422
    assert pt.nho.goi_ == []


def test_su_kien_nho_moi_du_an_va_he_moi_nhat_truoc(tmp_path):
    app, pt = _app(tmp_path)
    kho = pt.mo_kho()
    kho.ghi("hr", "nho.ghi", {"id": "m-1", "pham_vi": "/du-an/hr/cach-lam", "nguon": []}, bead_id="hr-1")
    kho.ghi("hr", "cot.da_chot", {"decision_id": "d"}, bead_id="hr-1")
    kho.ghi("_tram", "nho.thang_cap", {"id": "m-t", "pham_vi": "/chung"})
    kho.ghi("khac", "nho.ghi", {"id": "m-x"})                       # dự án không còn trong du-an/: không hiện
    r = goi(app, "GET", "/api/nho/su-kien", headers=DAI_CA)
    assert [(s["du_an"], s["loai"]) for s in r.json()["su_kien"]] == [("_tram", "nho.thang_cap"), ("hr", "nho.ghi")]
    assert r.json()["su_kien"][1]["bead_id"] == "hr-1" and '"m-1"' in r.json()["su_kien"][1]["tom_tat"]


def test_timeline_khong_lo_nguon_memory_cho_nguoi_doc_mo(tmp_path):
    from bead_gia import bead
    app, pt = tao_app_gia(tmp_path, {"hr": BdGia([bead("hr-1")])})
    with closing(pt.mo_kho()) as kho:
        kho.ghi("hr", "nho.ghi", {"nguon": [{"du_an": "bi-mat-nguon"}]}, bead_id="hr-1")
    assert "bi-mat-nguon" not in str(goi(app, "GET", "/api/bead/hr/hr-1").json())
    assert "bi-mat-nguon" in str(goi(app, "GET", "/api/bead/hr/hr-1", headers=DAI_CA).json())
