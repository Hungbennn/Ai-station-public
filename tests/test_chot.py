import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import PhuThuoc
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chot import CAU_CHUNG, chot
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

V = "2026-10-13T01:00:00Z"
HOI = ["Giá gồm VAT?", "Áp từ ngày nào?"]


def nc(tmp_path, *, labels=("cot:can-chot", "cot-khoa"), cau_hoi=HOI, **kw):
    db = tmp_path / "sk.db"
    n = NguCanhGhi(bd=BdGia([bead("hr-5", title="Giá tour", labels=labels)], **kw),
                   kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an="hr")
    if cau_hoi is not None:
        n.kho.ghi("hr", "cham_cot.ket_qua", {"cot": "can-chot", "ly_do": "Chạm giá", "cau_hoi": cau_hoi,
                                             "da_ghi": True}, bead_id="hr-5")
    return n


def _decision(n):
    return [b for b in n.bd.beads.values() if b.issue_type == "decision"]


def _chot(n, ma, tra_loi=("a", "b"), adr=None, version=V):
    return chot(n, "hr-5", tra_loi=list(tra_loi) if tra_loi is not None else None, adr=adr, ma=ma,
                expected_version=version)


def test_chot_tra_loi_du_buoc(tmp_path):
    n = nc(tmp_path)
    kq = _chot(n, "ma-chot-0001", tra_loi=["Có VAT", " Từ 1/11 "])
    (d,) = _decision(n)
    assert kq.ket_qua["tao_decision"] == d.id and kq.lap_lai is False
    assert d.title == "Chốt: Giá tour" and d.status == "closed" and d.close_reason == "(1) Có VAT; (2) Từ 1/11"
    assert "Hỏi: Giá gồm VAT?\nĐáp: Có VAT" in d.description
    assert d.description.endswith("<!-- tram:ma_thao_tac=ma-chot-0001 -->")
    b = n.bd.beads["hr-5"]
    assert PhuThuoc(d.id, "blocks") in b.phu_thuoc
    assert not [x for x in b.labels if x.startswith("cot:") or x == "cot-khoa"]
    sk = n.kho.moi_nhat("hr", "hr-5", "cot.da_chot")
    assert sk.du_lieu == {"decision_id": d.id, "cau_hoi": HOI, "tra_loi": ["Có VAT", "Từ 1/11"],
                          "ma_thao_tac": "ma-chot-0001"}
    assert [g[0] for g in n.bd.goi] == ["tat_ca", "tao", "dong", "them_phu_thuoc", "cap_nhat_nhan"]


def test_chot_dan_adr(tmp_path):
    n = nc(tmp_path)
    _chot(n, "ma-chot-0002", tra_loi=None, adr="ADR-0012")
    (d,) = _decision(n)
    assert d.close_reason == "Theo ADR-0012" and "Dẫn ADR: ADR-0012" in d.description
    sk = n.kho.moi_nhat("hr", "hr-5", "cot.da_chot")
    assert sk.du_lieu["adr"] == "ADR-0012" and sk.du_lieu["tra_loi"] == []


def test_khong_co_cau_hoi_thi_mot_cau_chung(tmp_path):
    n = nc(tmp_path, cau_hoi=None)
    _chot(n, "ma-chot-0003", tra_loi=["Làm theo giá cũ"])
    assert n.kho.moi_nhat("hr", "hr-5", "cot.da_chot").du_lieu["cau_hoi"] == [CAU_CHUNG]


@pytest.mark.parametrize("tra_loi,adr", [
    (["chỉ một"], None), (["a", " "], None), (None, None), (["a", "b"], "ADR-0001"), (None, "ADR-12"),
])
def test_noi_dung_sai_luat_khong_ghi_gi(tmp_path, tra_loi, adr):
    n = nc(tmp_path)
    with pytest.raises(KhongHopLe):
        _chot(n, "ma-chot-0004", tra_loi=tra_loi, adr=adr)
    assert n.bd.goi == [] and n.kho_tt.lay("ma-chot-0004") is None


@pytest.mark.parametrize("labels", [("cot:ai-lam",), ("cot:can-chot", "tram:escalation"), ("cho-duyet-spec",)])
def test_bead_khong_chot_duoc(tmp_path, labels):
    with pytest.raises(KhongHopLe):
        _chot(nc(tmp_path, labels=labels), "ma-chot-0005")


def test_bead_da_doi_409(tmp_path):
    with pytest.raises(XungDot):
        _chot(nc(tmp_path), "ma-chot-0006", version="2026-10-12T00:00:00Z")


def test_bam_hai_lan_chi_mot_decision(tmp_path):
    n = nc(tmp_path)
    a = _chot(n, "ma-chot-0007")
    b = _chot(n, "ma-chot-0007")
    assert b.lap_lai is True and b.ket_qua == a.ket_qua
    assert n.bd.so_lan("tao") == 1 and len(_decision(n)) == 1


def test_crash_sau_bd_create_truoc_bd_close(tmp_path):
    n = nc(tmp_path, ra_loi_sau={"tao": 1})
    with pytest.raises(LoiBd):
        _chot(n, "ma-chot-0008")
    (d,) = _decision(n)
    assert d.status == "open" and set(n.kho_tt.lay("ma-chot-0008").buoc_da_xong) == {"ngu_canh"}
    kq = _chot(n, "ma-chot-0008")
    assert n.bd.so_lan("tao") == 1 and len(_decision(n)) == 1 and kq.ket_qua["tao_decision"] == d.id
    assert n.bd.beads[d.id].status == "closed" and PhuThuoc(d.id, "blocks") in n.bd.beads["hr-5"].phu_thuoc


def test_crash_sau_bd_close_truoc_dep_add(tmp_path):
    n = nc(tmp_path, ra_loi_truoc={"them_phu_thuoc": 1})
    with pytest.raises(LoiBd):
        _chot(n, "ma-chot-0009")
    kq = _chot(n, "ma-chot-0009")
    assert (n.bd.so_lan("tao"), n.bd.so_lan("dong"), n.bd.so_lan("them_phu_thuoc")) == (1, 1, 1)
    assert kq.lap_lai is False and len(n.kho.gan_day("hr", "cot.da_chot", 10)) == 1


def test_dep_add_da_co_khong_them_lan_hai(tmp_path):
    n = nc(tmp_path, ra_loi_sau={"them_phu_thuoc": 1})
    with pytest.raises(LoiBd):
        _chot(n, "ma-chot-0010")
    _chot(n, "ma-chot-0010")
    d = _decision(n)[0].id
    assert n.bd.so_lan("them_phu_thuoc") == 1
    assert n.bd.beads["hr-5"].phu_thuoc.count(PhuThuoc(d, "blocks")) == 1
