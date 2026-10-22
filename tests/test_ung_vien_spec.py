"""Ứng viên bước `spec` (spec 4 §5.1 "Bead feature", §8): đủ điều kiện, chưa có phiếu, còn ngân sách, đợt chưa hết."""
from pathlib import Path

from bead_gia import bead
from kho_phieu_gia import dat_phieu, kho_tam
from su_kien_gia import ds, ket_thuc, nhan, sk
from test_phieu_yeu_cau import mo_ta
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.du_an_giao import CauHinhGiao, NganSachBead, NganSachGiao
from tram.giao_viec.ung_vien_spec import liet_ke_spec

DA = DuAn("hr-codex", Path("/r"), None, {})
F = bead("hr-f", issue_type="feature", labels=["can-spec"], description=mo_ta())


def lk(kho, *beads, san=None, da=DA):
    return liet_ke_spec(kho, da, list(beads), {b.id for b in beads} if san is None else san)


def test_feature_la_ung_vien_spec_khong_claim(tmp_path):
    kho = kho_tam(tmp_path)
    [u] = lk(kho, F, bead("hr-1", labels=["cot:ai-lam"]), bead("hr-g", issue_type="feature"))
    assert (u.bead.id, u.buoc, u.do, u.da_code) == ("hr-f", "spec", False, frozenset())


def test_co_phieu_bi_chan_hay_spec_vua_xong_thi_khong(tmp_path):
    kho = kho_tam(tmp_path)
    assert lk(kho, F, san=set()) == []
    p = dat_phieu(kho, bead_id="hr-f", buoc="spec")
    assert lk(kho, F) == []
    kho.db.execute("UPDATE phieu SET trang_thai = 'ket_thuc' WHERE giao_id = ?", (p.giao_id,))
    nhan(kho, "g-1", 1, buoc="spec", bead_id="hr-f")
    ket_thuc(kho, "g-1", 1, commit="c1c1c1c", buoc="spec", bead_id="hr-f")
    assert lk(kho, F) == []                                     # chờ tick chuyển sang cho-duyet-spec


def test_luot_bi_la_do_va_giao_lai(tmp_path):
    kho = kho_tam(tmp_path)
    nhan(kho, "g-1", 1, buoc="spec", bead_id="hr-f")
    ket_thuc(kho, "g-1", 1, ket_thuc="bi", ly_do="khe-tat", buoc="spec", bead_id="hr-f")
    [u] = lk(kho, F)
    assert u.do


def test_het_dot_sua_spec_hoac_het_ngan_sach(tmp_path):
    kho = kho_tam(tmp_path)
    for i in range(2):
        sk(kho, "spec.tra_ve", {"gop_y": f"lần {i}"}, bead_id="hr-f")
    assert lk(kho, F) == []
    (tmp_path / "b").mkdir()
    kho2 = kho_tam(tmp_path / "b")
    nhan(kho2, "g-1", 1, buoc="spec", bead_id="hr-f", ngan_sach={"so_lan_chay": 2, "phut": 45, "token_ra": 1})
    ket_thuc(kho2, "g-1", 1, ket_thuc="thu_hoi", buoc="spec", bead_id="hr-f")
    het = DuAn(**{**DA.__dict__, "giao": CauHinhGiao(ngan_sach=NganSachGiao(bead=NganSachBead(3, 3, 360)))})
    assert lk(kho2, F, da=het) == [] and lk(kho2, F) != []
