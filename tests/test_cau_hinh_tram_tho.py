import pytest

from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhThoTram, nap_cau_hinh_tram


def _ghi(tmp_path, noi_dung: str):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text(noi_dung, encoding="utf-8")
    return p


def test_mac_dinh_theo_spec(tram_home_tam):
    ch = nap_cau_hinh_tram()
    assert ch.han_muc == CauHinhHanMuc(90, 80, 6)
    assert ch.tho == CauHinhThoTram(6, 60, 60, 3, 10, 90)


def test_doc_han_muc_va_tho(tmp_path):
    ch = nap_cau_hinh_tram(_ghi(tmp_path, "han_muc: {ngung: 85, tuoi_toi_da_gio: 2.5}\n"
                                          "tho: {lan_chay_moi_gio: 4, phut_cau_dao: 30}\n"))
    assert ch.han_muc == CauHinhHanMuc(85, 80, 2.5)
    assert ch.tho.lan_chay_moi_gio == 4 and ch.tho.phut_cau_dao == 30 and ch.tho.lan_chay_moi_ngay == 60


@pytest.mark.parametrize("noi_dung", [
    "han_muc: {ngung: 0}\n", "han_muc: {ngung: 101}\n", "han_muc: {ngung: true}\n", "han_muc: {la: 1}\n",
    "han_muc: [90]\n", "tho: {lan_chay_moi_gio: 2.5}\n", "tho: {lan_chay_moi_ngay: 0}\n",
    "tho: {han_giu_phut: 1}\n", "tho: {mat_ket_noi_giay: '90'}\n",
])
def test_sai_bao_loi(tmp_path, noi_dung):
    with pytest.raises(ValueError):
        nap_cau_hinh_tram(_ghi(tmp_path, noi_dung))
