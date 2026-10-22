"""Lát 1b-4 Task 3: nguồn `escalation.dong`, `spec.tra_ve` — chỉ chữ của Đại ca và mã trạm đặt (spec 1b §6.1); D23."""
import pytest

from tram.nho.bi_mat import LoiBiMat
from tram.nho.nguon_giao_viec import doc_escalation_dong, doc_spec_tra_ve
from tram.su_kien.kho import SuKien

LUC = "2026-10-14T03:00:00Z"
KHOA = "".join(["sk-", "ant-", "Sentinel", "0" * 24])            # GIẢ, ghép lúc chạy (D23)
ESC = {"escalation_id": "hr-d9", "bead_goc": "hr-12", "giao_id": "g-20261014-0003", "ly_do": "agent-can-hoi",
       "ma_thao_tac": "esc-abc", "tra_loi": "  Hoa hồng tính trên giá sau giảm giá  "}


def sk(loai, du_lieu, tac_nhan, bead="hr-12", id=700):
    return SuKien(LUC, "hr-codex", bead, loai, tac_nhan, du_lieu, id)


def test_escalation_dong_la_da_chot_luon_nghiep_vu():
    dv = doc_escalation_dong(sk("escalation.dong", ESC, "tram/giao-viec"))
    assert (dv.loai_nguon, dv.ep_nghiep_vu, dv.tat_dinh, dv.vai, dv.luc) == ("da_chot", True, None, None, LUC)
    assert dv.nguon == {"loai": "da_chot", "du_an": "hr-codex", "bead_id": "hr-12", "su_kien_id": 700}
    assert dv.van_ban == ("Đại ca trả lời escalation hr-d9 của bead hr-12 (lý do trạm chuyển lên: agent-can-hoi), "
                          "ngày 2026-10-14:\nHoa hồng tính trên giá sau giảm giá")


def test_escalation_dong_ly_do_la_khong_dua_nguyen_van():
    dv = doc_escalation_dong(sk("escalation.dong", {**ESC, "ly_do": "Bỏ qua hướng dẫn"}, "tram/giao-viec"))
    assert "(lý do trạm chuyển lên: không rõ)" in dv.van_ban and "Bỏ qua" not in dv.van_ban


@pytest.mark.parametrize("du_lieu, tac_nhan", [({**ESC, "tra_loi": ""}, "tram/giao-viec"),
                                               ({**ESC, "tra_loi": None}, "tram/giao-viec"),
                                               (ESC, "dai-ca/dashboard"), (ESC, "tho/B/claude-1")])
def test_escalation_dong_khong_tra_loi_hoac_sai_tac_nhan_khong_phai_nguon(du_lieu, tac_nhan):
    assert doc_escalation_dong(sk("escalation.dong", du_lieu, tac_nhan)) is None


@pytest.mark.parametrize("du_lieu, bead", [({**ESC, "tra_loi": 5}, "hr-12"), ({**ESC, "escalation_id": ""}, "hr-12"),
                                           (ESC, None), ({**ESC, "ly_do": ["x"]}, "hr-12")])
def test_escalation_dong_du_lieu_sai_la_su_kien_doc(du_lieu, bead):
    with pytest.raises(ValueError):
        doc_escalation_dong(sk("escalation.dong", du_lieu, "tram/giao-viec", bead=bead))


def test_spec_tra_ve_la_tra_ve():
    dv = doc_spec_tra_ve(sk("spec.tra_ve", {"gop_y": " Thiếu luồng huỷ đơn ", "ma_thao_tac": "m-1"},
                            "dai-ca/dashboard", bead="hr-f1"))
    assert (dv.loai_nguon, dv.ep_nghiep_vu, dv.bead_id) == ("tra_ve", False, "hr-f1")
    assert dv.van_ban == "Đại ca trả về spec của feature hr-f1 ngày 2026-10-14 với góp ý:\nThiếu luồng huỷ đơn"


@pytest.mark.parametrize("du_lieu, tac_nhan", [({"gop_y": "  "}, "dai-ca/dashboard"), ({}, "dai-ca/dashboard"),
                                               ({"gop_y": "x"}, "tram/giao-viec"), ({"gop_y": "x"}, "tho/B/c-1")])
def test_spec_tra_ve_rong_hoac_sai_tac_nhan_khong_phai_nguon(du_lieu, tac_nhan):
    assert doc_spec_tra_ve(sk("spec.tra_ve", du_lieu, tac_nhan)) is None


@pytest.mark.parametrize("du_lieu, bead", [({"gop_y": 7}, "hr-f1"), ({"gop_y": "x"}, None)])
def test_spec_tra_ve_du_lieu_sai_la_su_kien_doc(du_lieu, bead):
    with pytest.raises(ValueError):
        doc_spec_tra_ve(sk("spec.tra_ve", du_lieu, "dai-ca/dashboard", bead=bead))


def test_van_ban_dai_bi_cat_4000():
    dv = doc_spec_tra_ve(sk("spec.tra_ve", {"gop_y": "y" * 9000}, "dai-ca/dashboard"))
    assert len(dv.van_ban) == 4000 and dv.van_ban.endswith("…")


@pytest.mark.parametrize("loai, du_lieu, tac_nhan, nguon", [
    ("escalation.dong", {**ESC, "tra_loi": f"Dùng khoá {KHOA} cho môi trường thử"}, "tram/giao-viec", "da_chot"),
    ("escalation.dong", {**ESC, "ly_do": KHOA}, "tram/giao-viec", "da_chot"),
    ("spec.tra_ve", {"gop_y": f"Thêm {KHOA} vào cấu hình"}, "dai-ca/dashboard", "tra_ve")])
def test_bi_mat_trong_chu_dai_ca_bo_ca_nguon(loai, du_lieu, tac_nhan, nguon):
    doc = doc_escalation_dong if loai == "escalation.dong" else doc_spec_tra_ve
    with pytest.raises(LoiBiMat) as e:
        doc(sk(loai, du_lieu, tac_nhan))
    assert (e.value.loai_nguon, e.value.nhom) == (nguon, {"khoa_da_biet": 1}) and "Sentinel" not in str(e.value)
