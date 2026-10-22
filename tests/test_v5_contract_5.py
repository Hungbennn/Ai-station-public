import subprocess
from pathlib import Path
from types import SimpleNamespace

from tram.tho.do_may import dang_nhap_codex


def test_codex_login_dung_principal_va_env_kin():
    goi = []
    kill = lambda *a: None
    pr = SimpleNamespace(boc=lambda a: ["principal-gia", *a], kill_nhom=kill)
    def chay(a, **kw):
        goi.append((a, kw))
        return subprocess.CompletedProcess(a, 0, "", "")
    assert dang_nhap_codex(pr, "/bin/codex-gia", Path("/cau-hinh-khe"), path="/bin", chay=chay)[0] is True
    a, kw = goi[0]
    assert a == ["principal-gia", "/bin/codex-gia", "login", "status"]
    assert kw["kill"] is kill and kw["timeout"] == 20
    assert kw["env"] == {"PATH": "/bin", "LANG": "C.UTF-8", "CODEX_HOME": "/cau-hinh-khe"}
