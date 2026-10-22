import pytest

from tram.cau_hinh.tram import CauHinhTelegram, CauHinhTram, nap_cau_hinh_tram


def _ghi(tmp_path, noi_dung: str):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text(noi_dung, encoding="utf-8")
    return p


def test_khong_co_file_la_mac_dinh_chi_doc(tram_home_tam):
    ch = nap_cau_hinh_tram()
    assert ch == CauHinhTram() and ch.dai_ca_logins == () and ch.telegram == CauHinhTelegram()


def test_doc_du_truong(tmp_path):
    p = _ghi(tmp_path, 'dai_ca_logins: ["a@b.c"]\nten_may_b: may-b.tail.ts.net\n'
                       'dashboard_url: "https://may-b.tail.ts.net/"\n'
                       'telegram: {chat_id: 123456789, gio_yen_lang: "23:00-07:00"}\n')
    ch = nap_cau_hinh_tram(p)
    assert ch.dai_ca_logins == ("a@b.c",) and ch.ten_may_b == "may-b.tail.ts.net"
    assert ch.telegram == CauHinhTelegram("123456789", "23:00-07:00")
    assert ch.dashboard_url == "https://may-b.tail.ts.net/"


@pytest.mark.parametrize("noi_dung", [
    'telegram: {gio_yen_lang: "23h-7h"}\n',
    'dai_ca_logins: "a@b.c"\n',
    'dai_ca_logins: ["", 3]\n',
    'dashboard_url: "http://may-b/"\n',
    'ten_may_b: "may b/x"\n',
    '- danh sách\n',
])
def test_sai_dang_bao_loi(tmp_path, noi_dung):
    with pytest.raises(ValueError):
        nap_cau_hinh_tram(_ghi(tmp_path, noi_dung))


def test_file_rong_la_mac_dinh(tmp_path):
    assert nap_cau_hinh_tram(_ghi(tmp_path, "")) == CauHinhTram()
