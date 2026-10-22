import sys
from pathlib import Path

import pytest

from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.cau_hinh_chay import PATH_HE_THONG, doc_cau_hinh_chay

THO = """may_id: B
tram_api: http://127.0.0.1:7700
khe:
  - {ten: claude-1, cli: claude, principal: "user:tram-k-b-claude-1", thu_muc_cau_hinh: /Users/k1/.claude,
     ten_goi_nho: Claude 1, vai_uu_tien: [coder]}
"""


def test_khong_co_chay_la_mac_dinh_chua_chot(tmp_path):
    (tmp_path / "tho.yaml").write_text(THO)
    c = nap_cau_hinh_tho(tmp_path / "tho.yaml").chay
    assert c.day is None and c.han_chot_dung_mem_phut == 3 and c.nho_url is None and c.cong_cam == (7700,)
    assert c.path_cli == f"{Path(sys.executable).parent}:{PATH_HE_THONG}"


def test_doc_du_khoa_chay(tmp_path):
    (tmp_path / "tho.yaml").write_text(THO + "chay:\n  day: ref-tam\n  han_chot_dung_mem_phut: 5\n"
                                       "  nho_url: http://127.0.0.1:7710/mcp\n  thang_utilization: ti_le\n"
                                       "  path: /x/bin:/usr/bin\n  thu_muc_tram: /Users/tram/.tram\n"
                                       "  cong_cam: [7700, 3306]\n")
    c = nap_cau_hinh_tho(tmp_path / "tho.yaml").chay
    assert (c.day, c.han_chot_dung_mem_phut, c.thang_utilization, c.path_cli) == ("ref-tam", 5, "ti_le", "/x/bin:/usr/bin")
    assert c.nho_url.endswith(":7710/mcp") and str(c.thu_muc_tram) == "/Users/tram/.tram" and c.cong_cam == (7700, 3306)


@pytest.mark.parametrize("raw", [{"day": "github"}, {"nho_url": "https://x/mcp"}, {"thang_utilization": "%"},
                                 {"han_chot_dung_mem_phut": 0}, {"lan_chay_moi_gio": True}, {"la": 1},
                                 {"thu_muc_tram": "tuong-doi"}, {"cong_cam": [0]}, [1]])
def test_chay_sai(raw):
    with pytest.raises(ValueError):
        doc_cau_hinh_chay(raw)
