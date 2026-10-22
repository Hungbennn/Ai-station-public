import pytest
from pydantic import ValidationError

from tram.cham_cot.ket_qua import SCHEMA, KetQuaCham, loi_ngu_nghia


def kq(**d):
    base = {"cot": "ai-lam", "ly_do": "Rõ ràng", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 0.9}
    base.update(d)
    return KetQuaCham.model_validate(base)


def test_hop_le():
    assert loi_ngu_nghia(kq()) == []


def test_can_chot_phai_co_cau_hoi_hoac_thieu():
    assert loi_ngu_nghia(kq(cot="can-chot"))
    assert loi_ngu_nghia(kq(cot="can-chot", thieu=["Thiếu tiêu chí nghiệm thu"])) == []


def test_ai_lam_thi_thieu_rong():
    assert loi_ngu_nghia(kq(thieu=["x"]))


def test_do_tin_cay_ngoai_khoang():
    assert loi_ngu_nghia(kq(do_tin_cay=1.5))


def test_ly_do_rong():
    assert loi_ngu_nghia(kq(ly_do="  "))


def test_cot_la_bi_tu_choi():
    with pytest.raises(ValidationError):
        kq(cot="cot-3")


def test_schema_khop_mo_hinh():
    assert SCHEMA["additionalProperties"] is False
    assert set(SCHEMA["required"]) == set(KetQuaCham.model_fields)
    assert SCHEMA["properties"]["cot"]["enum"] == ["ai-lam", "can-chot"]
