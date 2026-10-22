import json
import shutil

import pytest

from phieu_gia import de_xuat
from tram.chay_cli.lenh_claude import argv_claude, env_cli, ghi_file_phieu
from tram.chay_cli.quyen import HOOK_PRE_COMPACT, doc_mau, phien_ban_quyen, sinh_settings, thu_muc_quyen
from tram.phieu.mo_hinh import Phieu, sinh_ma_giao


def phieu(buoc="code") -> Phieu:
    return Phieu(**de_xuat(buoc=buoc).model_dump(), giao_id="g-20261013-0042", luot=3, khe_id="B/claude-1",
                 han_giu="2026-10-13T03:10:00Z", ma_giao=sinh_ma_giao())


@pytest.mark.parametrize("vai", ["spec", "coder", "qc"])
def test_mau_that_hop_le_va_cam_push(vai):
    m = doc_mau(vai)
    assert m["permissions"]["defaultMode"] == "dontAsk" and "Bash(git push:*)" in m["permissions"]["deny"]
    assert "Bash(tram bao:*)" in m["permissions"]["allow"]


def test_phien_ban_doi_khi_mau_doi(tmp_path):
    shutil.copytree(thu_muc_quyen(), tmp_path / "q")
    cu = phien_ban_quyen("coder", tmp_path / "q")
    assert cu.startswith("1+") and len(cu) == 14
    p = tmp_path / "q" / "coder.json"
    m = json.loads(p.read_text())
    m["permissions"]["deny"].append("Bash(rm:*)")
    p.write_text(json.dumps(m))
    assert phien_ban_quyen("coder", tmp_path / "q") != cu


@pytest.mark.parametrize("sua", [{"permissions": {"defaultMode": "bypassPermissions", "allow": [], "deny": [],
                                                  "disableBypassPermissionsMode": "disable"}},
                                 {"permissions": {"defaultMode": "dontAsk", "allow": [], "deny": []}},
                                 {"la": 1}, {"vai": "qc"}])
def test_mau_sai_bi_tu_choi(tmp_path, sua):
    m = {**doc_mau("coder"), **sua}
    (tmp_path / "coder.json").write_text(json.dumps(m))
    with pytest.raises(ValueError):
        doc_mau("coder", tmp_path)
    with pytest.raises(ValueError):
        doc_mau("admin")


def test_settings_cua_phieu():
    s = sinh_settings(phieu(), nho=False)
    allow = s["permissions"]["allow"]
    assert "Bash(php artisan test --filter *)" in allow and "Bash(npm run test:unit)" in allow
    assert not any(a.startswith("mcp__") for a in allow)
    assert s["hooks"]["PreCompact"][0]["hooks"][0]["command"] == HOOK_PRE_COMPACT
    assert "mcp__tram-nho__nho_lai" in sinh_settings(phieu(), nho=True)["permissions"]["allow"]
    spec = sinh_settings(phieu("spec"), nho=False)["permissions"]
    assert not any(a.startswith("Bash(php") for a in spec["allow"]) and "Edit(docs/**)" in spec["allow"]


def test_argv_khong_bo_qua_quyen_va_chi_nap_settings_vai(tmp_path):
    a = argv_claude(settings=tmp_path / "s.json", mcp=None)
    assert a[:5] == ["claude", "-p", "--output-format", "stream-json", "--verbose"]
    assert ["--setting-sources", "user"] == a[5:7] and a[a.index("--settings") + 1] == str(tmp_path / "s.json")
    assert "--strict-mcp-config" in a and not any("skip-permissions" in x or "bypass" in x for x in a)
    b = argv_claude(settings=tmp_path / "s.json", mcp=tmp_path / "m.json")
    assert b[b.index("--mcp-config") + 1] == str(tmp_path / "m.json")


def test_env_khong_co_token_va_nho_can_ma_giao(tmp_path):
    e = env_cli(thu_muc_cau_hinh=tmp_path / "cfg", giao_id="g-1", hang_doi=tmp_path / "hd", wt=tmp_path / "wt",
                path="/usr/bin:/bin")
    assert set(e) == {"CLAUDE_CONFIG_DIR", "TRAM_GIAO_ID", "TRAM_HANG_DOI", "PATH", "LANG", "GIT_CONFIG_COUNT",
                      "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0", "GIT_CONFIG_KEY_1", "GIT_CONFIG_VALUE_1"}
    assert e["GIT_CONFIG_VALUE_0"] == "/dev/null" and e["GIT_CONFIG_VALUE_1"] == str(tmp_path / "wt")
    n = env_cli(thu_muc_cau_hinh=tmp_path, giao_id="g-1", hang_doi=tmp_path, wt=tmp_path, path="/bin",
                ma_giao="m" * 22, nho_url="http://127.0.0.1:7710/mcp")
    assert n["TRAM_MA_GIAO"] == "m" * 22 and n["TRAM_NHO_URL"].endswith("/mcp")
    with pytest.raises(ValueError):
        env_cli(thu_muc_cau_hinh=tmp_path, giao_id="g", hang_doi=tmp_path, wt=tmp_path, path="/bin", nho_url="x")


def test_ghi_file_phieu(tmp_path):
    s, m = ghi_file_phieu(tmp_path / "p", phieu(), nho=False)
    assert m is None and json.loads(s.read_text())["permissions"]["defaultMode"] == "dontAsk"
    s, m = ghi_file_phieu(tmp_path / "p", phieu(), nho=True)
    assert "${TRAM_MA_GIAO}" in m.read_text() and phieu().ma_giao not in m.read_text()
