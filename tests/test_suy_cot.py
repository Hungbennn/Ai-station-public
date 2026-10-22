from bead_gia import bead
from tram.su_kien.kho import KhoSuKien
from tram.suy.cot import (ViTri, cham_gan_nhat, hien_tren_bang, ly_do_khong_chot, ly_do_khong_keo,
                          ly_do_khong_tra_loi, suy_vi_tri, the_bead)
from tram.suy.lam_sach import lam_sach


def vt(*labels, **kw):
    return suy_vi_tri(bead(labels=labels, **kw), {})


def test_cot_theo_nhan():
    assert vt("cot:ai-lam") == ViTri("ai-lam", True, False, False, ())
    assert vt("cot:can-chot").hang == "can-chot"
    assert vt("cot:cho-review").hang == "cho-review"


def test_nhieu_nhan_cot_chon_an_toan_va_bao_lech():
    v = vt("cot:ai-lam", "cot:cho-review")
    assert v.hang == "cho-review" and v.lech and v.tu_nhan_cot
    v = vt("cot:la")
    assert v.hang == "chua-cham" and v.lech and not v.tu_nhan_cot


def test_nhan_luong_va_escalation():
    assert vt("can-spec") == ViTri("ai-lam", False, False, True, ())
    assert vt("cho-duyet-spec").hang == "can-chot"
    assert vt("theo-plan").hang == "theo-plan"
    assert vt("tram:escalation", issue_type="decision").hang == "can-chot"
    assert vt().hang == "chua-cham" and vt("b2b").hang == "chua-cham"


def test_epic_hang_rieng_ke_ca_co_nhan_cot():
    assert vt("cot:ai-lam", issue_type="epic").hang == "epic"


def test_bi_chan_mo_va_fail_closed():
    b = bead("hr-1", labels=["cot:ai-lam"], chan_boi=["hr-2", "hr-3", "hr-9"])
    theo_id = {x.id: x for x in (b, bead("hr-2"), bead("hr-3", status="closed"))}
    assert suy_vi_tri(b, theo_id).cho == ("hr-2", "hr-9")
    t = the_bead("hr", b, theo_id)
    assert t["mo"] is True and t["cho"] == ["hr-2", "hr-9"] and t["hang"] == "ai-lam"


def test_the_bead_truong_va_lam_sach():
    b = bead("hr-1", title="Sửa‮ giá\x00", labels=["cot:can-chot", "cot-khoa", "co-do"], priority=2,
             updated_at="2026-10-13T05:00:00Z")
    assert the_bead("hr", b, {"hr-1": b}) == {
        "du_an": "hr", "id": "hr-1", "tieu_de": "Sửa giá", "loai": "task", "uu_tien": 2, "hang": "can-chot",
        "mo": False, "cho": [], "khoa": True, "co_do": True, "lech": False, "khe_spec": False,
        "keo_duoc": True, "chot_duoc": True, "tra_loi_duoc": False, "updated_at": "2026-10-13T05:00:00Z"}


def _ly_do(ham, *labels, **kw):
    b = bead(labels=labels, **kw)
    return ham(b, suy_vi_tri(b, {}))


def test_luat_keo():
    assert _ly_do(ly_do_khong_keo, "cot:ai-lam") is None
    assert _ly_do(ly_do_khong_keo, "cot:can-chot", "cot-khoa") is None
    for labels, kw in ((("cot:ai-lam",), {"issue_type": "epic"}), (("cot:cho-review",), {}), ((), {}),
                       (("can-spec",), {}), (("cot:can-chot", "tram:escalation"), {"issue_type": "decision"}),
                       (("cot:ai-lam",), {"status": "closed"}), (("cot:ai-lam", "theo-plan"), {})):
        assert _ly_do(ly_do_khong_keo, *labels, **kw), labels


def test_luat_keo_chan_decision_mo():
    for nhan in ("cot:can-chot", "cot:ai-lam"):
        assert "Trả lời" in _ly_do(ly_do_khong_keo, nhan, issue_type="decision")
    b = bead("hr-1", labels=["cot:can-chot"], issue_type="decision")
    assert the_bead("hr", b, {"hr-1": b})["keo_duoc"] is False


def test_luat_chot():
    assert _ly_do(ly_do_khong_chot, "cot:can-chot", "cot-khoa") is None
    for labels, kw in ((("cot:ai-lam",), {}), (("cho-duyet-spec",), {}), (("cot:can-chot",), {"issue_type": "decision"}),
                       (("cot:can-chot",), {"issue_type": "epic"}), (("cot:can-chot", "tram:escalation"), {}),
                       (("cot:can-chot",), {"status": "deferred"})):
        assert _ly_do(ly_do_khong_chot, *labels, **kw), labels


def test_luat_tra_loi():
    assert ly_do_khong_tra_loi(bead(issue_type="decision", labels=["tram:escalation"])) is None
    assert ly_do_khong_tra_loi(bead(issue_type="decision", labels=["cot:can-chot"])) is None   # decision mở
    for kw in ({"issue_type": "task"}, {"issue_type": "decision", "status": "closed"},
               {"issue_type": "decision", "status": "deferred"}):
        assert ly_do_khong_tra_loi(bead(**kw)), kw


def test_hien_tren_bang():
    assert hien_tren_bang(bead(status="in_progress")) and hien_tren_bang(bead(status="blocked"))
    assert not hien_tren_bang(bead(status="closed")) and not hien_tren_bang(bead(status="deferred"))


def test_cham_gan_nhat_bo_ket_qua_bi_huy(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    assert cham_gan_nhat(k, "hr", "hr-1") is None
    k.ghi("hr", "cham_cot.ket_qua", {"ly_do": "đúng"}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"ly_do": "huỷ", "huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    assert cham_gan_nhat(k, "hr", "hr-1").du_lieu["ly_do"] == "đúng"


def test_lam_sach_loc_ky_tu():
    assert lam_sach("a\x00b‮c⁦d​e­f\ng\th") == "abcdef\ng\th"
    assert lam_sach("Tiếng Việt có dấu") == "Tiếng Việt có dấu"


def test_lam_sach_cat_do_dai_va_none():
    assert lam_sach("x" * 10, 5) == "xxxx…"
    assert lam_sach(None) == "" and lam_sach("abc", 5) == "abc"
