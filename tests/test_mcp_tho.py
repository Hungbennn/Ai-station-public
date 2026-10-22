import json
import tomllib
from pathlib import Path

import pytest

from tram.nho.cau_hinh_mcp import TEN_MAY_CHU, cau_hinh_tho
from tram.tho.mcp_tho import DAU, CUOI, ghep_codex_toml, lenh_claude_mcp, url_nho

URL = "https://may-b.tail1234.ts.net/nho/mcp"
CU = 'model = "gpt-5"\n\n[profiles.nhanh]\nmodel = "gpt-5-mini"\n'


def test_url_nho_chi_https_tailnet():
    assert url_nho("https://may-b.tail1234.ts.net/") == URL
    for sai in ("http://may-b.tail1234.ts.net", "https://may-b/x", 'https://a"b'):
        with pytest.raises(ValueError):
            url_nho(sai)


def test_codex_them_khoi_cuoi_file_giu_noi_dung_cu_header_tu_bien_moi_truong():
    moi = ghep_codex_toml(CU, URL)
    assert moi.startswith(CU) and moi.count(DAU) == moi.count(CUOI) == 1
    t = tomllib.loads(moi)
    assert t["profiles"]["nhanh"]["model"] == "gpt-5-mini"
    may_chu = t["mcp_servers"][TEN_MAY_CHU]
    assert may_chu["url"] == URL and "http_headers" not in may_chu
    assert {h: f"${{{b}}}" for h, b in may_chu["env_http_headers"].items()} == cau_hinh_tho()["headers"]
    assert ghep_codex_toml("", URL).startswith(DAU)


def test_codex_chay_lai_thay_khoi_cu_khong_nhan_doi():
    lan1 = ghep_codex_toml(CU, URL)
    lan2 = ghep_codex_toml(lan1 + "\n[khac]\nx = 1\n", URL.replace("may-b", "may-b2"))
    assert lan2.count(DAU) == 1 and "may-b2" in lan2 and "may-b.tail" not in lan2
    assert tomllib.loads(lan2)["khac"]["x"] == 1


@pytest.mark.parametrize("cu", ['[mcp_servers.tram-nho]\nurl = "http://khac"\n', "model = \n", f"{DAU}\nx = 1\n"])
def test_codex_tu_choi_cau_hinh_hong_hoac_trung_ten_ngoai_khoi(cu):
    with pytest.raises(ValueError):
        ghep_codex_toml(cu, URL)


def test_claude_qua_lenh_cua_cli_voi_thu_muc_cua_khe(tmp_path):
    (xoa, env1), (them, env2) = lenh_claude_mcp("/b/claude", tmp_path / "khe")
    assert xoa == ["/b/claude", "mcp", "remove", "--scope", "user", TEN_MAY_CHU]
    assert them[:6] == ["/b/claude", "mcp", "add-json", "--scope", "user", TEN_MAY_CHU]
    assert json.loads(them[6]) == cau_hinh_tho() and "${TRAM_MA_GIAO}" in them[6]
    assert env1 == env2 == {"CLAUDE_CONFIG_DIR": str(tmp_path / "khe")}
