import pytest

from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
from tram.cau_hinh.cong_bo import nap_cau_hinh_cong_bo


def ghi(tmp_path, noi_dung):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text(noi_dung, encoding="utf-8")
    return p


def test_mac_dinh_chua_chot_gi(tmp_path, tram_home_tam):
    cb, cl = nap_cau_hinh_cong_bo(tmp_path / "khong.yaml"), nap_cau_hinh_cach_ly(tmp_path / "khong.yaml")
    assert cb.phuong_an is None and cb.kho_tho == {} and cb.thoi_gian_cho_giay == 60
    assert cl.kenh_ghi == "header" and cl.tram_kiem is None and cl.duong_socket == tram_home_tam / "api" / "api.sock"


def test_doc_du_khoa(tmp_path):
    p = ghi(tmp_path, "dai_ca_logins: [a@b]\ncong_bo:\n  phuong_an: kho-tho\n  kho_tho: {B: /Users/tram-tho/tram/kho}\n"
                      "  giu_toi_thieu_phut: 3\ncach_ly:\n  kenh_ghi: unix-socket\n"
                      "  socket: /Users/tram/.tram/api/a.sock\n"
                      "  tram_kiem: user:tram-kiem\n  db_nghiep_vu: ['127.0.0.1:3306']\n")
    cb, cl = nap_cau_hinh_cong_bo(p), nap_cau_hinh_cach_ly(p)
    assert cb.phuong_an == "kho-tho" and str(cb.kho_tho["B"]) == "/Users/tram-tho/tram/kho"
    assert cb.giu_toi_thieu_phut == 3 and cl.kenh_ghi == "unix-socket" and cl.tram_kiem == "user:tram-kiem"
    assert cl.db_nghiep_vu == ("127.0.0.1:3306",) and str(cl.duong_socket) == "/Users/tram/.tram/api/a.sock"


@pytest.mark.parametrize("noi_dung", [
    "cong_bo: {phuong_an: ca-hai}", "cong_bo: {phuong_an: kho-tho}", "cong_bo: {kho_tho: {B: tuong-doi}}",
    "cong_bo: {la: 1}", "cong_bo: {thoi_gian_cho_giay: 0}", "cong_bo: [1]"])
def test_cong_bo_sai(tmp_path, noi_dung):
    with pytest.raises(ValueError):
        nap_cau_hinh_cong_bo(ghi(tmp_path, noi_dung))


@pytest.mark.parametrize("noi_dung", [
    "cach_ly: {kenh_ghi: tcp}", "cach_ly: {socket: tuong-doi}", "cach_ly: {db_nghiep_vu: ['khong-cong']}",
    "cach_ly: {la: 1}", "- 1"])
def test_cach_ly_sai(tmp_path, noi_dung):
    with pytest.raises(ValueError):
        nap_cau_hinh_cach_ly(ghi(tmp_path, noi_dung))
