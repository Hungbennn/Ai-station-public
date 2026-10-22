"""bs-2bd.1.19 (D23, D40 "quét nguồn 1b-1/1b-2 để lát sau"): nguồn `cot.dai_ca_sua`, `cot.da_chot`, `cot.tra_ve`,
`nho.agent_ghi` qua bộ quét bí mật trên bản gốc, TRƯỚC LLM/embed/lưu; `ghi_nho` từ chối ngay, không ghi sự kiện.
Khoá GIẢ ghép lúc chạy; không đoạn khớp nào được lọt ra thông báo."""
from contextlib import closing

import pytest

from test_nho_cong_cu import PHIEU, dv  # noqa: F401 — fixture `dv` dùng lại
from tram.nho.bi_mat import LoiBiMat
from tram.nho.cong_cu import LoiCongCu, nhan_ghi_nho
from tram.nho.nguon import LOAI_AGENT_GHI, TAC_NHAN_NHO, doc_dau_vao
from tram.su_kien.kho import SuKien

KHOA = "".join(["gh", "p_", "Sentinel", "0" * 28])
MAT_KHAU = "".join(["pass", "word=", "Sentinel", "Mk"])


def sk(loai, du_lieu, tac_nhan="dai-ca/dashboard"):
    return SuKien("2026-10-17T02:00:00Z", "hr-codex", "hr-12", loai, tac_nhan, du_lieu, 900)


@pytest.mark.parametrize("loai, du_lieu, nguon", [
    ("cot.dai_ca_sua", {"tieu_de": "Sửa", "cot_he": "ai-lam", "cot_moi": "can-chot", "vi_sao": f"key {KHOA}"},
     "dai_ca_sua"),
    ("cot.dai_ca_sua", {"tieu_de": f"Đổi {MAT_KHAU}", "cot_he": "ai-lam", "cot_moi": "can-chot"}, "dai_ca_sua"),
    ("cot.dai_ca_sua", {"tieu_de": "Sửa", "ly_do_he": KHOA, "cot_moi": "can-chot"}, "dai_ca_sua"),
    ("cot.da_chot", {"decision_id": "hr-d1", "cau_hoi": ["Khoá nào?"], "tra_loi": [KHOA]}, "da_chot"),
    ("cot.da_chot", {"decision_id": "hr-d1", "adr": MAT_KHAU, "cau_hoi": ["q"], "tra_loi": ["a"]}, "da_chot"),
    ("cot.tra_ve", {"gop_y": f"Dùng {MAT_KHAU}"}, "tra_ve"),
])
def test_nguon_cot_co_bi_mat_bi_bo(loai, du_lieu, nguon):
    with pytest.raises(LoiBiMat) as e:
        doc_dau_vao(sk(loai, du_lieu))
    assert e.value.loai_nguon == nguon and "Sentinel" not in str(e.value)


def test_nguon_agent_ghi_co_bi_mat_bi_bo():
    d = {"noi_dung": f"Token CI: {KHOA}", "nhan": [], "giao_id": "g-20261013-0042", "vai": "coder"}
    with pytest.raises(LoiBiMat) as e:
        doc_dau_vao(sk(LOAI_AGENT_GHI, d, tac_nhan=TAC_NHAN_NHO))
    assert e.value.loai_nguon == "agent" and "Sentinel" not in str(e.value)


@pytest.mark.parametrize("loai, du_lieu", [
    ("cot.dai_ca_sua", {"tieu_de": "Sửa ngày", "cot_he": "ai-lam", "cot_moi": "can-chot", "vi_sao": "Đụng tiền"}),
    ("cot.da_chot", {"decision_id": "hr-d1", "cau_hoi": ["Có VAT?"], "tra_loi": ["Có, 8%"]}),
    ("cot.tra_ve", {"gop_y": "Thiếu test biên ngày 31/12"}),
])
def test_nguon_sach_van_qua(loai, du_lieu):
    assert doc_dau_vao(sk(loai, du_lieu)) is not None


def test_ghi_nho_co_bi_mat_tu_choi_khong_ghi_su_kien(dv):  # noqa: F811
    with pytest.raises(LoiCongCu) as e:
        nhan_ghi_nho(dv, PHIEU, f"Khoá deploy là {KHOA}")
    assert "bí mật" in str(e.value) and "Sentinel" not in str(e.value)
    with closing(dv.mo_kho_sk()) as kho:
        assert kho.gan_day("hr-codex", LOAI_AGENT_GHI, 10) == []
    assert nhan_ghi_nho(dv, PHIEU, "Chạy test Fin bằng --filter").startswith("Đã nhận")
