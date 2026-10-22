"""Escalation (spec 4 §9): bead decision chặn bead gốc, không trùng, đối soát sau sự cố (G5, G7-tương tự)."""
import pytest

from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC, kho_tam
from tram.beads.bd import LoiBd
from tram.giao_viec.escalation import NHAN, tao_escalation
from tram.su_kien.kho import KhoSuKien

DA = "hr-codex"


def moi(tmp_path, *beads, **kw):
    g = BdGia([bead("hr-1", title="Sửa UTF-8", status="in_progress"), *beads], **kw)
    return g, kho_tam(tmp_path)


def tao(g, kho, ly_do="agent-bi", nguon="g-1", cau_hoi="Vướng ở đâu"):
    return tao_escalation(g, kho, DA, g.beads["hr-1"], ly_do=ly_do, cau_hoi=cau_hoi, giao_id="g-1", nguon=nguon,
                          luc=LUC)


def test_tao_decision_chan_bead_goc_va_su_kien(tmp_path):
    g, kho = moi(tmp_path)
    e = tao(g, kho)
    esc = g.beads[e]
    assert esc.issue_type == "decision" and esc.labels == (NHAN,) and esc.title == "Bí: Sửa UTF-8"
    assert "ly_do: agent-bi" in esc.description and "bead_goc: hr-1" in esc.description and "Vướng" in esc.description
    assert [(p.depends_on_id, p.loai) for p in g.beads["hr-1"].phu_thuoc] == [(e, "blocks")]
    s = KhoSuKien(tmp_path / "su-kien.db").gan_day(DA, "escalation.tao", 5)
    assert len(s) == 1 and s[0].du_lieu["escalation_id"] == e and s[0].du_lieu["ly_do"] == "agent-bi"


def test_phat_lai_cung_nguon_khong_lam_gi(tmp_path):
    g, kho = moi(tmp_path)
    tao(g, kho)
    so = len(g.goi)
    assert tao(g, kho) is None and len(g.goi) == so


def test_trung_ly_do_dang_mo_them_notes_khong_tao_moi(tmp_path):
    g, kho = moi(tmp_path)
    e = tao(g, kho)
    e2 = tao(g, kho, nguon="g-2", cau_hoi="Lần hai")
    assert e2 == e and g.so_lan("tao") == 1 and "Lần hai" in g.beads[e].notes and g.so_lan("them_phu_thuoc") == 1
    e3 = tao(g, kho, ly_do="het-ngan-sach", nguon="tick")
    assert e3 != e and g.so_lan("tao") == 2


def test_escalation_cu_da_dong_thi_tao_moi(tmp_path):
    g, kho = moi(tmp_path)
    e = tao(g, kho)
    g.dong(e, "Làm cách B")
    assert tao(g, kho, nguon="g-2") != e


def test_crash_sau_bd_create_doi_soat_khong_tao_trung(tmp_path):
    g, kho = moi(tmp_path, ra_loi_sau={"tao": 1})
    with pytest.raises(LoiBd):
        tao(g, kho)
    assert tao(g, kho) is not None and g.so_lan("tao") == 1 and g.so_lan("them_phu_thuoc") == 1


def test_dau_doi_soat_trong_bead_khac_khong_thay_decision(tmp_path):
    from tram.giao_viec.escalation import ma_escalation
    ma = ma_escalation("hr-codex", "hr-1", "agent-bi", "g-1")
    g, kho = moi(tmp_path, bead("hr-gia", description=f"<!-- ma_thao_tac: {ma} -->", status="closed"))
    esc = tao(g, kho)
    assert esc != "hr-gia" and g.beads[esc].issue_type == "decision"


def test_ly_do_la_bi_tu_choi(tmp_path):
    g, kho = moi(tmp_path)
    with pytest.raises(ValueError):
        tao(g, kho, ly_do="tu-che")


@pytest.mark.parametrize("ly_do", ["agent-bi", "agent-can-hoi", "can-thao-tac-nguy-hiem"])
@pytest.mark.parametrize("gop", [False, True])
@pytest.mark.parametrize("noi_dung", ["password=gia-lap-chi-de-test", "x " * 2100 + "password=gia-lap-chi-de-test"],
                         ids=["ngan", "sau-moc-cat"])
def test_ly_do_co_bi_mat_van_tao_escalation_nhung_khong_chep(tmp_path, ly_do, gop, noi_dung):
    g, kho = moi(tmp_path)
    if gop:
        tao(g, kho, ly_do=ly_do, nguon="truoc")
    e = tao(g, kho, ly_do=ly_do, nguon="sau", cau_hoi=noi_dung)
    esc = g.beads[e]
    van_ban = esc.notes if gop else esc.description
    assert "Nội dung có dấu hiệu bí mật đã được ẩn; Đại ca xem lại yêu cầu." in van_ban
    assert "gia-lap-chi-de-test" not in repr(g.goi)
    assert g.so_lan("tao") == 1
    assert e in [p.depends_on_id for p in g.beads["hr-1"].phu_thuoc]
