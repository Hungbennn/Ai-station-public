import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.beads.bd import LoiBd
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.cot import keo_cot, thu_lai
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

V = "2026-10-13T01:00:00Z"


def nc(tmp_path, *beads, **kw):
    db = tmp_path / "sk.db"
    return NguCanhGhi(bd=BdGia(beads, **kw), kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an="hr")


def test_keo_ai_lam_sang_can_chot(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam", "b2b"]))
    n.kho.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": "Rõ", "da_ghi": True}, bead_id="hr-1")
    kq = keo_cot(n, "hr-1", cot="can-chot", vi_sao="Chạm giá", ma="ma-keo-0001", expected_version=V)
    assert set(n.bd.beads["hr-1"].labels) == {"b2b", "cot:can-chot", "cot-khoa"} and kq.lap_lai is False
    assert n.bd.goi == [("cap_nhat_nhan", "hr-1", ("cot:can-chot", "cot-khoa"), ("cot:ai-lam",), None)]
    sk = n.kho.moi_nhat("hr", "hr-1", "cot.dai_ca_sua")
    assert sk.du_lieu == {"tieu_de": "Việc", "cot_he": "cot:ai-lam", "cot_moi": "cot:can-chot", "ly_do_he": "Rõ",
                          "vi_sao": "Chạm giá", "nguon": "dashboard", "da_ghi": True, "ma_thao_tac": "ma-keo-0001"}
    assert sk.tac_nhan == "dai-ca/dashboard"


def test_hai_nhan_cot_sau_keo_con_dung_mot(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam", "cot:can-chot"]))
    keo_cot(n, "hr-1", cot="ai-lam", vi_sao=None, ma="ma-keo-0002", expected_version=V)
    assert sorted(n.bd.beads["hr-1"].labels) == ["cot-khoa", "cot:ai-lam"]
    sk = n.kho.moi_nhat("hr", "hr-1", "cot.dai_ca_sua")
    assert "vi_sao" not in sk.du_lieu and sk.du_lieu["cot_he"] is None


def test_bead_da_doi_thi_409_khong_ghi_gi(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    with pytest.raises(XungDot):
        keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0003", expected_version="2026-10-12T00:00:00Z")
    assert n.bd.goi == [] and n.kho_tt.lay("ma-keo-0003") is None


@pytest.mark.parametrize("labels,kw", [
    (["cot:ai-lam"], {"issue_type": "epic"}), (["cot:cho-review"], {}), ([], {}), (["can-spec"], {}),
    (["cot:can-chot"], {}),
])
def test_khong_keo_duoc(tmp_path, labels, kw):
    n = nc(tmp_path, bead("hr-1", labels=labels, **kw))
    with pytest.raises(KhongHopLe):
        keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0004", expected_version=V)
    assert n.bd.goi == []


@pytest.mark.parametrize("nhan,dich", [("cot:can-chot", "ai-lam"), ("cot:ai-lam", "can-chot")])
def test_khong_keo_decision_mo(tmp_path, nhan, dich):
    n = nc(tmp_path, bead("hr-1", labels=[nhan], issue_type="decision"))
    with pytest.raises(KhongHopLe, match="Trả lời"):
        keo_cot(n, "hr-1", cot=dich, vi_sao=None, ma="ma-keo-0006", expected_version=V)
    assert n.bd.goi == [] and n.kho_tt.lay("ma-keo-0006") is None


def test_cot_dich_sai(tmp_path):
    with pytest.raises(KhongHopLe):
        keo_cot(nc(tmp_path, bead()), "hr-1", cot="cho-review", vi_sao=None, ma="ma-keo-0005", expected_version=V)


def test_bam_hai_lan_chi_ghi_mot_lan(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    a = keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0006", expected_version=V)
    b = keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0006", expected_version=V)
    assert a.lap_lai is False and b.lap_lai is True and n.bd.so_lan("cap_nhat_nhan") == 1
    assert len(n.kho.gan_day("hr", "cot.dai_ca_sua", 10)) == 1


def test_crash_sau_khi_bd_ghi_nhan_lam_tiep_khong_ghi_lai(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]), ra_loi_sau={"cap_nhat_nhan": 1})
    with pytest.raises(LoiBd):
        keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0007", expected_version=V)
    kq = keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0007", expected_version=V)
    assert kq.lap_lai is False and n.bd.so_lan("cap_nhat_nhan") == 1
    assert len(n.kho.gan_day("hr", "cot.dai_ca_sua", 10)) == 1
    assert kq.ket_qua["nhan"] == {"them": ["cot:can-chot", "cot-khoa"], "bo": ["cot:ai-lam"]}   # so với lúc đọc đầu


def test_thu_lai_ghi_su_kien_mot_lan(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    thu_lai(n, "hr-1", ma="ma-thulai-01", expected_version=V)
    thu_lai(n, "hr-1", ma="ma-thulai-01", expected_version=V)
    ds = n.kho.gan_day("hr", "cham_cot.thu_lai", 10)
    assert len(ds) == 1 and ds[0].du_lieu == {"ma_thao_tac": "ma-thulai-01"} and ds[0].tac_nhan == "dai-ca/dashboard"
    assert n.bd.goi == [] and n.kho.yeu_cau.nhan_su_kien_nguon("hr") == 1     # 1a nhận thành yêu cầu chấm lại
    with pytest.raises(XungDot):
        thu_lai(n, "hr-1", ma="ma-thulai-02", expected_version="2026-10-12T00:00:00Z")


@pytest.mark.parametrize("kw", [{"status": "closed"}, {"status": "deferred"}, {"issue_type": "epic"}])
def test_thu_lai_chan_bead_dong_hoan_hoac_epic(tmp_path, kw):
    n = nc(tmp_path, bead("hr-1", **kw))
    with pytest.raises(KhongHopLe):
        thu_lai(n, "hr-1", ma="ma-thulai-03", expected_version=V)
    assert n.kho.gan_day("hr", "cham_cot.thu_lai", 10) == [] and n.kho_tt.lay("ma-thulai-03") is None
