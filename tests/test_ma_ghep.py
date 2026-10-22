from datetime import timedelta

import pytest

from kho_phieu_gia import LUC, kho_tam
from tram.phieu.ma_ghep import GhepBiKhoa, MaGhepSai, cap_ma_ghep, doi_ma_ghep
from tram.phieu.may import cap_token_may, xac_thuc_may


def _loai(kho):
    return [r[0] for r in kho.db.execute("SELECT loai FROM su_kien WHERE du_an = '_tram' ORDER BY id")]


def test_cap_roi_doi_mot_lan_ra_token_may(tmp_path):
    kho = kho_tam(tmp_path)
    mg = cap_ma_ghep(kho, "C", luc=LUC)
    assert mg.may_id == "C" and mg.het_luc == "2026-10-13T03:10:00Z"
    assert len(mg.ma) == 14 and mg.ma[4] == mg.ma[9] == "-"
    may_id, token = doi_ma_ghep(kho, mg.ma.lower().replace("-", " "), luc=LUC + timedelta(minutes=9))
    assert may_id == "C" and xac_thuc_may(kho, token) == "C"
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, mg.ma, luc=LUC + timedelta(minutes=9))                 # dùng một lần
    bang = str(kho.db.execute("SELECT * FROM ma_ghep").fetchall()) + str(kho.db.execute(
        "SELECT du_lieu FROM su_kien").fetchall())
    assert mg.ma not in bang and mg.ma.replace("-", "") not in bang and token not in bang
    assert _loai(kho) == ["may.cap_ma", "may.ghep", "may.ghep_sai"]


def test_het_han_sau_10_phut_va_ma_moi_huy_ma_cu(tmp_path):
    kho = kho_tam(tmp_path)
    cu = cap_ma_ghep(kho, "C", luc=LUC)
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, cu.ma, luc=LUC + timedelta(minutes=10))
    cu = cap_ma_ghep(kho, "C", luc=LUC)
    moi = cap_ma_ghep(kho, "C", luc=LUC)
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, cu.ma, luc=LUC)
    assert doi_ma_ghep(kho, moi.ma, luc=LUC)[0] == "C"


def test_may_dang_co_token_khong_cap_ma(tmp_path):
    kho = kho_tam(tmp_path)
    cap_token_may(kho, "B", luc=LUC)
    with pytest.raises(ValueError, match="go-may"):
        cap_ma_ghep(kho, "B", luc=LUC)
    with pytest.raises(ValueError):
        cap_ma_ghep(kho, "C/x", luc=LUC)
    mg = cap_ma_ghep(kho, "C", luc=LUC)
    cap_token_may(kho, "C", luc=LUC)                                              # máy C được ghép đường khác
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, mg.ma, luc=LUC)


def test_sai_5_lan_trong_10_phut_khoa_va_huy_moi_ma_dang_cho(tmp_path):
    kho = kho_tam(tmp_path)
    mg = cap_ma_ghep(kho, "C", luc=LUC)
    for i in range(5):
        with pytest.raises(MaGhepSai):
            doi_ma_ghep(kho, "AAAA-AAAA-AAA" + str(i), luc=LUC + timedelta(seconds=i))
    with pytest.raises(GhepBiKhoa):
        doi_ma_ghep(kho, mg.ma, luc=LUC + timedelta(minutes=1))
    with pytest.raises(MaGhepSai):                                                # hết khoá nhưng mã đã bị huỷ
        doi_ma_ghep(kho, mg.ma, luc=LUC + timedelta(minutes=11))
    assert doi_ma_ghep(kho, cap_ma_ghep(kho, "C", luc=LUC + timedelta(minutes=11)).ma,
                       luc=LUC + timedelta(minutes=11))[0] == "C"
