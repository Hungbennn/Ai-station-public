import plistlib
import shlex
import subprocess
from pathlib import Path

import pytest

from tram.tho.khach import KEYCHAIN_THO
from tram.tho.launchd_tho import NHAN_THO, lenh_nap_launchd, tao_plist_tho
from tram.tho.token_may import ghi_token_may

TOKEN = "AbC_d-" + "x" * 40


class KeychainGia:
    def __init__(self, hong=False):
        self.kho, self.argv, self.hong = {}, [], hong

    def __call__(self, argv, **kw):
        self.argv.append(argv)
        if argv == ["security", "-i"]:
            t = shlex.split(kw["input"])
            if not self.hong:
                self.kho[t[t.index("-s") + 1]] = t[t.index("-w") + 1]
            return subprocess.CompletedProcess(argv, 0, "", "")
        gt = self.kho.get(argv[argv.index("-s") + 1])
        return subprocess.CompletedProcess(argv, 0 if gt else 44, (gt or "") + "\n", "")


def test_plist_chay_tram_tho_chay_khong_mang_bi_mat(tmp_path):
    p = plistlib.loads(tao_plist_tho(tram="/Users/tho/.local/bin/tram", log=tmp_path / "tho.log", home=tmp_path))
    assert p["Label"] == NHAN_THO == "vn.tram.tho"
    assert p["ProgramArguments"] == ["/Users/tho/.local/bin/tram", "tho", "chay"]
    assert p["RunAtLoad"] is True and p["KeepAlive"] == {"SuccessfulExit": False}
    assert p["StandardOutPath"] == p["StandardErrorPath"] == str(tmp_path / "tho.log")
    env = p["EnvironmentVariables"]
    assert set(env) == {"PATH"} and str(tmp_path / ".local/bin") in env["PATH"]
    with pytest.raises(ValueError):
        tao_plist_tho(tram="tram", log=tmp_path / "x.log", home=tmp_path)
    pl = tmp_path / f"{NHAN_THO}.plist"
    assert lenh_nap_launchd(pl, uid=501) == [["launchctl", "bootout", f"gui/501/{NHAN_THO}"],
                                             ["launchctl", "bootstrap", "gui/501", str(pl)]]


def test_ghi_token_qua_stdin_roi_doc_lai_khop():
    kc = KeychainGia()
    ghi_token_may("C", TOKEN, chay=kc)
    assert kc.kho == {KEYCHAIN_THO: TOKEN}
    assert all(TOKEN not in " ".join(a) for a in kc.argv)                     # không bao giờ nằm trong argv
    with pytest.raises(RuntimeError, match="Keychain"):
        ghi_token_may("C", TOKEN, chay=KeychainGia(hong=True))


@pytest.mark.parametrize("may_id, token", [("C", "ngan"), ("C", 'x" -A ' + "y" * 40), ("C/x", TOKEN), ("-U", TOKEN)])
def test_tu_choi_gia_tri_la_tu_tram_tra_ve(may_id, token):
    kc = KeychainGia()
    with pytest.raises(ValueError):
        ghi_token_may(may_id, token, chay=kc)
    assert kc.argv == []
