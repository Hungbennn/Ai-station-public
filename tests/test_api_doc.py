from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from tram.chu import estop


def _bds():
    return {
        "hr": BdGia([bead("hr-1", title="Sửa ‮giá", labels=["cot:ai-lam"], priority=1),
                     bead("hr-2", labels=["cot:cho-review"]),
                     bead("hr-3", status="closed", labels=["cot:ai-lam"])]),
        "web": BdGia([bead("web-1")], tien_to="web"),
    }


def test_cong_viec_tat_ca_va_loc(tmp_path):
    app, _ = tao_app_gia(tmp_path, _bds())
    r = goi(app, "GET", "/api/cong-viec")
    assert r.status == 200
    the = {(t["du_an"], t["id"]): t for t in r.json()["the"]}
    assert set(the) == {("hr", "hr-1"), ("hr", "hr-2"), ("web", "web-1")}
    assert the[("hr", "hr-1")]["hang"] == "ai-lam" and the[("hr", "hr-1")]["tieu_de"] == "Sửa giá"
    assert the[("web", "web-1")]["hang"] == "chua-cham"
    assert [t["id"] for t in goi(app, "GET", "/api/cong-viec?du_an=web").json()["the"]] == ["web-1"]


def test_du_an_khong_co_la_404(tmp_path):
    app, _ = tao_app_gia(tmp_path, _bds())
    r = goi(app, "GET", "/api/cong-viec?du_an=khong-co")
    assert r.status == 404 and "khong-co" in r.json()["loi"]


def test_du_an_dem_cot_va_quet_cuoi(tmp_path):
    app, pt = tao_app_gia(tmp_path, _bds())
    pt.mo_kho().ghi("hr", "quet.xong", {"da_cham": 1})
    ds = {d["ten"]: d for d in goi(app, "GET", "/api/du-an").json()["du_an"]}
    assert ds["hr"]["so_bead"]["ai-lam"] == 1 and ds["hr"]["so_bead"]["cho-review"] == 1
    assert ds["hr"]["quet_cuoi"] is not None and ds["web"]["quet_cuoi"] is None


def test_chi_tiet_bead(tmp_path):
    app, pt = tao_app_gia(tmp_path, _bds())
    pt.mo_kho().ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": "Rõ", "cau_hoi": []}, bead_id="hr-1")
    r = goi(app, "GET", "/api/bead/hr/hr-1").json()
    assert r["the"]["id"] == "hr-1" and r["cham_gan_nhat"]["ly_do"] == "Rõ"
    assert [s["loai"] for s in r["dong_thoi_gian"]] == ["cham_cot.ket_qua"]
    assert goi(app, "GET", "/api/bead/hr/hr-9").status == 404
    assert goi(app, "GET", "/api/bead/hr/-x").status == 422


def test_phe_duyet_va_trang_thai(tmp_path):
    app, _ = tao_app_gia(tmp_path, _bds())
    r = goi(app, "GET", "/api/phe-duyet").json()
    assert r["so"] == 1 and r["muc"][0]["loai"] == "cho-review"
    tt = goi(app, "GET", "/api/chu/trang-thai").json()
    assert tt["estop"] is False and tt["la_dai_ca"] is False and [d["ten"] for d in tt["du_an"]] == ["hr", "web"]
    assert goi(app, "GET", "/api/chu/trang-thai", headers=DAI_CA).json()["la_dai_ca"] is True
    estop.bat("thử")
    assert goi(app, "GET", "/api/chu/trang-thai").json()["estop"] is True


def test_bd_loi_mot_du_an_van_tra_du_an_khac(tmp_path):
    bds = _bds()
    bds["web"] = BdGia(ra_loi_truoc={"tat_ca": 1})
    app, _ = tao_app_gia(tmp_path, bds)
    r = goi(app, "GET", "/api/cong-viec").json()
    assert {t["du_an"] for t in r["the"]} == {"hr"} and "web" in r["loi"]


def test_phuc_vu_file_tinh_va_tat_docs(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<p>bàn điều hành</p>", encoding="utf-8")
    app, _ = tao_app_gia(tmp_path, _bds(), thu_muc_tinh=dist)
    r = goi(app, "GET", "/")
    assert r.status == 200 and "bàn điều hành" in r.body.decode()
    assert goi(app, "GET", "/api/du-an").status == 200
    assert goi(app, "GET", "/openapi.json").status == 404


def test_header_an_toan_va_host_421(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<p>x</p>", encoding="utf-8")
    app, _ = tao_app_gia(tmp_path, _bds(), thu_muc_tinh=dist)
    for duong in ("/", "/api/du-an"):
        r = goi(app, "GET", duong)
        csp = r.headers["content-security-policy"]
        assert r.status == 200 and "script-src 'self'" in csp, duong
        assert "unsafe-eval" not in csp and "unsafe-inline" not in csp and r.headers["x-frame-options"] == "DENY"
    assert goi(app, "GET", "/api/du-an", headers={"Host": "may-b.tail.ts.net"}).status == 200
    assert goi(app, "GET", "/api/du-an", headers={"Host": "rebind.evil.example"}).status == 421
