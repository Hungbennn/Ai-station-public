import json

import pytest

from tram.nho.cau_hinh_mcp import cau_hinh_phien_tay, cau_hinh_tho, mcp_json
from tram.nho.danh_tinh import H_AUTH, H_DU_AN, H_GIAO, H_MA
from tram.nho.pham_vi import LoiVungCap

URL = "https://may-b.tail1234.ts.net/nho/mcp"


def test_header_khop_ben_kiem_va_khong_chua_bi_mat():
    tho, tay = cau_hinh_tho(), cau_hinh_phien_tay("hr-codex", URL)
    assert {k.lower().encode() for k in tho["headers"]} == {H_GIAO, H_MA}
    assert {k.lower().encode() for k in tay["headers"]} == {H_AUTH, H_DU_AN}
    assert tho["url"] == "${TRAM_NHO_URL}" and tay["headers"]["Authorization"] == "Bearer ${TRAM_DAI_CA_MA}"
    assert json.loads(mcp_json(tay)) == {"mcpServers": {"tram-nho": tay}}


@pytest.mark.parametrize("du_an, url, loi", [("HR", URL, LoiVungCap), ("../x", URL, LoiVungCap),
                                             ("hr-codex", "http://may-b/nho/mcp", ValueError),
                                             ("hr-codex", "https://may-b.ts.net/mcp", ValueError)])
def test_phien_tay_tu_choi_du_an_hay_url_sai(du_an, url, loi):
    with pytest.raises(loi):
        cau_hinh_phien_tay(du_an, url)
