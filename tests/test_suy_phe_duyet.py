from bead_gia import bead, notes_ban_giao
from tram.su_kien.kho import KhoSuKien
from tram.suy.chi_tiet import chi_tiet_bead
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.trang_thai import trang_thai_du_an, trang_thai_tram


def kho(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def _beads():
    return [
        bead("hr-1", labels=["cot:cho-review"], notes=notes_ban_giao(), priority=2),
        bead("hr-2", issue_type="decision", labels=["tram:escalation"]),
        bead("hr-3", labels=["co-do", "cot:cho-review"], priority=1),
        bead("hr-4", issue_type="feature", labels=["cho-duyet-spec"]),
        bead("hr-5", status="closed", labels=["cot:cho-review"]),
        bead("hr-6", labels=["cot:ai-lam"]),
        bead("hr-7", labels=["cot:ai-lam"]),
        bead("hr-8", issue_type="decision", labels=["cot:can-chot"]),
        bead("hr-9", issue_type="decision", status="closed"),
    ]


def test_gom_phe_duyet_du_loai_va_thu_tu(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.loi", {"loi": "API hết hạn mức"}, bead_id="hr-6")
    k.ghi("hr", "cham_cot.bo_qua", {"vi_sao": "loi_lien_tiep"}, bead_id="hr-6")
    k.ghi("hr", "cham_cot.ket_qua", {"huy": "bead_doi_khi_cham", "da_ghi": False}, bead_id="hr-6")
    k.ghi("hr", "cham_cot.bo_qua", {"vi_sao": "loi_lien_tiep"}, bead_id="hr-7")
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m"}, bead_id="hr-7")
    k.ghi("hr", "quet.xong", {})
    k.ghi("hr", "quet.loi", {"loi": "bd list: JSON hỏng"})
    muc = gom_phe_duyet(["hr"], {"hr": _beads()}, k)
    assert [(m["loai"], m["bead_id"]) for m in muc] == [
        ("escalation", "hr-2"), ("decision", "hr-8"), ("co-do", "hr-3"), ("he", None), ("he", "hr-6"),
        ("cho-review", "hr-3"), ("cho-review", "hr-1"), ("spec", "hr-4")]
    he = {m["bead_id"]: m["chi_tiet"] for m in muc if m["loai"] == "he"}
    assert he["hr-6"]["su_kien"] == "cham_cot.bo_qua" and he["hr-6"]["loi"] == "API hết hạn mức"
    assert he[None] == {"su_kien": "quet.loi", "luc": he[None]["luc"], "loi": "bd list: JSON hỏng"}
    cr = {m["bead_id"]: m["chi_tiet"] for m in muc if m["loai"] == "cho-review"}
    assert cr["hr-1"]["pr"] == "https://github.com/o/r/pull/7" and cr["hr-1"]["loi"] == []
    assert cr["hr-3"]["loi"] == ["Thiếu khối bàn giao"] and cr["hr-3"]["pr"] is None


def test_quet_loi_cu_hon_quet_xong_khong_hien(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "quet.loi", {"loi": "x"})
    k.ghi("hr", "quet.xong", {})
    assert gom_phe_duyet(["hr"], {"hr": []}, k) == []


def test_du_an_doc_bd_loi_van_hien_quet_loi(tmp_path):
    k = kho(tmp_path)
    k.ghi("web", "quet.loi", {"loi": "bd hỏng"})
    muc = gom_phe_duyet(["hr", "web"], {"hr": []}, k)
    assert [(m["du_an"], m["loai"]) for m in muc] == [("web", "he")]


def test_trang_thai(tmp_path):
    k = kho(tmp_path)
    assert trang_thai_du_an(k, "hr") == {"ten": "hr", "quet_cuoi": None, "loi_gan_nhat": None}
    k.ghi("hr", "quet.xong", {})
    k.ghi("hr", "cham_cot.loi", {"loi": "cũ"}, bead_id="hr-1")
    k.ghi("hr", "quet.loi", {"loi": "mới‮"})
    tt = trang_thai_du_an(k, "hr")
    assert tt["quet_cuoi"] is not None
    assert tt["loi_gan_nhat"]["loai"] == "quet.loi" and tt["loi_gan_nhat"]["loi"] == "mới"
    assert trang_thai_tram(k, ["hr"], estop_bat=True) == {"estop": True, "du_an": [tt]}


def test_chi_tiet_bead(tmp_path):
    k = kho(tmp_path)
    b = bead("hr-1", labels=["cot:can-chot"], description="Mô tả\x07", acceptance_criteria="Test pass",
             notes=notes_ban_giao())
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "can-chot", "ly_do": "Chạm giá", "cau_hoi": ["Có VAT?"], "da_ghi": True},
          bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": "huỷ", "cau_hoi": [], "da_ghi": False,
                                     "huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    k.ghi("hr", "cot.dai_ca_sua", {"vi_sao": "x"}, bead_id="hr-1")
    ct = chi_tiet_bead("hr", b, {"hr-1": b}, k)
    assert ct["the"]["id"] == "hr-1" and ct["mo_ta"] == "Mô tả" and ct["nghiem_thu"] == "Test pass"
    assert ct["cham_gan_nhat"]["ly_do"] == "Chạm giá" and ct["cham_gan_nhat"]["cau_hoi"] == ["Có VAT?"]
    assert ct["ban_giao"]["pr"] == "https://github.com/o/r/pull/7"
    assert [s["loai"] for s in ct["dong_thoi_gian"]] == ["cham_cot.ket_qua", "cham_cot.ket_qua", "cot.dai_ca_sua"]
    assert ct["dong_thoi_gian"][2]["tom_tat"] == '{"vi_sao": "x"}'


def test_chi_tiet_khong_co_cham_va_ban_giao(tmp_path):
    b = bead("hr-1")
    ct = chi_tiet_bead("hr", b, {"hr-1": b}, kho(tmp_path))
    assert ct["cham_gan_nhat"] is None and ct["ban_giao"] is None and ct["dong_thoi_gian"] == []
