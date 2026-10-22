import pytest

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.phieu.may import cap_token_may, go_may, xac_thuc_may


def test_cap_va_xac_thuc_chi_luu_bam(tmp_path):
    kho = kho_tam(tmp_path)
    tb, tc = cap_token_may(kho, "B", luc=LUC), cap_token_may(kho, "C", luc=LUC)
    assert len(tb) >= 43 and tb != tc
    assert xac_thuc_may(kho, tb) == "B" and xac_thuc_may(kho, tc) == "C"
    assert xac_thuc_may(kho, tb + "x") is None and xac_thuc_may(kho, "") is None and xac_thuc_may(kho, None) is None
    assert tb not in str(kho.db.execute("SELECT * FROM may_tho").fetchall())


def test_cap_lai_thay_token_cu(tmp_path):
    kho = kho_tam(tmp_path)
    cu = cap_token_may(kho, "B", luc=LUC)
    moi = cap_token_may(kho, "B", luc=LUC)
    assert xac_thuc_may(kho, cu) is None and xac_thuc_may(kho, moi) == "B"
    with pytest.raises(ValueError):
        cap_token_may(kho, "B/x", luc=LUC)


def test_go_may_vo_hieu_token_va_thu_hoi_phieu_cua_may_do(tmp_path):
    kho = kho_tam(tmp_path)
    tb = cap_token_may(kho, "B", luc=LUC)
    pb = dat_phieu(kho, "B/claude-1", bead_id="hr-1")
    pc = dat_phieu(kho, "C/claude-1", bead_id="hr-2")
    assert go_may(kho, "B", luc=LUC) == 1
    assert xac_thuc_may(kho, tb) is None
    assert kho.lay(pb.giao_id).ket_thuc == "thu_hoi" and kho.phieu_theo_giao_id(pb.giao_id)["ma_giao"] is None
    assert kho.lay(pc.giao_id).trang_thai == "hieu_luc"
    with pytest.raises(ValueError):
        go_may(kho, "B", luc=LUC)
    assert xac_thuc_may(kho, cap_token_may(kho, "B", luc=LUC)) == "B"            # ghép lại
