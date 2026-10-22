from dataclasses import replace
from types import SimpleNamespace
import pytest
from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
from tram.cau_hinh.pham_vi_giao import danh_sach
from tram.giao_viec.noi_that import dung_bo_that


@pytest.mark.parametrize("ds", [[], "ben-station", [True], ["../hr"]])
def test_sai_pham_vi_khong_mo_rong(ds):
    with pytest.raises(ValueError):
        danh_sach({"du_an": ds}, "du_an")


def test_nap_cau_hinh_khong_tu_bat(tmp_path):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text("giao_viec:\n  du_an: [ben-station]\n")
    ch = nap_cau_hinh_giao_viec(p)
    assert not ch.bat and ch.du_an == ("ben-station",)
    assert not hasattr(ch, "bead")
    p.write_text("giao_viec:\n  bead: [bs-thu]\n")
    with pytest.raises(ValueError):
        nap_cau_hinh_giao_viec(p)


@pytest.mark.parametrize("bead_id", ["bs-mot", "bs-hai"])
def test_moi_bead_ben_duoc_xet_hr_khong_doc_claim_cap(tmp_path, monkeypatch, bead_id):
    from giao_viec_gia import dung, bug
    from tram.giao_viec import noi_that
    t = dung(tmp_path, bug(bead_id))
    try:
        ben = replace(t.da, ten="ben-station")
        monkeypatch.setattr(noi_that, "cac_du_an_that", lambda _: [t.da, ben])
        bo = dung_bo_that(CauHinhGiaoViec(du_an=("ben-station",)), t.bo.ch)
        doc = []
        def tao_bd(da):
            doc.append(da.ten)
            assert da.ten == "ben-station"
            return t.g
        bo = replace(bo, tao_bd=tao_bd, mo_kho=t.bo.mo_kho, kho_git=t.bo.kho_git, dong_ho=t.bo.dong_ho)
        assert [d.ten for d in bo.cac_du_an()] == ["ben-station"]
        dx = bo.chon("B/claude-1", None)
        assert dx is not None and dx.bead_id == bead_id and dx.du_an == "ben-station"
        assert t.g.beads[bead_id].status == "in_progress" and doc == ["ben-station"]
        assert not bo.con_hop_le(SimpleNamespace(du_an="hr-codex", bead_id="hr-1"))
        assert bo.con_hop_le(dx)
        monkeypatch.setattr(noi_that, "cac_du_an_that", lambda _: [])
        assert not bo.con_hop_le(dx)  # bat_ghi vừa tắt: nguồn đọc lại không còn dự án.
    finally:
        t.kho.close()
