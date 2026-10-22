from pathlib import Path

import pytest

from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.cau_hinh.usage import CauHinhUsage, nap_cau_hinh_usage

DU = """dai_ca_logins: [dai-ca@example.com]
usage:
  ccusage: /Users/tram/.tram/ccusage/node_modules/.bin/ccusage
  ccusage_phien_ban: "17.2.1"
  gia_usd_moi_trieu_token:
    claude-sonnet-5-5: {vao: 3, ra: 15, cache_doc: 0.3}
"""


def _ghi(tmp_path, noi_dung: str) -> Path:
    p = tmp_path / "cau-hinh.yaml"
    p.write_text(noi_dung, encoding="utf-8")
    return p


def test_mac_dinh_khi_thieu_file_hoac_thieu_khoa(tram_home_tam, tmp_path):
    assert nap_cau_hinh_usage() == CauHinhUsage()
    assert nap_cau_hinh_usage(_ghi(tmp_path, "ten_may_b: may-b\n")) == CauHinhUsage()


def test_doc_du_va_cau_hinh_tram_khong_bi_anh_huong(tmp_path):
    p = _ghi(tmp_path, DU)
    ch = nap_cau_hinh_usage(p)
    assert ch.ccusage == Path("/Users/tram/.tram/ccusage/node_modules/.bin/ccusage")
    assert ch.ccusage_phien_ban == "17.2.1"
    assert ch.gia == {"claude-sonnet-5-5": {"vao": 3.0, "ra": 15.0, "cache_doc": 0.3, "cache_ghi": 0.0}}
    assert nap_cau_hinh_tram(p).dai_ca_logins == ("dai-ca@example.com",)


@pytest.mark.parametrize("usage", [
    "[1]", "{la: 1}", "{ccusage: /x/ccusage}", "{ccusage_phien_ban: '1.2.3'}",
    "{ccusage: ccusage, ccusage_phien_ban: '1.2.3'}", "{ccusage: /a/../ccusage, ccusage_phien_ban: '1.2.3'}",
    "{ccusage: /x/ccusage, ccusage_phien_ban: latest}", "{ccusage: /x/ccusage, ccusage_phien_ban: 1.2}",
    "{gia_usd_moi_trieu_token: {m: {vao: 1}}}", "{gia_usd_moi_trieu_token: {m: {vao: 1, ra: -1}}}",
    "{gia_usd_moi_trieu_token: {m: {vao: 1, ra: true}}}", "{gia_usd_moi_trieu_token: {'m x': {vao: 1, ra: 1}}}",
])
def test_sai_bao_loi(tmp_path, usage):
    with pytest.raises(ValueError):
        nap_cau_hinh_usage(_ghi(tmp_path, f"usage: {usage}\n"))
