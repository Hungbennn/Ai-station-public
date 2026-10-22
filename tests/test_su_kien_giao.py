from kho_phieu_gia import LUC, kho_tam
from su_kien_gia import DA, cong_bo, ds, sk
from tram.giao_viec.su_kien import (cong_bo_cua_luot, cua_so, da_co, ghi_mot_lan, moi_nhat, ref_cong_bo,
                                    su_kien_bead)
from tram.su_kien.kho import KhoSuKien


def test_doc_su_kien_bead_theo_thu_tu_va_loc_dung_bead(tmp_path):
    kho = kho_tam(tmp_path)
    a = sk(kho, "x.a", {"n": 1})
    sk(kho, "x.a", {"n": 2}, bead_id="hr-2")
    b = sk(kho, "x.b", {"n": 3})
    sk(kho, "x.a", {"n": 4}, du_an="khac")
    d = su_kien_bead(kho, DA, "hr-1")
    assert [(s.id, s.loai, s.du_lieu) for s in d] == [(a, "x.a", {"n": 1}), (b, "x.b", {"n": 3})]
    assert moi_nhat(d, "x.a").id == a and moi_nhat(d, "x.b", lambda s: s.du_lieu["n"] > 5) is None


def test_cua_so_bat_dau_sau_tra_ve_gan_nhat(tmp_path):
    kho = kho_tam(tmp_path)
    sk(kho, "kiem.lai", {})
    sk(kho, "cot.tra_ve", {"gop_y": "a"})
    sk(kho, "kiem.lai", {})
    tv = sk(kho, "cot.tra_ve", {"gop_y": "b"})
    sau = sk(kho, "giao.nhan", {})
    assert [s.id for s in cua_so(ds(kho))] == [sau] and tv < sau


def test_ref_cong_bo_va_theo_luot(tmp_path):
    kho = kho_tam(tmp_path)
    assert ref_cong_bo(ds(kho)) is None
    cong_bo(kho, 1, "aaaaaaa")
    cong_bo(kho, 3, "ccccccc")
    cong_bo(kho, 1, "bbbbbbb")
    d = ds(kho)
    assert ref_cong_bo(d) == "bbbbbbb" and cong_bo_cua_luot(d, 1) == "bbbbbbb"
    assert cong_bo_cua_luot(d, 3) == "ccccccc" and cong_bo_cua_luot(d, 2) is None


def test_ghi_mot_lan_theo_khoa_va_tac_nhan(tmp_path):
    kho = kho_tam(tmp_path)
    i = ghi_mot_lan(kho, DA, "bead.dong", {"du_an": DA, "bead_id": "hr-1"}, bead_id="hr-1", luc=LUC,
                    khoa=("bead_id",))
    assert i and ghi_mot_lan(kho, DA, "bead.dong", {"du_an": DA, "bead_id": "hr-1"}, bead_id="hr-1", luc=LUC,
                             khoa=("bead_id",)) is None
    assert da_co(kho, DA, "bead.dong", {"bead_id": "hr-1"}) and not da_co(kho, DA, "bead.dong", {"bead_id": "x"})
    s = KhoSuKien(tmp_path / "su-kien.db").gan_day(DA, "bead.dong", 5)
    assert len(s) == 1 and s[0].tac_nhan == "tram/giao-viec" and s[0].bead_id == "hr-1"
