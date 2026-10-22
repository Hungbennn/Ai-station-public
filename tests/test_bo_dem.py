import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.api.bo_dem import BoDemBeads
from tram.beads.bd import LoiBd


class DongHo:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _bo(bd, dh=None):
    return BoDemBeads(lambda ten: bd, dong_ho=dh or DongHo())


def test_dem_trong_30_giay_roi_doc_lai():
    bd, dh = BdGia([bead()]), DongHo()
    bo = _bo(bd, dh)
    bo.lay("hr")
    dh.t = 29
    bo.lay("hr")
    assert bd.so_lan("tat_ca") == 1
    dh.t = 30.5
    bo.lay("hr")
    assert bd.so_lan("tat_ca") == 2


def test_danh_dau_cu_thi_doc_lai_ngay():
    bd = BdGia([bead()])
    bo = _bo(bd)
    bo.lay("hr")
    bo.danh_dau_cu("hr")
    bo.lay("hr")
    assert bd.so_lan("tat_ca") == 2


def test_phien_ban_chi_tang_khi_noi_dung_doi():
    bd = BdGia([bead()])
    bo = _bo(bd)
    assert bo.phien_ban("hr") == 0
    bo.lay("hr")
    assert bo.phien_ban("hr") == 1
    bo.danh_dau_cu("hr")
    bo.lay("hr")
    assert bo.phien_ban("hr") == 1
    bd.beads["hr-1"] = bead(labels=["cot:ai-lam"], updated_at="2026-10-13T02:00:00Z")
    bo.danh_dau_cu("hr")
    bo.lay("hr")
    assert bo.phien_ban("hr") == 2


def test_loi_bd_lan_ra_va_lan_sau_thu_lai():
    bd = BdGia([bead()], ra_loi_truoc={"tat_ca": 1})
    bo = _bo(bd)
    with pytest.raises(LoiBd):
        bo.lay("hr")
    assert [b.id for b in bo.lay("hr")] == ["hr-1"]
