from bead_gia import bead
from tram.bao_tin.nguon import anh_tu_beads, so_quet_loi_lien_tiep, tin_tu_anh, tin_tu_su_kien
from tram.bao_tin.tin import Tin
from tram.su_kien.kho import KhoSuKien


def test_tin_khi_nhan_moi_xuat_hien():
    truoc = anh_tu_beads([bead("hr-1"), bead("hr-2", labels=["co-do"])])
    sau = [bead("hr-1", labels=["cot:cho-review", "co-do"]), bead("hr-2", labels=["co-do"]),
           bead("hr-3", issue_type="feature", labels=["cho-duyet-spec"]),
           bead("hr-4", status="closed", labels=["cot:cho-review"])]
    assert tin_tu_anh("hr", truoc, sau) == [Tin("cho_review", "hr", "hr-1"), Tin("co_do", "hr", "hr-1"),
                                            Tin("spec_cho_duyet", "hr", "hr-3")]


def test_escalation_moi_hoac_mo_lai():
    esc = {"issue_type": "decision", "labels": ["tram:escalation"]}
    assert tin_tu_anh("hr", {}, [bead("hr-9", **esc)]) == [Tin("escalation", "hr", "hr-9")]
    assert tin_tu_anh("hr", anh_tu_beads([bead("hr-9", **esc)]), [bead("hr-9", **esc)]) == []
    da_dong = anh_tu_beads([bead("hr-9", status="closed", **esc)])
    assert tin_tu_anh("hr", da_dong, [bead("hr-9", **esc)]) == [Tin("escalation", "hr", "hr-9")]


def test_tin_tu_su_kien(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("_tram", "estop.bat", {})
    k.ghi("_tram", "estop.tat", {})
    k.ghi("hr", "cham_cot.bo_qua", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {}, bead_id="hr-1")
    assert [t for s in k.sau_id(0, 10) for t in tin_tu_su_kien(s, k)] == [
        Tin("estop_bat", "_tram"), Tin("estop_tat", "_tram"), Tin("tram_loi", "hr", "hr-1")]


def test_quet_loi_3_lan_lien_moi_bao(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    for _ in range(2):
        k.ghi("hr", "quet.loi", {"loi": "x"})
    assert so_quet_loi_lien_tiep(k, "hr") == 2
    assert tin_tu_su_kien(k.gan_day("hr", "quet.loi", 1)[0], k) == []
    k.ghi("hr", "quet.loi", {"loi": "x"})
    assert tin_tu_su_kien(k.gan_day("hr", "quet.loi", 1)[0], k) == [Tin("tram_loi", "hr")]
    k.ghi("hr", "quet.xong", {})
    k.ghi("hr", "quet.loi", {"loi": "x"})
    assert so_quet_loi_lien_tiep(k, "hr") == 1
