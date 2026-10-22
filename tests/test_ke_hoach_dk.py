import plistlib
import tomllib

import pytest

from tho_dk_gia import URL, dau_do
from tram.tho.ke_hoach_dk import in_ke_hoach_dk, lap_ke_hoach_dk
from tram.tho.khai_khe import doc_khe, noi_dung_tho_yaml

CODEX = doc_khe("codex-1:codex:coder,qc:Codex tài khoản 1")
CLAUDE = doc_khe("claude-3:claude:spec:Claude tài khoản 3")


def _kh(tmp_path, khe=(CODEX, CLAUDE), nho=True, **kw):
    goi = []
    kh = lap_ke_hoach_dk(URL + "/", list(khe), thu_muc_khe=tmp_path / "khe", nho=nho,
                         dd=dau_do(tmp_path, goi=goi, **kw))
    return kh, goi


@pytest.mark.parametrize("sai", ["codex-1:codex:coder", "Codex:codex:coder:x", "g:gemini:coder:x",
                                 "c:codex:admin:x", "c:codex::x", "c:codex:qc:a@b.c", "c:codex:qc: "])
def test_doc_khe_sai(sai):
    with pytest.raises(ValueError):
        doc_khe(sai)


def test_ke_hoach_chi_do_khong_ghi_gi(tmp_path):
    kh, goi = _kh(tmp_path)
    assert not (tmp_path / "home").exists() and not (tmp_path / "khe").exists()
    assert all(a[1:] in (["--version"], ["login", "status"], ["status", "--json"]) for a in goi)
    assert kh.tram_chu == URL and [k["ten"] for k in kh.khe] == ["codex-1", "claude-3"]
    assert kh.khe[0]["thu_muc_cau_hinh"] == str(tmp_path / "khe" / "codex-1")
    toml = kh.tep[tmp_path / "khe" / "codex-1" / "config.toml"].decode()
    assert tomllib.loads(toml)["mcp_servers"]["tram-nho"]["url"] == URL + "/nho/mcp"
    plist = plistlib.loads(kh.tep[tmp_path / "home/Library/LaunchAgents/vn.tram.tho.plist"])
    assert plist["ProgramArguments"] == ["/opt/bin/tram", "tho", "chay"]
    assert kh.lenh_mcp[1][0][:4] == ["/opt/bin/claude", "mcp", "add-json", "--scope"]
    pl = str(tmp_path / "home/Library/LaunchAgents/vn.tram.tho.plist")
    assert kh.lenh_launchd[-1] == ["launchctl", "bootstrap", "gui/501", pl]
    van_ban = in_ke_hoach_dk(kh)
    for y in ("Đổi mã ghép", "Keychain tram-tho-token", "tho.yaml", "config.toml", "+[mcp_servers.tram-nho]",
              "launchctl bootstrap", "/api/tho/dang-ky", "Beads", "S6", "tag:tram-tho"):
        assert y in van_ban, y


def test_khong_nho_thi_khong_cham_cau_hinh_cli(tmp_path):
    kh, _ = _kh(tmp_path, nho=False)
    assert kh.lenh_mcp == [] and all(p.suffix == ".plist" for p in kh.tep)


@pytest.mark.parametrize("kw, mau", [({"tags": ()}, "chưa gắn"), ({"co": ("tram", "claude", "tailscale")}, "codex"),
                                     ({"co": ("codex", "claude", "tailscale")}, "tram")])
def test_tu_choi_khi_chua_gan_tag_hoac_thieu_cli(tmp_path, kw, mau):
    with pytest.raises(ValueError, match=mau):
        _kh(tmp_path, **kw)


def test_tu_choi_url_va_khe_trung(tmp_path):
    with pytest.raises(ValueError):
        lap_ke_hoach_dk("http://may-b.tail1234.ts.net", [CODEX], thu_muc_khe=tmp_path, nho=True, dd=dau_do(tmp_path))
    with pytest.raises(ValueError):
        lap_ke_hoach_dk(URL, [CODEX, CODEX], thu_muc_khe=tmp_path, nho=True, dd=dau_do(tmp_path))


def test_chua_dang_nhap_chi_canh_bao_va_tho_yaml_hop_le(tmp_path):
    kh, _ = _kh(tmp_path, dang_nhap=1)
    assert any("codex-1" in c and "đăng nhập" in c for c in kh.canh_bao)
    from tram.tho.cau_hinh import nap_cau_hinh_tho
    p = tmp_path / "tho.yaml"
    p.write_text(noi_dung_tho_yaml("C", kh.tram_chu, kh.khe), encoding="utf-8")
    ch = nap_cau_hinh_tho(p)
    assert ch.may_id == "C" and [ch.khe_id(k) for k in ch.khe] == ["C/codex-1", "C/claude-3"]


def test_ke_hoach_noi_dung_khi_da_co_tho_yaml_la_dung_khong_bak(tmp_path):
    """bs-2bd.1.8 (bs-78r.12): `thuc_hien_dk` từ chối khi đã có tho.yaml — kế hoạch không được hứa giữ `.bak`."""
    kh, _ = _kh(tmp_path)
    van_ban = in_ke_hoach_dk(kh)
    assert ".bak" not in van_ban and "đã có tho.yaml thì dừng" in van_ban
