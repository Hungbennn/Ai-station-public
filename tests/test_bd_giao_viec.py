import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.beads.bd import Bd, LoiBd


def _bd(ra=""):
    goi = []
    return Bd("/r", actor="tram/giao-viec", runner=lambda a: goi.append(list(a)) or ra), goi


def test_san_sang_doc_id_tu_bd_ready():
    bd, goi = _bd('[{"id": "hr-1", "title": "a"}, {"id": "hr-2"}]')
    assert bd.san_sang() == {"hr-1", "hr-2"}
    assert goi == [["-C", "/r", "ready", "--json", "--limit", "0"]]


@pytest.mark.parametrize("ra", ["khong-json", '{"id": "x"}', '[{"ten": "x"}]'])
def test_san_sang_json_hong(ra):
    with pytest.raises(LoiBd):
        _bd(ra)[0].san_sang()


def test_nhan_viec_goi_claim_voi_actor():
    bd, goi = _bd()
    bd.nhan_viec("hr-1")
    assert goi == [["-C", "/r", "update", "hr-1", "--claim", "--actor", "tram/giao-viec"]]


def test_bd_gia_san_sang_loai_in_progress_va_bi_chan():
    g = BdGia([bead("hr-1"), bead("hr-2", status="in_progress"), bead("hr-3", chan_boi=["hr-1"]),
               bead("hr-4", chan_boi=["hr-9"]), bead("hr-5", status="closed"),
               bead("hr-6", chan_boi=["hr-5"])])
    assert g.san_sang() == {"hr-1", "hr-6"}


def test_bd_gia_nhan_viec_mot_lan():
    g = BdGia([bead("hr-1")])
    g.nhan_viec("hr-1")
    assert g.beads["hr-1"].status == "in_progress" and g.beads["hr-1"].assignee == "tram/giao-viec"
    with pytest.raises(LoiBd):
        g.nhan_viec("hr-1")
