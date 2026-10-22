from contextlib import closing

from api_gia import DAI_CA
from phieu_gia import de_xuat
from tho_api_gia import tao_tram
from tram.phieu.ket_thuc import thu_hoi

BG = {"phien_ban": 1, "loai": "chinh-thuc", "luot": 1, "file_ban_giao": "docs/handovers/x.md", "nhanh": "tram/hr-6xe1",
      "commit": "abcdef1", "doi_chieu_nghiem_thu": [], "lenh_kiem": [], "quyet_dinh": [], "huong_da_bo": [],
      "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [], "thay_doi_vung_nhay_cam": []}
NHIP = {"khe_id": "B/claude-1", "buoc_tho": "ranh"}


def test_token_may_bat_buoc_ke_ca_khi_than_sai(tmp_path):
    t = tao_tram(tmp_path)
    for may, h in ((None, {}), (None, {"Authorization": "Bearer sai"}), (None, {"Authorization": t.token["B"]})):
        assert t.goi("POST", "/api/tho/nhip", may, json_body={"rác": 1}, headers=h).status == 401
    assert t.goi("GET", "/api/tho/ping", None, headers={**DAI_CA}).status == 401     # danh tính Đại ca không thay
    r = t.goi("GET", "/api/tho/ping")
    assert r.status == 200 and r.json()["may_id"] == "B" and [k["khe_id"] for k in r.json()["khe"]] == [
        "B/claude-1", "B/claude-2"] and r.json()["khe"][0]["cau_dao"]["ngat"] is False


def test_khong_can_x_tram_origin_va_token_may_khong_co_quyen_dashboard(tmp_path):
    t = tao_tram(tmp_path)
    assert t.goi("POST", "/api/tho/nhip", json_body=NHIP).json() == {"tiep_tuc": True, "phieu": None}
    r = t.goi("POST", "/api/chu/estop", json_body={"ma_thao_tac": "m-12345678", "expected_version": "x"})
    assert r.status == 403


def test_dang_ky_va_khe_cua_may_khac_403(tmp_path):
    t = tao_tram(tmp_path)
    assert t.goi("POST", "/api/tho/dang-ky", "C", json_body={"may_id": "B", "khe": [
        {"ten": "x", "cli": "claude", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]}]}).status == 403
    assert t.goi("POST", "/api/tho/nhip", "C", json_body=NHIP).status == 403
    assert t.goi("POST", "/api/tho/nhip", json_body={**NHIP, "khe_id": "B/claude-9"}).status == 403
    for khe in ({"ten": "x", "cli": "gemini", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]},
                {"ten": "x", "cli": "claude", "ten_goi_nho": "a@b.c", "vai_uu_tien": ["qc"]}):
        assert t.goi("POST", "/api/tho/dang-ky", json_body={"may_id": "B", "khe": [khe]}).status == 422


def test_luong_phieu_qua_http(tmp_path):
    t = tao_tram(tmp_path, chon=lambda khe, hm: de_xuat())
    p = t.goi("POST", "/api/tho/nhip", json_body=NHIP).json()["phieu"]
    giu = {"khe_id": "B/claude-1", "giao_id": p["giao_id"], "luot": 1}
    t.toi(seconds=30)
    assert t.goi("POST", "/api/tho/nhip", json_body={**giu, "buoc_tho": "chay"}).json()["han_giu"] == \
        "2026-10-13T03:10:30Z"
    ev = {**giu, "loai": "chay.bat_dau", "du_lieu": {"lan": 1}, "request_id": "r-chay0001"}
    assert t.goi("POST", "/api/tho/su-kien", json_body=ev).status == 200
    assert t.goi("POST", "/api/tho/su-kien", json_body={**ev, "request_id": "r-bat-lap1"}).status == 422
    assert t.goi("POST", "/api/tho/su-kien", json_body={**ev, "loai": "bao.xong", "request_id": "r-x1234567"}
                 ).status == 400
    assert t.goi("POST", "/api/tho/su-kien", json_body={**ev, "du_lieu": {"lan": 9}, "request_id": "r-x1234568"}
                 ).status == 422
    xong = {**giu, "loai": "xong", "ban_giao": BG, "commit": "abcdef1", "request_id": "r-xong0001"}
    r1 = t.goi("POST", "/api/tho/bao", json_body=xong)
    assert r1.status == 200 and t.goi("POST", "/api/tho/bao", json_body=xong).json() == r1.json()
    assert t.goi("POST", "/api/tho/bao", json_body={**xong, "noi_dung": "khác"}).json() == {
        "ly_do": "request-id-trung"}
    r = t.goi("POST", "/api/tho/bao", json_body={**giu, "loai": "moc", "request_id": "r-moc00001"})
    assert (r.status, r.json()) == (409, {"ly_do": "luot-cu"})
    sai = {**xong, "ban_giao": {**BG, "luot": 2}, "request_id": "r-90000000"}
    assert t.goi("POST", "/api/tho/bao", json_body=sai).status == 422


def test_noi_bo_chi_token_noi_bo_ma_giao_chi_khi_hieu_luc(tmp_path):
    t = tao_tram(tmp_path, chon=lambda khe, hm: de_xuat(), token_noi_bo="tok-noi-bo")
    p = t.goi("POST", "/api/tho/nhip", json_body=NHIP).json()["phieu"]
    url = f"/api/noi-bo/phieu/{p['giao_id']}"
    assert t.goi("GET", url).status == 401                                          # token máy không dùng được
    r = t.goi("GET", url, None, headers={"Authorization": "Bearer tok-noi-bo"})
    assert r.status == 200 and r.json() == {"du_an": "hr-codex", "vai": "coder", "ma_giao": p["ma_giao"],
                                            "con_hieu_luc": True} and r.headers["cache-control"] == "no-store"
    assert t.goi("GET", "/api/noi-bo/phieu/g-20991231-0001", None,
                 headers={"Authorization": "Bearer tok-noi-bo"}).status == 404
    with closing(t.kho()) as kho:
        with kho.giao_dich():
            thu_hoi(kho, kho.lay(p["giao_id"]), ly_do="mat-nhip", luc=t.gio[0])
    assert t.goi("GET", url, None, headers={"Authorization": "Bearer tok-noi-bo"}).json()["ma_giao"] is None
    (tmp_path / "x").mkdir()
    t2 = tao_tram(tmp_path / "x", token_noi_bo=None)
    assert t2.goi("GET", url, None, headers={"Authorization": "Bearer "}).status == 401


def test_phu_thuoc_that_khong_doc_keychain_luc_khoi_dong(monkeypatch):
    import subprocess
    from tram.api import noi_bo
    from tram.api.phu_thuoc import phu_thuoc_that
    goi = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: goi.append(a))
    pt = phu_thuoc_that()
    assert goi == [] and pt.mo_kho_phieu is not None
    dem = []
    lay = noi_bo.doc_mot_lan(lambda: dem.append(1) or "t")
    assert lay() == lay() == "t" and dem == [1]
