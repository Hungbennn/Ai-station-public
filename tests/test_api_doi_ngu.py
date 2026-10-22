from dataclasses import replace
from datetime import timedelta

from api_gia import DAI_CA, tao_pt
from asgi_gia import goi
from kho_phieu_gia import LUC
from tram.api.app import tao_app
from tram.cau_hinh.usage import CauHinhUsage
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import dang_ky_khe, khe_dang_bat
from tram.phieu.kho import KhoPhieu
from tram.usage.ccusage import KetQuaCcusage

KHE = [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude tài khoản 1", "vai_uu_tien": ["coder"]}]
URL = "/api/khe/B/claude-1"


def _app(tmp_path, *, kho_phieu=True, **kw):
    db = tmp_path / "sk.db"
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", KHE, luc=LUC)
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/claude-1"}, luc=LUC, bead_id="hr-1", token_vao=10,
                        token_ra=5, mo_hinh="m")
    kho.close()
    pt = replace(tao_pt(tmp_path, {}), mo_kho_phieu=(lambda: KhoPhieu(db)) if kho_phieu else None,
                 dong_ho=lambda: LUC, **kw)
    from passkey_phien_gia import dang_nhap_app
    return dang_nhap_app(tao_app(pt), tmp_path / "pk-test.db")


def _than(**kw):
    return {"ma_thao_tac": kw.pop("ma", "ma-khe-0001"), "expected_version": kw.pop("v", ""), **kw}


def test_doi_ngu_doc_khong_can_danh_tinh_va_tat_khi_chua_co_kho_phieu(tmp_path):
    r = goi(_app(tmp_path), "GET", "/api/doi-ngu")
    assert r.status == 200 and r.json()["bat"] is True and r.json()["khe"][0]["ten_goi_nho"] == "Claude tài khoản 1"
    (tmp_path / "x").mkdir()
    assert goi(_app(tmp_path / "x", kho_phieu=False), "GET", "/api/doi-ngu").json() == {
        "bat": False, "khe": [], "luat_vai": None, "bang_diem": []}


def test_tat_bat_khe_qua_api_can_dai_ca_va_idempotent(tmp_path):
    app = _app(tmp_path)
    assert goi(app, "POST", f"{URL}/tat", json_body=_than()).status == 403
    assert goi(app, "POST", f"{URL}/tat", json_body=_than(),
               headers={"Authorization": "Bearer tok-may", "X-Tram": "1"}).status == 403
    r1 = goi(app, "POST", f"{URL}/tat", json_body=_than(vi_sao="để dành"), headers=DAI_CA)
    r2 = goi(app, "POST", f"{URL}/tat", json_body=_than(vi_sao="để dành"), headers=DAI_CA)
    assert (r1.status, r1.json()["lap_lai"], r2.json()["lap_lai"]) == (200, False, True)
    assert not khe_dang_bat(KhoPhieu(tmp_path / "sk.db"), "B/claude-1")
    assert goi(app, "POST", f"{URL}/bat", json_body=_than(ma="ma-bat-0001", v="0:0"), headers=DAI_CA).status == 409
    v = goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["phien_ban"]
    assert goi(app, "POST", f"{URL}/bat", json_body=_than(ma="ma-bat-0002", v=v), headers=DAI_CA).status == 200


def test_cau_dao_dong_va_loi(tmp_path):
    app = _app(tmp_path)
    v = goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["phien_ban"]
    assert goi(app, "POST", f"{URL}/cau-dao-dong", json_body=_than(v=v), headers=DAI_CA).status == 409
    kho = KhoPhieu(tmp_path / "sk.db")
    with kho.giao_dich():
        ngat_cau_dao(kho, "B/claude-1", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    v = goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["phien_ban"]
    assert goi(app, "POST", f"{URL}/cau-dao-dong", json_body=_than(ma="ma-dao-0002", v=v), headers=DAI_CA).status == 200
    assert goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["cau_dao"]["ngat"] is False
    assert goi(app, "POST", "/api/khe/B/claude-9/tat", json_body=_than(ma="ma-tat-0009"), headers=DAI_CA).status == 404
    assert goi(app, "POST", "/api/khe/B/Claude_1/tat", json_body=_than(ma="ma-tat-0010"), headers=DAI_CA).status == 422
    assert goi(app, "POST", f"{URL}/tat", json_body=_than(ma="ma-tat-0011", la=1), headers=DAI_CA).status == 422
    assert goi(app, "POST", f"{URL}/tat", json_body=_than(ma="ma-tat-0012", vi_sao="x" * 501),
               headers=DAI_CA).status == 422
    (tmp_path / "y").mkdir()
    assert goi(_app(tmp_path / "y", kho_phieu=False), "POST", f"{URL}/tat", json_body=_than(),
               headers=DAI_CA).status == 501


def test_usage_tu_su_kien_va_ccusage(tmp_path):
    goi_cc = []

    def cc(tu, den):
        goi_cc.append((tu.isoformat(), den.isoformat()))
        return KetQuaCcusage("ok", ({"ngay": "2026-10-13", "token_vao": 1, "token_ra": 2, "token_cache_doc": 0,
                                     "token_cache_ghi": 0, "chi_phi_usd": 0.5},), phien_ban="17.2.1")
    app = _app(tmp_path, usage=CauHinhUsage(gia={"m": {"vao": 1e6, "ra": 0, "cache_doc": 0, "cache_ghi": 0}}),
               doc_ccusage=cc)
    r = goi(app, "GET", "/api/usage?so_ngay=7").json()
    assert (r["tu"], r["den"], r["co_bang_gia"]) == ("2026-10-07", "2026-10-13", True)
    assert r["theo_nguon"] == [{"khoa": "B/claude-1", "token_vao": 10, "token_ra": 5, "token_cache_doc": 0,
                                "token_cache_ghi": 0, "so_lan": 1, "chi_phi_usd": 10.0, "thieu_gia": 0}]
    assert r["ccusage"]["trang_thai"] == "ok" and r["ccusage"]["theo_ngay"][0]["chi_phi_usd"] == 0.5
    assert goi_cc == [("2026-10-07", "2026-10-13")]
    assert goi(app, "GET", "/api/usage?so_ngay=93").status == 422
    (tmp_path / "z").mkdir()
    r = goi(_app(tmp_path / "z"), "GET", "/api/usage").json()
    assert r["ccusage"] == {"trang_thai": "chua_cau_hinh", "theo_ngay": [], "loi": None, "phien_ban": None}
    assert r["co_bang_gia"] is False and r["theo_ngay"][0]["chi_phi_usd"] is None


def test_phu_thuoc_that_khong_chay_ccusage_luc_khoi_dong(monkeypatch, tram_home_tam):
    import subprocess
    from tram.api.phu_thuoc import phu_thuoc_that
    goi_that = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: goi_that.append(a))
    assert phu_thuoc_that().doc_ccusage is None
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("usage: {ccusage: /x/ccusage, ccusage_phien_ban: '17.2.1'}\n")
    assert callable(phu_thuoc_that().doc_ccusage) and goi_that == []
