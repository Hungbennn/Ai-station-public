from contextlib import closing

import pytest

from tho_api_gia import tao_tram
from tram.phieu.khe import cac_khe
from tram.tho.cau_hinh import nap_cau_hinh_tho

YAML = """may_id: C
tram_api: https://may-b.tail1234.ts.net
khe:
  - ten: codex-1
    cli: codex
    thu_muc_cau_hinh: /Users/tho/khe/codex-1
    ten_goi_nho: "Codex tài khoản 1"
    vai_uu_tien: [coder, qc]
"""
CODEX = {"ten": "codex-1", "cli": "codex", "ten_goi_nho": "Codex tài khoản 1", "vai_uu_tien": ["coder", "qc"]}


def test_tho_yaml_nhan_khe_codex_tu_xa(tmp_path):
    (tmp_path / "tho.yaml").write_text(YAML, encoding="utf-8")
    ch = nap_cau_hinh_tho(tmp_path / "tho.yaml")
    assert ch.tram_api == "https://may-b.tail1234.ts.net" and ch.khe_id(ch.khe[0]) == "C/codex-1"
    assert ch.khe[0].cli == "codex" and ch.khe[0].vai_uu_tien == ("coder", "qc")
    (tmp_path / "tho.yaml").write_text(YAML.replace("cli: codex", "cli: gemini"), encoding="utf-8")
    with pytest.raises(ValueError, match="gemini"):
        nap_cau_hinh_tho(tmp_path / "tho.yaml")


def test_api_dang_ky_khe_codex_cua_may_c(tmp_path):
    t = tao_tram(tmp_path, dang_ky=False)
    r = t.goi("POST", "/api/tho/dang-ky", "C", json_body={"may_id": "C", "khe": [CODEX]})
    assert r.status == 200 and r.json() == {"khe_id": ["C/codex-1"]}
    with closing(t.kho()) as kho:
        assert cac_khe(kho)["C/codex-1"]["cli"] == "codex"
    sai = {**CODEX, "cli": "gemini"}
    assert t.goi("POST", "/api/tho/dang-ky", "C", json_body={"may_id": "C", "khe": [sai]}).status == 422
