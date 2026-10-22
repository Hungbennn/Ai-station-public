import io
import json
import urllib.error
from pathlib import Path

import pytest

from tho_dk_gia import URL, dau_do
from tram.cli import main
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import LoiKhachTram
from tram.tho.ke_hoach_dk import lap_ke_hoach_dk
from tram.tho.khai_khe import doc_khe
from tram.tho.thuc_hien_dk import HieuUng, dang_ky_that, ghep_that, thuc_hien_dk

TOKEN = "tok_" + "z" * 40
KHE = ["codex-1:codex:coder,qc:Codex 1", "claude-3:claude:spec:Claude 3"]


def _hu(nhat_ky, *, ghep_loi=False):
    def ghep(url, ma):
        if ghep_loi:
            raise LoiKhachTram("trạm từ chối mã ghép (403)")
        nhat_ky.append(("ghep", url, ma))
        return "C", TOKEN
    return HieuUng(ghep=ghep, ghi_token=lambda m, t: nhat_ky.append(("token", m)),
                   dang_ky=lambda url, m, t, khe: nhat_ky.append(("dang_ky", m, t == TOKEN, [k["ten"] for k in khe])),
                   chay=lambda argv, **kw: nhat_ky.append(("chay", argv[:3], kw.get("check"),
                                                           (kw.get("env") or {}).get("CLAUDE_CONFIG_DIR"))))


def _kh(tmp_path):
    return lap_ke_hoach_dk(URL, [doc_khe(k) for k in KHE], thu_muc_khe=tmp_path / "khe", nho=True,
                           dd=dau_do(tmp_path))


def test_thu_tu_ghep_token_yaml_tep_mcp_dang_ky_launchd(tmp_path):
    kh, nk = _kh(tmp_path), []
    assert thuc_hien_dk(kh, "ABCD-EFGH-JKMN", _hu(nk)) == "C"
    assert [x[0] for x in nk] == ["ghep", "token", "chay", "chay", "dang_ky"]
    assert nk[0] == ("ghep", URL, "ABCD-EFGH-JKMN") and nk[4] == ("dang_ky", "C", True, ["codex-1", "claude-3"])
    assert nk[2][1:] == (["/opt/bin/claude", "mcp", "remove"], False, str(tmp_path / "khe/claude-3"))
    assert nk[3][1:] == (["/opt/bin/claude", "mcp", "add-json"], True, str(tmp_path / "khe/claude-3"))
    assert not any(x[0] == "chay" and x[1][0] == "launchctl" for x in nk)
    ch = nap_cau_hinh_tho(kh.tho_yaml)
    assert ch.chay.nho_url == URL + "/nho/mcp"
    assert ch.may_id == "C" and ch.tram_api == URL and not (kh.tho_yaml.parent / "tho.yaml.bak").exists()
    toml = tmp_path / "khe/codex-1/config.toml"
    assert "tram-nho" in toml.read_text() and toml.stat().st_mode & 0o777 == 0o600
    assert (tmp_path / "home/Library/LaunchAgents/vn.tram.tho.plist").exists()
    assert not any(TOKEN in p.read_text(errors="ignore") for p in tmp_path.rglob("*") if p.is_file())
    before = list(nk)
    with pytest.raises(ValueError, match="service"):
        thuc_hien_dk(kh, "MA-MOI", _hu(nk))
    assert nk == before


def test_ghep_loi_thi_khong_ghi_gi(tmp_path):
    kh, nk = _kh(tmp_path), []
    with pytest.raises(LoiKhachTram):
        thuc_hien_dk(kh, "x", _hu(nk, ghep_loi=True))
    assert nk == [] and not kh.tho_yaml.exists() and not any(p.exists() for p in kh.tep)


class _Ph(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_ghep_va_dang_ky_qua_http():
    goi = []

    def mo(yc, timeout):
        goi.append((yc.full_url, yc.get_header("Authorization"), json.loads(yc.data)))
        if yc.data and b"SAI" in yc.data:
            raise urllib.error.HTTPError(yc.full_url, 403, "x", {}, io.BytesIO(b'{"loi": "M\xc3\xa3 sai"}'))
        return _Ph(json.dumps({"may_id": "C", "token": TOKEN, "khe_id": ["C/codex-1"]}).encode())

    assert ghep_that(URL, "ABCD", mo=mo) == ("C", TOKEN)
    assert goi[0] == (URL + "/api/ghep-may", None, {"ma": "ABCD"})
    with pytest.raises(LoiKhachTram, match="403"):
        ghep_that(URL, "SAI", mo=mo)
    dang_ky_that(URL, "C", TOKEN, [{"ten": "codex-1", "cli": "codex", "thu_muc_cau_hinh": "/x", "ten_goi_nho": "C1",
                                     "vai_uu_tien": ["qc"]}], mo=mo)
    assert goi[2] == (URL + "/api/tho/dang-ky", f"Bearer {TOKEN}", {"may_id": "C", "khe": [
        {"ten": "codex-1", "cli": "codex", "ten_goi_nho": "C1", "vai_uu_tien": ["qc"]}]})


def test_cli_liet_ke_roi_cho_dong_y(tmp_path, monkeypatch, capsys):
    import tram.tho.ke_hoach_dk as khdk
    import tram.tho.thuc_hien_dk as thdk
    nk = []
    monkeypatch.setattr("getpass.getpass", lambda *_: "ABCD-EFGH-JKMN")
    monkeypatch.setattr(khdk, "DauDoDK", lambda: dau_do(tmp_path))
    monkeypatch.setattr(thdk, "hieu_ung_that", lambda: _hu(nk))
    lenh = ["tho", "dang-ky", "--tram-chu", URL, "--thu-muc-khe", str(tmp_path / "khe"),
            *[x for k in KHE for x in ("--khe", k)]]
    monkeypatch.setattr("builtins.input", lambda *_: "không")
    assert main(lenh) == 1 and nk == [] and "Sẽ làm" in capsys.readouterr().out
    assert main([*lenh, "--dong-y"]) == 0 and nk[0][0] == "ghep" and "Đã đăng ký máy C" in capsys.readouterr().out
    assert main([*lenh[:-4], "--khe", "x:gemini:qc:X", "--dong-y"]) == 2
    monkeypatch.setattr(khdk, "DauDoDK", lambda: dau_do(tmp_path / "may-moi", tags=()))
    assert main([*lenh, "--dong-y"]) == 2 and "chưa gắn" in capsys.readouterr().err
