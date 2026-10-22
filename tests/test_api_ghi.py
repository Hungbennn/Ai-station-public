from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from duyet_merge_gia import tao
from tram.chu import estop

V = "2026-10-13T01:00:00Z"


def _app(tmp_path, *beads):
    bd = BdGia(beads)
    app, pt = tao_app_gia(tmp_path, {"hr": bd})
    return app, pt, bd


def _than(**kw):
    return {"ma_thao_tac": "ma-api-00001", "expected_version": V, **kw}


def test_ghi_khong_du_danh_tinh_hoac_csrf_bi_403(tmp_path):
    app, _, bd = _app(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    for h in ({}, {**DAI_CA, "Tailscale-User-Login": "nguoi-la@example.com"},
              {k: v for k, v in DAI_CA.items() if k != "X-Tram"}, {**DAI_CA, "Origin": "https://evil.example"}):
        r = goi(app, "POST", "/api/bead/hr/hr-1/cot", json_body=_than(cot="can-chot"), headers=h)
        assert r.status == 403
    assert bd.so_lan("cap_nhat_nhan") == 0


def test_keo_cot_qua_api_lap_lai_va_lam_moi_bo_dem(tmp_path):
    app, pt, bd = _app(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    pt.bo_dem.lay("hr")
    r = goi(app, "POST", "/api/bead/hr/hr-1/cot", json_body=_than(cot="can-chot", vi_sao="giá"), headers=DAI_CA)
    assert r.status == 200 and r.json()["lap_lai"] is False and "cot:can-chot" in bd.beads["hr-1"].labels
    r2 = goi(app, "POST", "/api/bead/hr/hr-1/cot", json_body=_than(cot="can-chot", vi_sao="giá"), headers=DAI_CA)
    assert r2.json()["lap_lai"] is True and bd.so_lan("cap_nhat_nhan") == 1
    assert bd.so_lan("tat_ca") == 1
    pt.bo_dem.lay("hr")
    assert bd.so_lan("tat_ca") == 2


def test_ma_loi_http(tmp_path):
    app, _, _ = _app(tmp_path, bead("hr-1", labels=["cot:ai-lam"]),
                     bead("hr-2", labels=["cot:cho-review", "cho-duyet-spec"]))
    cot = "/api/bead/hr/hr-1/cot"
    r = goi(app, "POST", cot, json_body=_than(ma_thao_tac="loi-api-001", cot="can-chot", expected_version="2026-10-12T00:00:00Z"), headers=DAI_CA)
    assert r.status == 409 and "đã đổi" in r.json()["loi"]
    assert goi(app, "POST", cot, json_body=_than(ma_thao_tac="loi-api-002", cot="cho-review"), headers=DAI_CA).status == 422
    assert goi(app, "POST", cot, json_body=_than(ma_thao_tac="loi-api-003", cot="can-chot", la="x"), headers=DAI_CA).status == 422
    assert goi(app, "POST", "/api/bead/khong/hr-1/cot", json_body=_than(ma_thao_tac="loi-api-004", cot="can-chot"), headers=DAI_CA).status == 404
    assert goi(app, "POST", "/api/bead/hr/hr-99/cot", json_body=_than(ma_thao_tac="loi-api-005", cot="can-chot"), headers=DAI_CA).status == 404
    assert goi(app, "POST", "/api/phe-duyet/hr/hr-2/duyet", json_body=_than(ma_thao_tac="loi-api-cuoi"), headers=DAI_CA).status == 422


def test_chot_tra_ve_tra_loi_thu_lai(tmp_path):
    app, pt, bd = _app(tmp_path, bead("hr-1", title="Giá", labels=["cot:can-chot"]),
                       bead("hr-2", labels=["cot:cho-review"]),
                       bead("hr-3", issue_type="decision", labels=["tram:escalation"]),
                       bead("hr-4", issue_type="decision", labels=["cot:can-chot"]))
    pt.mo_kho().ghi("hr", "cham_cot.ket_qua", {"cot": "can-chot", "ly_do": "x", "cau_hoi": ["Có VAT?"]}, bead_id="hr-1")
    r = goi(app, "POST", "/api/bead/hr/hr-1/chot", json_body=_than(ma_thao_tac="ma-chot-0001", tra_loi=["Có"]),
            headers=DAI_CA)
    assert r.status == 200 and r.json()["ket_qua"]["tao_decision"].startswith("hr-")
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-2/tra-ve", json_body=_than(ma_thao_tac="ma-trave-001", gop_y="Thiếu test"),
            headers=DAI_CA)
    assert r.status == 200 and "cot:cho-review" not in bd.beads["hr-2"].labels
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-3/tra-loi", json_body=_than(ma_thao_tac="ma-traloi-01", tra_loi="Làm A"),
            headers=DAI_CA)
    assert r.status == 200 and bd.beads["hr-3"].status == "closed"
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-4/tra-loi", json_body=_than(ma_thao_tac="ma-traloi-02", tra_loi="Chọn B"),
            headers=DAI_CA)
    assert r.status == 200 and bd.beads["hr-4"].close_reason == "Chọn B"     # decision mở (Q4)
    r = goi(app, "POST", "/api/bead/hr/hr-1/thu-lai",
            json_body=_than(ma_thao_tac="ma-thulai-01", expected_version=bd.beads["hr-1"].updated_at), headers=DAI_CA)
    assert r.status == 200 and pt.mo_kho().gan_day("hr", "cham_cot.thu_lai", 1)


def test_duyet_dong_bead(tmp_path):
    t = tao(tmp_path, da_vao=True, nhanh_chinh="develop")
    bd = t.n.bd
    app, pt = tao_app_gia(tmp_path, {"hr": bd})
    pt.nguon_duyet = t.n.nguon_duyet
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-2/duyet", json_body=_than(), headers=DAI_CA)
    assert r.status == 200 and bd.beads["hr-2"].status == "closed"
    assert bd.beads["hr-2"].close_reason == f"Đại ca duyệt — commit {t.commit[:7]} đã vào develop"


def test_duyet_chua_vao_main_tra_422_va_loi_nguyen_van(tmp_path):
    t = tao(tmp_path)
    app, pt = tao_app_gia(tmp_path, {"hr": t.n.bd})
    pt.nguon_duyet = t.n.nguon_duyet
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-2/duyet", json_body=_than(), headers=DAI_CA)
    assert r.status == 422
    assert r.json()["loi"] == ("Commit chưa vào main và trạm chưa mở PR — ghép nhánh tram/hr-2 "
                               "vào main rồi bấm Duyệt")
    assert t.n.bd.beads["hr-2"].status == "open" and t.n.bd.goi == []


def test_estop_va_tiep_tuc_qua_api(tmp_path):
    app, pt, _ = _app(tmp_path)
    r = goi(app, "POST", "/api/chu/estop",
            json_body={"ma_thao_tac": "ma-estop-001", "expected_version": "tat", "ly_do": "thử"}, headers=DAI_CA)
    assert r.status == 200 and estop.dang_bat()
    assert pt.mo_kho().gan_day("_tram", "estop.bat", 1)[0].du_lieu["ly_do"] == "thử"
    r = goi(app, "POST", "/api/chu/tiep-tuc", json_body={"ma_thao_tac": "ma-tieptuc-01", "expected_version": "bat"},
            headers=DAI_CA)
    assert r.status == 200 and not estop.dang_bat()
    assert goi(app, "POST", "/api/chu/estop",
               json_body={"ma_thao_tac": "ma-estop-002", "expected_version": "tat"}).status == 403
