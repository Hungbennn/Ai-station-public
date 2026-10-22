"""API máy A gửi, máy B tạo feature (plan 4d 4D-2): xem không ghi, tạo đúng một lần, mã HTTP theo trạng thái, kho và
actor do B quyết. tram-api thật trong bộ nhớ, sổ thật trên SQLite tạm, `bd` giả."""
from api_yeu_cau_gia import MA, TAO, XEM, dau, mo_app, tao, than
from asgi_gia import goi
from api_gia import DAI_CA, LOGIN
from yeu_cau_gia import BI_MAT

from tram.yeu_cau.so_nhan import SoNhan


def test_xem_khong_ghi_va_cho_biet_kho_ma_trang_thai(tmp_path):
    app, _, bd, _ = mo_app(tmp_path)
    r = goi(app, "POST", XEM, json_body=than(), headers=DAI_CA)
    assert r.status == 200
    d = r.json()
    assert (d["hop_le"], d["loi"], d["du_an"], d["bat_ghi"]) == (True, [], "hr-codex", True)
    assert d["kho"] == "/kho/b/hr-codex"
    assert (d["ma_yeu_cau"], d["dau_xem"], d["bien_nhan"]) == (MA, dau(), None)
    assert bd.so_lan_doc() == bd.so_lan_tao() == 0 and SoNhan(tmp_path / "so.db").lay(MA) is None


def test_tao_mot_lan_gui_lai_tra_feature_cu_va_xem_thay_bien_nhan(tmp_path):
    app, _, bd, _ = mo_app(tmp_path)
    r = tao(app)
    assert (r.status, r.json()["trang_thai"], r.json()["bead_id"]) == (201, "da_tao", "hr-f1")
    r2 = tao(app)
    assert (r2.status, r2.json()["trang_thai"], r2.json()["bead_id"]) == (200, "da_co", "hr-f1")
    assert bd.so_lan_tao() == 1 and SoNhan(tmp_path / "so.db").lay(MA).nguoi_gui == LOGIN
    bn = goi(app, "POST", XEM, json_body=than(), headers=DAI_CA).json()["bien_nhan"]
    assert bn == {"trang_thai": "da_tao", "bead_id": "hr-f1", "cung_noi_dung": True}
    khac = goi(app, "POST", XEM, json_body=than(tieu_de="Khác"), headers=DAI_CA).json()["bien_nhan"]
    assert (khac["cung_noi_dung"], khac["bead_id"]) == (False, None)


def test_sua_sau_khi_xem_thi_lech_ban_xem_khong_ghi(tmp_path):
    app, _, bd, mo = mo_app(tmp_path)
    r = goi(app, "POST", TAO, json_body={**than(tieu_de="Sửa sau khi xem"), "dau_xem": dau()}, headers=DAI_CA)
    assert (r.status, r.json()["trang_thai"]) == (409, "lech_ban_xem")
    assert mo == [] and bd.so_lan_doc() == bd.so_lan_tao() == 0


def test_cung_ma_khac_noi_dung_la_xung_dot(tmp_path):
    app, _, bd, _ = mo_app(tmp_path)
    tao(app)
    r = tao(app, tieu_de="Nội dung khác")
    assert (r.status, r.json()["trang_thai"], bd.so_lan_tao()) == (409, "xung_dot", 1)


def test_khong_ro_va_chua_tao_co_ma_rieng_khong_tao_lai(tmp_path):
    app, _, bd, _ = mo_app(tmp_path / "a", su_co=("truoc_ghi", "loi"))
    for _ in range(3):
        r = tao(app)
        assert (r.status, r.json()["trang_thai"], r.json()["bead_id"]) == (202, "khong_ro", None)
    assert bd.so_lan_tao() == 1 and BI_MAT not in r.body.decode()
    app, _, bd, _ = mo_app(tmp_path / "b", su_co=("doc", "loi"))
    r = tao(app)
    assert (r.status, r.json()["trang_thai"], r.json()["ly_do"]) == (503, "chua_tao", "doc_bd_loi")
    assert tao(app).status == 201 and bd.so_lan_tao() == 1


def test_phieu_sai_bi_tu_choi_khong_chep_noi_dung(tmp_path):
    app, _, bd, mo = mo_app(tmp_path)
    sai = {**than()["phieu"], "muc_tieu": " ", "pham_vi": BI_MAT * 300}
    x = goi(app, "POST", XEM, json_body=than(phieu=sai), headers=DAI_CA)
    assert (x.status, x.json()["hop_le"], x.json()["dau_xem"]) == (200, False, None)
    r = goi(app, "POST", TAO, json_body={**than(phieu=sai), "dau_xem": "0" * 16}, headers=DAI_CA)
    assert (r.status, r.json()["trang_thai"]) == (422, "khong_hop_le") and r.json()["loi"]
    assert BI_MAT not in x.body.decode() + r.body.decode()
    assert len(mo) == 1 and bd.so_lan_doc() == bd.so_lan_tao() == 0     # chỉ /xem mở sổ để đọc biên nhận


def test_chua_cau_hinh_so_bd_hay_yaml_hong_thi_503_chua_mo_so(tmp_path):
    app, pt, bd, mo = mo_app(tmp_path)
    pt.mo_so_nhan = None
    assert (tao(app).status, tao(app).json()["trang_thai"]) == (503, "chua_bat")
    app, pt, bd, mo = mo_app(tmp_path / "b")

    def hong(ten):
        raise ValueError("yaml hỏng " + BI_MAT)
    pt.tao_bd_yeu_cau = hong
    r = tao(app)
    assert (r.status, r.json()["trang_thai"], mo, bd.so_lan_tao()) == (503, "chua_bat", [], 0)
    assert BI_MAT not in r.body.decode()


def test_xem_khi_chua_bat_ghi_khong_mo_so_va_ma_xem_gan_ma_yeu_cau(tmp_path):
    app, _, bd, mo = mo_app(tmp_path, bat_ghi=False)
    d = goi(app, "POST", XEM, json_body=than(), headers=DAI_CA).json()
    assert (d["bat_ghi"], d["hop_le"], mo) == (False, True, [])
    app, _, bd, mo = mo_app(tmp_path / "b")
    khac = "yc-" + "e" * 32                                   # mã xem của MA không dùng được cho mã khác
    r = goi(app, "POST", TAO, json_body={**than(ma_yeu_cau=khac), "dau_xem": dau()}, headers=DAI_CA)
    assert (r.status, r.json()["trang_thai"], bd.so_lan_tao()) == (409, "lech_ban_xem", 0)


def test_phu_thuoc_that_kho_theo_du_an_va_actor_may_a(tmp_path, monkeypatch, tram_home_tam):
    import subprocess

    from tram.api.phu_thuoc import phu_thuoc_that
    (tmp_path / "du-an").mkdir()
    (tmp_path / "du-an" / "thu.yaml").write_text('ten: thu\nduong_dan: "/kho/b/thu"\nhang_rao: {}\n', encoding="utf-8")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)
    pt = phu_thuoc_that()
    bd = pt.tao_bd_yeu_cau("thu")
    assert (str(bd.repo), bd.actor) == ("/kho/b/thu", "dai-ca/may-a")
    so = pt.mo_so_nhan()
    so.close()
    assert (tram_home_tam / "su-kien.db").exists()
