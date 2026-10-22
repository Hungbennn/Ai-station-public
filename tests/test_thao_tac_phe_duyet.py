import pytest

from bd_gia import BdGia
from bead_gia import bead, notes_ban_giao
from duyet_merge_gia import URL, tao
from tram.beads.bd import LoiBd
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe
from tram.thao_tac.phe_duyet import duyet, tra_loi_decision, tra_ve

V = "2026-10-13T01:00:00Z"


def nc(tmp_path, *beads, **kw):
    db = tmp_path / "sk.db"
    return NguCanhGhi(bd=BdGia(beads, **kw), kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an="hr")


def test_duyet_khong_pr(tmp_path):
    t = tao(tmp_path, da_vao=True)
    n = t.n
    kq = duyet(n, "hr-2", ma="ma-duyet-001", expected_version=V)
    b = n.bd.beads["hr-2"]
    assert b.status == "closed" and b.close_reason == f"Đại ca duyệt — commit {t.commit[:7]} đã vào main"
    assert kq.ket_qua == {"dong": {"pr": None}}


def test_duyet_co_pr_ghi_ro_la_thao_tac_tay(tmp_path):
    t = tao(tmp_path, pr=URL)
    t.pr.update(state="MERGED", mergedAt=V)
    n = t.n
    duyet(n, "hr-2", ma="ma-duyet-002", expected_version=V)
    ly_do = n.bd.beads["hr-2"].close_reason
    assert "https://github.com/o/r/pull/7" in ly_do and "thao tác tay" in ly_do and "không phải bằng chứng máy" in ly_do


def test_duyet_thieu_vao_cot_3_tu_choi_khong_ghi(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"], notes=notes_ban_giao(luot="x")))
    with pytest.raises(KhongHopLe, match="bead.vao_cot_3"):
        duyet(n, "hr-2", ma="ma-duyet-003", expected_version=V)
    assert n.bd.beads["hr-2"].status == "open" and n.bd.goi == []
    assert n.kho_tt.lay("ma-duyet-003") is None


def test_spec_khong_di_duong_cot_3_khong_ghi_gi(tmp_path):
    """bs-2bd.1.7: không có `nguon_spec` (chỉ ở test giả — tram-api thật luôn có) thì bead chờ duyệt spec bị từ chối
    422 như bead ngoài cột 3, không còn 501 "nối ở phần 4b" — kể cả khi bead mang nhãn cột 3."""
    n = nc(tmp_path, bead("hr-4", issue_type="feature", labels=["cho-duyet-spec", "cot:cho-review"]))
    with pytest.raises(KhongHopLe, match="spec"):
        duyet(n, "hr-4", ma="ma-duyet-004", expected_version=V, expected_commit="abc", digest_bead="d")
    with pytest.raises(KhongHopLe, match="spec"):
        tra_ve(n, "hr-4", gop_y="x", ma="ma-trave-004", expected_version=V)
    assert n.bd.goi == [] and n.kho_tt.lay("ma-duyet-004") is None


def test_duyet_khong_phai_cot_3(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    with pytest.raises(KhongHopLe):
        duyet(n, "hr-1", ma="ma-duyet-005", expected_version=V)


def test_tra_ve_go_nhan_ghi_gop_y_va_su_kien(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review", "cot-khoa", "b2b"]))
    tra_ve(n, "hr-2", gop_y="Thiếu test biên", ma="ma-trave-001", expected_version=V)
    b = n.bd.beads["hr-2"]
    assert b.labels == ("b2b",) and b.notes.startswith("[dai-ca/dashboard ")
    assert "Trả về: Thiếu test biên (ma_thao_tac ma-trave-001)" in b.notes
    sk = n.kho.moi_nhat("hr", "hr-2", "cot.tra_ve")
    assert sk.du_lieu == {"gop_y": "Thiếu test biên", "ma_thao_tac": "ma-trave-001"}


def test_tra_ve_hai_lan_cung_ma(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"]))
    tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-002", expected_version=V)
    assert tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-002", expected_version=V).lap_lai is True
    assert n.bd.so_lan("cap_nhat_nhan") == 1 and len(n.kho.gan_day("hr", "cot.tra_ve", 10)) == 1


def test_tra_ve_crash_sau_bd_update(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"]), ra_loi_sau={"cap_nhat_nhan": 1})
    with pytest.raises(LoiBd):
        tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-003", expected_version=V)
    tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-003", expected_version=V)
    assert n.bd.so_lan("cap_nhat_nhan") == 1 and n.bd.beads["hr-2"].notes.count("ma_thao_tac ma-trave-003") == 1
    assert len(n.kho.gan_day("hr", "cot.tra_ve", 10)) == 1


def test_tra_ve_gop_y_rong(tmp_path):
    with pytest.raises(KhongHopLe):
        tra_ve(nc(tmp_path, bead("hr-2", labels=["cot:cho-review"])), "hr-2", gop_y="  ", ma="ma-trave-005",
               expected_version=V)


def test_tra_loi_decision(tmp_path):
    n = nc(tmp_path, bead("hr-3", issue_type="decision", labels=["tram:escalation"]))
    tra_loi_decision(n, "hr-3", tra_loi=" Làm theo hướng A ", ma="ma-traloi-01", expected_version=V)
    tra_loi_decision(n, "hr-3", tra_loi=" Làm theo hướng A ", ma="ma-traloi-01", expected_version=V)
    b = n.bd.beads["hr-3"]
    assert b.status == "closed" and b.close_reason == "Làm theo hướng A" and n.bd.so_lan("dong") == 1
    ds = n.kho.gan_day("hr", "escalation.tra_loi", 10)
    assert len(ds) == 1 and ds[0].bead_id == "hr-3"
    assert ds[0].du_lieu == {"escalation_id": "hr-3", "ma_thao_tac": "ma-traloi-01"}


def test_tra_loi_decision_mo_khong_phai_escalation(tmp_path):
    n = nc(tmp_path, bead("hr-8", issue_type="decision", labels=["cot:can-chot"]))
    tra_loi_decision(n, "hr-8", tra_loi="Chọn B", ma="ma-traloi-04", expected_version=V)
    b = n.bd.beads["hr-8"]
    assert b.status == "closed" and b.close_reason == "Chọn B"
    ds = n.kho.gan_day("hr", "escalation.tra_loi", 10)
    assert len(ds) == 1 and ds[0].du_lieu == {"escalation_id": "hr-8", "ma_thao_tac": "ma-traloi-04"}


def test_bead_hoan_khong_duyet_khong_tra_loi(tmp_path):
    n = nc(tmp_path, bead("hr-2", status="deferred", labels=["cot:cho-review"]),
           bead("hr-3", status="deferred", issue_type="decision", labels=["tram:escalation"]))
    with pytest.raises(KhongHopLe):
        duyet(n, "hr-2", ma="ma-duyet-006", expected_version=V)
    with pytest.raises(KhongHopLe):
        tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-006", expected_version=V)
    with pytest.raises(KhongHopLe):
        tra_loi_decision(n, "hr-3", tra_loi="x", ma="ma-traloi-05", expected_version=V)
    assert n.bd.goi == []


def test_tra_loi_khong_phai_decision_hoac_rong(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:can-chot"]),
           bead("hr-3", issue_type="decision", labels=["tram:escalation"]))
    with pytest.raises(KhongHopLe):
        tra_loi_decision(n, "hr-1", tra_loi="x", ma="ma-traloi-02", expected_version=V)
    with pytest.raises(KhongHopLe):
        tra_loi_decision(n, "hr-3", tra_loi="  ", ma="ma-traloi-03", expected_version=V)
