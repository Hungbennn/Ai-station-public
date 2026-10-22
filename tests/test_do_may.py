import json
import subprocess

from tram.tho.do_may import DUONG_TAILSCALE_APP, TAG_THO, do_cli, kiem_tag


def _chay(bang: dict, goi: list):
    def chay(argv, **kw):
        goi.append((argv, kw.get("env", {}).get("CODEX_HOME")))
        ma, ra = bang[tuple(argv[1:])]
        return subprocess.CompletedProcess(argv, ma, ra, "")
    return chay


def test_codex_chi_doc_phien_ban_dang_nhap_do_duoi_principal(tmp_path):
    goi = []
    chay = _chay({("--version",): (0, "codex-cli 0.170.0\n")}, goi)
    kq = do_cli("codex", tmp_path / "khe", which=lambda c: f"/opt/bin/{c}", chay=chay)
    assert (kq.duong_dan, kq.phien_ban, kq.dang_nhap) == ("/opt/bin/codex", "codex-cli 0.170.0", None)
    assert goi == [(["/opt/bin/codex", "--version"], None)] and "principal" in kq.chi_tiet    # bs-863.17


def test_claude_chua_kiem_dang_nhap_va_cli_thieu(tmp_path):
    goi = []
    kq = do_cli("claude", tmp_path, which=lambda c: "/b/claude", chay=_chay({("--version",): (0, "2.1.227\n")}, goi))
    assert kq.dang_nhap is None and "principal" in kq.chi_tiet and len(goi) == 1
    kq = do_cli("codex", tmp_path, which=lambda c: None, chay=None)
    assert kq.duong_dan is None and kq.dang_nhap is None and "PATH" in kq.chi_tiet


def _ts(du_lieu, goi=None, ma=0):
    def chay(argv, **kw):
        (goi if goi is not None else []).append(argv)
        return subprocess.CompletedProcess(argv, ma, json.dumps(du_lieu) if isinstance(du_lieu, dict) else du_lieu, "")
    return chay


def test_tag_tailscale_chi_doc_khong_doi():
    goi = []
    ok, ct = kiem_tag(which=lambda c: "/usr/local/bin/tailscale" if c == "tailscale" else None,
                      chay=_ts({"Self": {"Tags": ["tag:khac", TAG_THO], "HostName": "mac-c"}}, goi))
    assert ok and TAG_THO in ct and goi == [["/usr/local/bin/tailscale", "status", "--json"]]
    ok, ct = kiem_tag(which=lambda c: None, chay=None)
    assert not ok and "Tailscale" in ct
    app = {DUONG_TAILSCALE_APP: DUONG_TAILSCALE_APP}
    ok, ct = kiem_tag(which=app.get, chay=_ts({"Self": {"UserID": 1}}))
    assert not ok and "chưa gắn" in ct and "không tự đổi" in ct
    for hong in ("không phải json", {"Self": None}, {"Self": {"Tags": "tag:tram-tho"}}):
        assert kiem_tag(which=app.get, chay=_ts(hong))[0] is False
    assert kiem_tag(which=app.get, chay=_ts({"Self": {"Tags": [TAG_THO]}}, ma=1))[0] is False
