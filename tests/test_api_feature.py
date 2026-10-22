"""tram-api luồng feature (spec 4 §7.1, §7.3; spec 2 §5.2): Phê duyệt theo commit, Duyệt/Trả về spec. `POST
/api/phieu/kiem` đã bỏ (bs-2bd.1.6, Đại ca chốt): skill 4d tạo feature qua `POST /api/feature/yeu-cau` (D46)."""
from api_gia import DAI_CA, LOGIN, tao_app_gia
from asgi_gia import goi
from spec_cho_duyet_gia import V, cho_duyet
from test_phieu_yeu_cau import mo_ta


def app_spec(tmp_path, *, noi=True):
    t = cho_duyet(tmp_path)
    app, pt = tao_app_gia(tmp_path, {"hr-codex": t.g})
    if noi:
        pt.nguon_spec = lambda ten: t.ns
    return app, t


def than(**kw):
    return {"ma_thao_tac": "ma-api-spec-01", "expected_version": V, **kw}


def test_route_kiem_phieu_da_bo(tmp_path):
    app, _ = app_spec(tmp_path)
    r = goi(app, "POST", "/api/phieu/kiem", json_body={"du_an": "hr-codex", "mo_ta": mo_ta()},
            headers={"Tailscale-User-Login": LOGIN})
    assert r.status == 404


def test_phe_duyet_hien_commit_roi_duyet_dung_ban(tmp_path):
    app, t = app_spec(tmp_path)
    [m] = [m for m in goi(app, "GET", "/api/phe-duyet").json()["muc"] if m["loai"] == "spec"]
    assert (m["chi_tiet"]["commit"], m["chi_tiet"]["digest_bead"]) == (t.commit, t.digest)
    url = "/api/phe-duyet/hr-codex/hr-f/duyet"
    cu = goi(app, "POST", url, json_body=than(expected_commit="0" * 40, digest_bead=t.digest), headers=DAI_CA)
    assert cu.status == 409 and t.g.so_lan("tao") == 0                                     # G11
    r = goi(app, "POST", url, json_body=than(ma_thao_tac="ma-api-spec-02", expected_commit=t.commit,
                                             digest_bead=t.digest), headers=DAI_CA)
    assert r.status == 200 and r.json()["ket_qua"]["tao_bead"] == {"t1": "hr-f.1", "t2": "hr-f.2"}
    assert t.g.beads["hr-f"].labels == ("theo-plan",)


def test_tra_ve_spec_qua_api_va_chua_noi_thi_422(tmp_path):
    app, t = app_spec(tmp_path)
    r = goi(app, "POST", "/api/phe-duyet/hr-codex/hr-f/tra-ve", json_body=than(gop_y="Tách hai bead"), headers=DAI_CA)
    assert r.status == 200 and t.g.beads["hr-f"].labels == ("can-spec",)
    app2, t2 = app_spec(tmp_path / "b", noi=False)
    r = goi(app2, "POST", "/api/phe-duyet/hr-codex/hr-f/duyet",
            json_body=than(expected_commit=t2.commit, digest_bead=t2.digest), headers=DAI_CA)
    assert r.status == 422 and t2.g.so_lan("tao") == 0
