import pytest

from tram.nho.pham_vi import (LoiVungCap, chia_nhom, du_an_cua, la_pham_vi, mo_rong, nhom_cua, pham_vi_du_an,
                              vung_cap_cham_cot)


def test_mo_rong_du_an_thanh_hai_nhanh_dang_khac_giu_nguyen():
    assert mo_rong(["/du-an/hr-codex", "/vai/coder", "/chung"]) == {
        "/du-an/hr-codex/nghiep-vu", "/du-an/hr-codex/cach-lam", "/vai/coder", "/chung"}
    assert mo_rong(["/du-an/hr/cach-lam"]) == {"/du-an/hr/cach-lam"}


@pytest.mark.parametrize("vung", [
    None, [], (), "/chung", ["/"], ["/du-an"], ["/du-an/"], ["/vai"], ["/vai/"], [""], ["/du-an/HR"],
    ["/du-an/hr/"], ["/du-an/hr/khac"], ["/du-an/hr/cach-lam/x"], ["/chung/x"], ["/du-an/hr", 3],
    ["/du-an/hr\n"], ["/du-an/hr", "/du-an"], ["du-an/hr"], ["/du-an/hr*"], ["/du-an/h r"]])
def test_vung_cap_sai_dang_tu_choi_ca_loi_goi(vung):
    with pytest.raises(LoiVungCap):
        mo_rong(vung)


def test_khong_so_tien_to():
    tap = mo_rong(["/du-an/hr"])
    assert "/du-an/hr-codex/cach-lam" not in tap and all(p.startswith("/du-an/hr/") for p in tap)


def test_la_pham_vi_chi_bon_dang():
    assert all(la_pham_vi(p) for p in ["/du-an/x/nghiep-vu", "/du-an/x/cach-lam", "/vai/qc", "/chung"])
    assert not any(la_pham_vi(p) for p in ["/du-an/x", "/vai", "/", "/chung/", None, "/du-an/x/khac"])


def test_nhom_va_chia_nhom():
    tap = mo_rong(["/du-an/x", "/vai/coder", "/chung"])
    assert chia_nhom(tap) == {"du-an": ["/du-an/x/cach-lam", "/du-an/x/nghiep-vu"], "vai": ["/vai/coder"],
                              "chung": ["/chung"]}
    assert list(chia_nhom(["/chung", "/du-an/x/cach-lam"])) == ["du-an", "chung"]
    assert nhom_cua("/vai/qc") == "vai" and nhom_cua("/chung") == "chung"


def test_dung_pham_vi_du_an_va_vung_cap_1a():
    assert pham_vi_du_an("hr-codex", "cach-lam") == "/du-an/hr-codex/cach-lam"
    with pytest.raises(LoiVungCap):
        pham_vi_du_an("hr-codex", "chung")
    with pytest.raises(LoiVungCap):
        pham_vi_du_an("../x", "cach-lam")
    assert vung_cap_cham_cot("hr-codex") == ["/du-an/hr-codex", "/vai/cham-cot", "/chung"]
    assert du_an_cua("/du-an/hr-codex/nghiep-vu") == "hr-codex" and du_an_cua("/chung") is None
