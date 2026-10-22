"""Lát 1a-2: đầu ra chế độ rút gọn + câu hỏi dự phòng (spec 0+1a §5.2 bước 4–5)."""
import json

import pytest
from pydantic import ValidationError
from test_claude import ClientGia, tra_loi

from tram.cham_cot.cau_hoi import (CAU_CUOI, DAU_RA_CAU_HOI, SCHEMA_CAU_HOI, CauHoiChot, cau_hoi_du_phong,
                                   loi_cau_hoi)
from tram.cham_cot.luat_cung import KetQuaLuat
from tram.llm.claude import LoiChamLLM, cham_bang_llm

Q = "Hoa hồng tính trên giá trước hay sau giảm giá?"


def luat(*cham, decision_mo=False):
    return KetQuaLuat(tuple(cham), False, decision_mo, ())


@pytest.mark.parametrize("ds, loi", [
    ([Q], []),
    ([], ["từ 1 đến 3"]),
    ([Q] * 4, ["từ 1 đến 3"]),
    (["  "], ["không được rỗng"]),
    (["x" * 301], ["tối đa 300"]),
])
def test_loi_cau_hoi(ds, loi):
    kq = loi_cau_hoi(CauHoiChot(cau_hoi_can_chot=ds))
    assert len(kq) == len(loi) and all(m in k for m, k in zip(loi, kq))


def test_khong_nhan_truong_cot():
    with pytest.raises(ValidationError):
        CauHoiChot.model_validate_json(json.dumps({"cau_hoi_can_chot": [Q], "cot": "ai-lam"}))
    assert SCHEMA_CAU_HOI["additionalProperties"] is False and "cot" not in SCHEMA_CAU_HOI["properties"]


def test_dau_ra_rut_gon_gui_schema_rieng_va_tran_thap():
    c = ClientGia(tra_loi(json.dumps({"cau_hoi_can_chot": [Q]})))
    kq = cham_bang_llm(c, "HỆ", "ND", DAU_RA_CAU_HOI)
    kw = c.goi[0]
    assert kq.ket_qua.cau_hoi_can_chot == [Q] and kq.so_lan == 1
    assert kw["output_config"] == {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA_CAU_HOI}}
    assert kw["max_tokens"] == 1024 and kw["model"] == "claude-sonnet-5-5" and kw["fallbacks"] == "default"


def test_dau_ra_rut_gon_tra_cot_thi_thu_lai_roi_loi():
    sai = tra_loi(json.dumps({"cot": "ai-lam", "ly_do": "x", "thieu": [], "cau_hoi_can_chot": [], "do_tin_cay": 1}))
    c = ClientGia(sai, sai, sai)
    with pytest.raises(LoiChamLLM):
        cham_bang_llm(c, "HỆ", "ND", DAU_RA_CAU_HOI)
    assert len(c.goi) == 3


def test_du_phong_theo_loai_hang_rao():
    cau = cau_hoi_du_phong(luat("tien (từ khoá 'hoa hồng')", "schema (đường dẫn db/migrations/x.php)"))
    assert len(cau) == 2
    assert "tiền" in cau[0] and "(từ khoá 'hoa hồng')" in cau[0] and "Đại ca chốt" in cau[0]
    assert "cấu trúc dữ liệu" in cau[1] and "(đường dẫn db/migrations/x.php)" in cau[1]


def test_du_phong_loai_la_dung_mau_chung():
    assert cau_hoi_du_phong(luat("khac (nhãn x)")) == ["Việc này chạm hàng rào khac (nhãn x). "
                                                       "Đại ca chốt cách làm được phép là gì?"]


def test_du_phong_decision_mo_hoi_chinh_decision():
    cau = cau_hoi_du_phong(luat(decision_mo=True), "  Chốt   giá tour  ")
    assert cau == ["Đại ca chốt quyết định này: Chốt giá tour"]


def test_du_phong_khong_bao_gio_rong():
    assert cau_hoi_du_phong(luat()) == [CAU_CUOI]
