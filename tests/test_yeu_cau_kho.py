from tram.su_kien.kho import KhoSuKien


def kho(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def test_su_kien_co_id_tang_dan(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "x", {}, bead_id="hr-1")
    k.ghi("hr", "x", {}, bead_id="hr-1")
    moi, cu = k.gan_day("hr", "x", 2)
    assert moi.id > cu.id > 0


def test_thu_lai_cat_chuoi_loi(tmp_path):
    k = kho(tmp_path)
    for _ in range(3):
        k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m1"}, bead_id="hr-1", tac_nhan="dai-ca")
    assert k.dem_loi_lien_tiep("hr", "hr-1") == 0
    k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    assert k.dem_loi_lien_tiep("hr", "hr-1") == 1


def test_nhan_su_kien_nguon_thanh_yeu_cau_mot_lan(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m1"}, bead_id="hr-1", tac_nhan="dai-ca")
    nguon = k.gan_day("hr", "cham_cot.thu_lai", 1)[0].id
    assert k.yeu_cau.nhan_su_kien_nguon("hr") == 1
    assert k.yeu_cau.nhan_su_kien_nguon("hr") == 0
    assert k.yeu_cau.dang_cho("hr") == {"hr-1": [nguon]}


def test_danh_dau_xong_roi_nhan_lai_khong_tao_lai(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.thu_lai", {}, bead_id="hr-1", tac_nhan="dai-ca")
    k.yeu_cau.nhan_su_kien_nguon("hr")
    k.yeu_cau.danh_dau_xong("hr", "hr-1", k.yeu_cau.dang_cho("hr")["hr-1"])
    k.yeu_cau.nhan_su_kien_nguon("hr")
    assert k.yeu_cau.dang_cho("hr") == {}


def test_thu_lai_du_an_khac_khong_lan(tmp_path):
    k = kho(tmp_path)
    k.ghi("khac", "cham_cot.thu_lai", {}, bead_id="hr-1")
    k.yeu_cau.nhan_su_kien_nguon("hr")
    assert k.yeu_cau.dang_cho("hr") == {}


def test_anh_decision_chua_luu_la_none_luu_rong_la_dict_rong(tmp_path):
    k = kho(tmp_path)
    assert k.yeu_cau.doc_anh_decision("hr") is None
    k.yeu_cau.luu_anh_decision("hr", {}, [])
    assert k.yeu_cau.doc_anh_decision("hr") == {}


def test_luu_anh_decision_tao_su_kien_nguon_va_yeu_cau(tmp_path):
    k = kho(tmp_path)
    ids = k.yeu_cau.luu_anh_decision("hr", {"hr-d": [True, "Có"]},
                                     [("hr-1", {"decision_ids": ["hr-d"]}), ("hr-2", {"decision_ids": ["hr-d"]})])
    assert k.yeu_cau.doc_anh_decision("hr") == {"hr-d": [True, "Có"]}
    assert k.yeu_cau.dang_cho("hr") == {"hr-1": [ids[0]], "hr-2": [ids[1]]}
    sk = k.moi_nhat("hr", "hr-1", "cham_cot.can_cham_lai")
    assert sk.id == ids[0] and sk.tac_nhan == "tram/cham-cot"
    assert sk.du_lieu == {"nguon": "decision", "decision_ids": ["hr-d"]}  # kho tự chèn nguon


def test_yeu_cau_ben_qua_lan_mo_kho_moi(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.thu_lai", {}, bead_id="hr-1")
    k.yeu_cau.nhan_su_kien_nguon("hr")
    assert list(KhoSuKien(tmp_path / "sk.db").yeu_cau.dang_cho("hr")) == ["hr-1"]


def test_ket_qua_bi_huy_thanh_yeu_cau(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "da_ghi": False, "huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "da_ghi": True}, bead_id="hr-2")
    assert k.yeu_cau.nhan_su_kien_nguon("hr") == 1
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-1"]


def test_ket_qua_bi_huy_khong_cat_va_khong_tinh_vao_chuoi_loi(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    assert k.dem_loi_lien_tiep("hr", "hr-1") == 2


def test_dem_huy_lien_tiep_dung_o_ket_qua_khong_huy(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.ket_qua", {"huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"da_ghi": True}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.loi", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"huy": "khong_doc_duoc_version"}, bead_id="hr-1")
    assert k.yeu_cau.dem_huy_lien_tiep("hr", "hr-1") == 2


def test_dong_het_gom_ca_su_kien_chua_nhan(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.thu_lai", {}, bead_id="hr-1")
    k.yeu_cau.nhan_su_kien_nguon("hr")
    k.ghi("hr", "cham_cot.ket_qua", {"huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.thu_lai", {}, bead_id="hr-2")
    k.yeu_cau.dong_het("hr", "hr-1")
    k.yeu_cau.nhan_su_kien_nguon("hr")
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-2"]
