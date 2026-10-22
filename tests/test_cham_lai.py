"""Yêu cầu chấm lại khi decision mà bead phụ thuộc `blocks` đổi — spec 0+1a §5.6 (Q02)."""
from tram.beads.mo_hinh import Bead, PhuThuoc
from tram.cham_cot.cham_lai import anh_decision, decision_doi, phat_hien_decision_doi
from tram.su_kien.kho import KhoSuKien


def dec(id="hr-d", status="open", close_reason="", updated_at="2026-10-13T00:00:00Z"):
    return Bead(id, "Chốt?", "", "", "", "", status, "decision", (), (), updated_at, close_reason=close_reason)


def viec(id, *chan, loai="blocks", status="open", issue_type="task", labels=()):
    return Bead(id, "Việc", "", "", "", "", status, issue_type, tuple(labels),
                tuple(PhuThuoc(x, loai) for x in chan), "2026-10-12T00:00:00Z")


def kho(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def test_anh_decision_chi_lay_decision():
    assert anh_decision([dec("hr-d", "closed", "Có"), viec("hr-1")]) == {"hr-d": [True, "Có"]}


def test_decision_doi_ham_thuan():
    assert decision_doi(None, {"hr-d": [True, "Có"]}) == []
    assert decision_doi({"hr-d": [False, ""]}, {"hr-d": [False, ""]}) == []
    assert decision_doi({}, {"hr-d": [False, ""]}) == []  # decision mới, còn mở: chưa có gì để chấm lại
    assert decision_doi({}, {"hr-d": [True, ""]}) == ["hr-d"]
    assert decision_doi({"hr-d": [True, "A"]}, {"hr-d": [True, "B"]}) == ["hr-d"]
    assert decision_doi({"hr-d": [True, "A"]}, {}) == ["hr-d"]  # biến mất khỏi snapshot


def test_lan_dau_chi_luu_anh_khong_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    assert phat_hien_decision_doi(k, "hr", [dec("hr-d", "closed", "Có"), viec("hr-1", "hr-d")]) == 0
    assert k.yeu_cau.doc_anh_decision("hr") == {"hr-d": [True, "Có"]}
    assert k.yeu_cau.dang_cho("hr") == {}


def test_dong_decision_bang_bd_tay_bead_goc_khong_doi_van_co_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [dec(), viec("hr-1", "hr-d"), viec("hr-2")])
    dong = dec(status="closed", close_reason="Có", updated_at="2026-10-13T05:00:00Z")
    assert phat_hien_decision_doi(k, "hr", [dong, viec("hr-1", "hr-d"), viec("hr-2")]) == 1
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-1"]
    sk = k.moi_nhat("hr", "hr-1", "cham_cot.can_cham_lai")
    assert sk.du_lieu == {"nguon": "decision", "decision_ids": ["hr-d"]}


def test_mo_lai_decision_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [dec(status="closed", close_reason="Có"), viec("hr-1", "hr-d")])
    assert phat_hien_decision_doi(k, "hr", [dec(), viec("hr-1", "hr-d")]) == 1


def test_doi_close_reason_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [dec(status="closed", close_reason="A"), viec("hr-1", "hr-d")])
    assert phat_hien_decision_doi(k, "hr", [dec(status="closed", close_reason="B"), viec("hr-1", "hr-d")]) == 1


def test_chi_timestamp_decision_doi_khong_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [dec(status="closed", close_reason="A"), viec("hr-1", "hr-d")])
    lai = dec(status="closed", close_reason="A", updated_at="2026-10-14T00:00:00Z")
    assert phat_hien_decision_doi(k, "hr", [lai, viec("hr-1", "hr-d")]) == 0
    assert k.yeu_cau.dang_cho("hr") == {}


def test_decision_bien_mat_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [dec(status="closed", close_reason="A"), viec("hr-1", "hr-d")])
    assert phat_hien_decision_doi(k, "hr", [viec("hr-1", "hr-d")]) == 1


def test_decision_moi_da_dong_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [viec("hr-1")])
    assert phat_hien_decision_doi(k, "hr", [dec(status="closed", close_reason="Có"), viec("hr-1", "hr-d")]) == 1


def test_phu_thuoc_khong_phai_blocks_khong_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [dec(), viec("hr-1", "hr-d", loai="related")])
    assert phat_hien_decision_doi(k, "hr", [dec(status="closed"), viec("hr-1", "hr-d", loai="related")]) == 0


def test_mot_bead_hai_decision_doi_mot_yeu_cau(tmp_path):
    k = kho(tmp_path)
    phat_hien_decision_doi(k, "hr", [dec("hr-a"), dec("hr-b"), viec("hr-1", "hr-a", "hr-b")])
    moi = [dec("hr-a", "closed"), dec("hr-b", "closed"), viec("hr-1", "hr-a", "hr-b")]
    assert phat_hien_decision_doi(k, "hr", moi) == 1
    assert k.moi_nhat("hr", "hr-1", "cham_cot.can_cham_lai").du_lieu["decision_ids"] == ["hr-a", "hr-b"]


def test_bead_da_dong_hoac_epic_khong_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    ds = [viec("hr-1", "hr-d", status="closed"), viec("hr-2", "hr-d", issue_type="epic"), viec("hr-3", "hr-d")]
    phat_hien_decision_doi(k, "hr", [dec(), *ds])
    assert phat_hien_decision_doi(k, "hr", [dec(status="closed"), *ds]) == 1
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-3"]


def test_bead_bo_qua_co_dinh_theo_nhan_khong_tao_yeu_cau(tmp_path):
    k = kho(tmp_path)
    ds = [viec("hr-1", "hr-d", labels=["cot-khoa"]), viec("hr-2", "hr-d", labels=["cot:cho-review"]), viec("hr-3", "hr-d")]
    phat_hien_decision_doi(k, "hr", [dec(), *ds])
    assert phat_hien_decision_doi(k, "hr", [dec(status="closed"), *ds]) == 1
    assert list(k.yeu_cau.dang_cho("hr")) == ["hr-3"]
