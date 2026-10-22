"""Ca biên trên main; SQLite/BdGia/remote Git cục bộ, không quota thật."""
import pytest
from dataclasses import replace
from test_pipeline import code_xong, TT, C1, Q1
from su_kien_gia import ds, nhan, cong_bo, ket_thuc, kiem, sk
from kho_phieu_gia import LUC, kho_tam
from test_escalation import moi, tao
from tram.beads.bd import LoiBd
from tram.giao_viec.pipeline import buoc_ke_tiep
from tram.giao_viec.tick_doc import ghi_escalation_dong, mo_chu_ky_con_thieu
from tram.giao_viec.hang_doi import viec_cua_pha


@pytest.mark.parametrize("doi,muon", [("khong", "qc"), ("ref-khac", "code"), ("luot-khac", "code"),
                                      ("digest", "code"), ("tra-ve", "code"), ("qc-dat", "cot_3")])
def test_bs_ecd_qc_cong_bo_roi_thu_hoi(tmp_path, doi, muon):
    from su_kien_gia import qc
    kho = kho_tam(tmp_path)
    code_xong(kho)
    kiem(kho, "g-1", C1)
    nhan(kho, "g-2", 2, buoc="qc")
    cong_bo(kho, 2, Q1)
    ket_thuc(kho, "g-2", 2, ket_thuc="thu_hoi", buoc="qc")
    if doi == "ref-khac":
        cong_bo(kho, 9, "eeeeeee")
    if doi == "luot-khac":
        nhan(kho, "g-3", 3, buoc="qc")
        ket_thuc(kho, "g-3", 3, ket_thuc="thu_hoi", buoc="qc")
    if doi == "tra-ve":
        sk(kho, "cot.tra_ve", {"gop_y": "sửa lại"})
    if doi == "qc-dat":
        qc(kho, "g-2", C1, Q1)
    tt = replace(TT, digest_tieu_chi="sha256:moi") if doi == "digest" else TT
    assert buoc_ke_tiep(ds(kho), tt) == muon


def test_bs_s52_escalation_dong_giua_crash_va_doi_soat(tmp_path):
    g, kho = moi(tmp_path, ra_loi_sau={"tao": 1})
    with pytest.raises(LoiBd):
        tao(g, kho)
    e = next(b.id for b in g.tat_ca() if b.issue_type == "decision")
    g.dong(e, "Đại ca đã trả lời")
    assert tao(g, kho) == e and g.so_lan("tao") == 1
    assert ghi_escalation_dong(kho, "hr-codex", g.tat_ca(), LUC) == 1
    assert mo_chu_ky_con_thieu(kho, "hr-codex", LUC) == 1
    assert tao(g, kho) is None
    assert ghi_escalation_dong(kho, "hr-codex", g.tat_ca(), LUC) == 0
    assert mo_chu_ky_con_thieu(kho, "hr-codex", LUC) == 0


def test_queue_loc_du_an_va_pha_truoc_limit(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich() as db:
        db.executemany("INSERT INTO cong_viec_cho(giao_id,du_an,bead_id,ket_thuc,su_kien_id,luc) "
                       "VALUES (?,?,?,?,?,?)", [(f"g-{i}", "khac", "b", "xong", i, "2026-10-13T00:00:00Z")
                                                for i in range(1001)])
        db.execute("INSERT INTO cong_viec_cho(giao_id,du_an,bead_id,ket_thuc,su_kien_id,luc) "
                   "VALUES ('can-xu-ly','hr-codex','hr-1','bi',2000,'2026-10-13T00:00:00Z')")
    assert [v.giao_id for v in viec_cua_pha(kho, "hr-codex", git=False, gioi_han=1)] == ["can-xu-ly"]
    assert viec_cua_pha(kho, "hr-codex", git=True) == []


def test_gate_adr_duoc_noi_vao_bo_chon(tmp_path):
    from giao_viec_gia import dung, bug
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.git_kiem import fetch
    t = dung(tmp_path, bug(description="schema ADR-0083"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    t.bo.cac_du_an = lambda: [da]
    fetch(t.k.kho)
    assert t.bo.chon("B/claude-1", None) is None and t.g.so_lan("nhan_viec") == 0
    t.bo.adr_hop_le = lambda d, b: True  # CHỈ DÙNG TRONG TEST; không phải adapter được duyệt.
    assert t.bo.chon("B/claude-1", None).bead_id == "hr-1"
