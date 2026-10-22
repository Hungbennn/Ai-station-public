from tram.su_kien.kho import KhoSuKien


def kho(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def test_ghi_va_doc_moi_nhat(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "da_ghi": True}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "can-chot", "da_ghi": False}, bead_id="hr-1")
    assert k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua").du_lieu["cot"] == "can-chot"
    da_ghi = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua", dieu_kien=lambda s: s.du_lieu["da_ghi"])
    assert da_ghi.du_lieu["cot"] == "ai-lam"


def test_moi_nhat_khong_co(tmp_path):
    assert kho(tmp_path).moi_nhat("hr", "hr-x", "cham_cot.ket_qua") is None


def test_du_lieu_giu_tieng_viet(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "x", {"ly_do": "Chạm hàng rào: tiền"}, bead_id="hr-1")
    assert k.moi_nhat("hr", "hr-1", "x").du_lieu["ly_do"] == "Chạm hàng rào: tiền"


def test_moc_quet(tmp_path):
    k = kho(tmp_path)
    assert k.doc_moc("hr") is None
    k.ghi_moc("hr", "2026-10-12T14:00:00Z")
    k.ghi_moc("hr", "2026-10-12T15:00:00Z")
    assert k.doc_moc("hr") == "2026-10-12T15:00:00Z"


def test_gan_day_theo_thu_tu_moi_truoc(tmp_path):
    k = kho(tmp_path)
    for i in range(4):
        k.ghi("hr", "cot.dai_ca_sua", {"i": i}, bead_id=f"hr-{i}")
    assert [s.du_lieu["i"] for s in k.gan_day("hr", "cot.dai_ca_sua", 2)] == [3, 2]


def test_dem_loi_lien_tiep_dung_o_ket_qua(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    assert k.dem_loi_lien_tiep("hr", "hr-1") == 2


def test_cac_du_an(tmp_path):
    k = kho(tmp_path)
    k.ghi("b", "x", {})
    k.ghi("a", "x", {})
    assert k.cac_du_an() == ["a", "b"]


def test_moi_nhat_cac_loai_theo_thu_tu_ghi(tmp_path, monkeypatch):
    import tram.su_kien.kho as m
    monkeypatch.setattr(m, "bay_gio", lambda: "2026-10-12T00:00:00Z")
    k = kho(tmp_path)
    k.ghi("hr", "a", {"n": 1, "da_ghi": True}, bead_id="hr-1")
    k.ghi("hr", "b", {"n": 2, "da_ghi": True}, bead_id="hr-1")
    k.ghi("hr", "b", {"n": 3, "da_ghi": False}, bead_id="hr-1")
    k.ghi("hr", "c", {"n": 4, "da_ghi": True}, bead_id="hr-1")
    assert k.moi_nhat_cac_loai("hr", "hr-1", ("a", "b")).du_lieu["n"] == 3
    loc = k.moi_nhat_cac_loai("hr", "hr-1", ("a", "b"), dieu_kien=lambda s: s.du_lieu["da_ghi"])
    assert loc.loai == "b" and loc.du_lieu["n"] == 2
    assert k.moi_nhat_cac_loai("hr", "hr-2", ("a", "b")) is None
