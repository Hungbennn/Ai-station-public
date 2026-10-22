from pathlib import Path

import pytest

from tram.tho.cau_hinh import nap_cau_hinh_tho

MAU = """may_id: B
tram_api: http://127.0.0.1:7700
khe:
  - ten: claude-1
    cli: claude
    principal: tram-khe-1
    thu_muc_cau_hinh: /Users/tho/khe/claude-1
    ten_goi_nho: "Claude tài khoản 1"
    vai_uu_tien: [coder]
  - ten: claude-2
    cli: claude
    thu_muc_cau_hinh: ~/khe/claude-2
    ten_goi_nho: "Claude tài khoản 2"
    vai_uu_tien: [spec, qc]
"""


def _ghi(tmp_path, s):
    p = tmp_path / "tho.yaml"
    p.write_text(s, encoding="utf-8")
    return p


def test_doc_mau_spec(tmp_path):
    ch = nap_cau_hinh_tho(_ghi(tmp_path, MAU))
    assert ch.may_id == "B" and ch.tram_api == "http://127.0.0.1:7700"
    k1, k2 = ch.khe
    assert ch.khe_id(k1) == "B/claude-1" and k1.principal == "tram-khe-1" and k1.vai_uu_tien == ("coder",)
    assert k2.principal is None and k2.thu_muc_cau_hinh == Path.home() / "khe/claude-2"


def test_mac_dinh_doc_tu_tram_home(tram_home_tam):
    (tram_home_tam / "tho.yaml").parent.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "tho.yaml").write_text(MAU, encoding="utf-8")
    assert nap_cau_hinh_tho().may_id == "B"


@pytest.mark.parametrize("cu, moi", [
    ("may_id: B", "may_id: 'B/x'"), ("tram_api: http://127.0.0.1:7700", "tram_api: http://10.0.0.2:7700"),
    ("cli: claude\n    principal", "cli: gemini\n    principal"), ("ten: claude-1", "ten: Claude_1"),
    ("ten: claude-2", "ten: claude-1"), ("[coder]", "[admin]"), ("[coder]", "[]"),
    ('"Claude tài khoản 1"', '"hung@example.com"'), ("/Users/tho/khe/claude-1", "khe/claude-1"),
    ("    vai_uu_tien: [coder]", "    vai_uu_tien: [coder]\n    token: x"), ("may_id: B", "may_id: B\nla: 1"),
])
def test_sai_bao_loi(tmp_path, cu, moi):
    assert cu in MAU
    with pytest.raises(ValueError):
        nap_cau_hinh_tho(_ghi(tmp_path, MAU.replace(cu, moi, 1)))


def test_thieu_file_hoac_khong_co_khe(tmp_path):
    with pytest.raises(ValueError, match="Chưa có"):
        nap_cau_hinh_tho(tmp_path / "khong.yaml")
    with pytest.raises(ValueError):
        nap_cau_hinh_tho(_ghi(tmp_path, "may_id: B\ntram_api: https://may-b.tail.ts.net\nkhe: []\n"))
