from pathlib import Path
import pytest
from he_gia import HeGia
from tram.chu.cai_dat_tho import lap_ke_hoach_tho
from tram.giao_viec.principal_kiem import tu_cach_ly


def lap(tmp_path, khe):
    he = HeGia()
    return lap_ke_hoach_tho(uv="uv", repo=tmp_path, tram="hung", quan_ly="tram-tho", khe=khe,
        co_che="user", kiem=tu_cach_ly("user:tram-kiem"), thu_muc_kiem=tmp_path / "kiem",
        quan_sat=he.quan_sat, chay=he.chay, chi_tho=True, giu_tat=True)


def test_khong_dung_uq_khong_nap(tram_home_tam, tmp_path):
    kh = lap(tmp_path, {"claude-1": "tram-khe1", "claude-2": "tram-khe2"})
    assert kh.lenh == [] and kh.han_lenh == 30
    assert {p.name for p in kh.tep} == {"tram-tho.sudoers", "vn.tram.tho.plist"}
    assert not any("tram-kiem" in mo or "quan-kiem" in mo for mo, _ in kh.buoc)
    assert "tram-khe1,tram-khe2" in next(v.decode() for p, v in kh.tep.items() if p.suffix == ".sudoers")


@pytest.mark.parametrize("users", [("tram-khe1", "tram-khe1"), ("hung", "tram-khe2"),
    ("tram-tho", "tram-khe2"), ("tram-kiem", "tram-khe2"), ("tram-quan-kiem", "tram-khe2")])
def test_tu_choi_dung_chung_uid_chuc_nang(tram_home_tam, tmp_path, users):
    with pytest.raises(ValueError, match="user riêng"):
        lap(tmp_path, dict(zip(("claude-1", "claude-2"), users)))


def test_han_ap_ca_buoc_tao_tai_nguyen(tram_home_tam, tmp_path):
    he, da = HeGia(), []
    def chay(argv, **kw):
        da.append(kw.get("timeout"))
        return he.chay(argv, **kw)
    kh = lap_ke_hoach_tho(uv="uv", repo=tmp_path, tram="hung", quan_ly="tram-tho",
                         khe={"claude-1": "tram-khe1", "claude-2": "tram-khe2"},
                         co_che="user", chi_tho=True, giu_tat=True, quan_sat=he.quan_sat, chay=chay)
    kh.buoc[1][1]()
    assert da and all(x == 30 for x in da)
