import pytest

from tram.nho.nguon import doc_dau_vao
from tram.su_kien.kho import SuKien


def sk(loai, du_lieu, du_an="hr-codex", bead="hr-12", id=812):
    return SuKien("2026-10-13T02:00:00Z", du_an, bead, loai, "dai-ca/dashboard", du_lieu, id)


def test_dai_ca_sua_khong_vi_sao_tat_dinh_khong_llm():
    dv = doc_dau_vao(sk("cot.dai_ca_sua", {"tieu_de": "Sửa lỗi xuất PDF", "cot_he": "cot:ai-lam",
                                           "cot_moi": "cot:can-chot", "ly_do_he": "Rõ phạm vi", "da_ghi": True}))
    assert dv.tat_dinh == ('"Sửa lỗi xuất PDF": hệ xếp cot:ai-lam, Đại ca chuyển cot:can-chot. '
                           'Lý do hệ: Rõ phạm vi')
    assert dv.van_ban is None and not dv.ep_nghiep_vu and dv.loai_nguon == "dai_ca_sua"
    assert dv.luc == "2026-10-13T02:00:00Z"                    # giờ sự kiện nguồn, không phải giờ nạp
    assert dv.nguon == {"loai": "dai_ca_sua", "du_an": "hr-codex", "bead_id": "hr-12", "su_kien_id": 812}


def test_dai_ca_sua_cot_he_rong_va_noi_dung_dai_bi_cat():
    dv = doc_dau_vao(sk("cot.dai_ca_sua", {"tieu_de": "T", "cot_he": None, "cot_moi": "cot:ai-lam",
                                           "ly_do_he": "rất  dài\n" * 200}))
    assert "hệ xếp (chưa chấm)" in dv.tat_dinh and len(dv.tat_dinh) == 600 and dv.tat_dinh.endswith("…")


def test_dai_ca_sua_co_vi_sao_thi_dua_llm():
    dv = doc_dau_vao(sk("cot.dai_ca_sua", {"tieu_de": "T", "cot_he": "cot:ai-lam", "cot_moi": "cot:can-chot",
                                           "ly_do_he": "L", "vi_sao": "Chạm giá tour", "nguon": "dashboard"}))
    assert dv.tat_dinh is None and "Đại ca giải thích: Chạm giá tour" in dv.van_ban and "hr-12" in dv.van_ban


def test_da_chot_luon_nghiep_vu_ghep_hoi_dap_va_adr():
    dv = doc_dau_vao(sk("cot.da_chot", {"decision_id": "hr-d1", "cau_hoi": ["Hoa hồng tính trên giá nào?"],
                                        "tra_loi": ["Giá sau giảm giá"], "ma_thao_tac": "m"}))
    assert dv.ep_nghiep_vu and dv.loai_nguon == "da_chot"
    assert "Hỏi: Hoa hồng tính trên giá nào?\nĐáp: Giá sau giảm giá" in dv.van_ban and "2026-10-13" in dv.van_ban
    dv = doc_dau_vao(sk("cot.da_chot", {"decision_id": "hr-d2", "cau_hoi": ["Q"], "tra_loi": [], "adr": "ADR-0083"}))
    assert "Theo ADR-0083." in dv.van_ban


def test_tra_ve_lay_gop_y():
    dv = doc_dau_vao(sk("cot.tra_ve", {"gop_y": "Thiếu test biên", "ma_thao_tac": "m"}))
    assert dv.loai_nguon == "tra_ve" and dv.van_ban.endswith("Thiếu test biên") and not dv.ep_nghiep_vu
    assert doc_dau_vao(sk("cot.tra_ve", {"gop_y": "  "})) is None


@pytest.mark.parametrize("s", [
    sk("cham_cot.ket_qua", {"cot": "ai-lam"}), sk("escalation.tra_loi", {"escalation_id": "hr-3"}),
    sk("cot.dai_ca_sua", {"tieu_de": "x"}, du_an="_tram"), sk("nho.ghi", {"id": "m-1"}),
    sk("quet.xong", {}), sk("cot.da_chot", "khong-phai-dict"),
    sk("cot.tra_ve", {"gop_y": "x"}, du_an="HR Codex"), sk("cot.tra_ve", {"gop_y": "x"}, du_an="../y")])
def test_su_kien_khac_khong_phai_nguon(s):
    assert doc_dau_vao(s) is None
