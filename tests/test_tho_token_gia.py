"""Đường nối CLI/token giả phải chạy được mà không dựa vào UID hay token thật của B."""
import json
import os
import subprocess

import pytest

from tho_chay_gia import dung_may
from tram.tho import claude_token
from tram.tho.lenh_token_khe import boc_token
from tram.tho.tep_token import ghi


def test_fixture_b_chay_cli_gia_qua_token_fd(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"ghi": ["da-chay.txt", "CLI giả nhận FD token giả"]}])
    assert m.nc.ch.tren_may_b
    pr = m.nc.principal(m.nc.ch.khe[0], None, "test-token")
    env = {"PATH": os.environ["PATH"], "LANG": "C.UTF-8"}
    kq = subprocess.run(pr.boc(boc_token(["claude", "-p"])), cwd=tmp_path, env=env,
                        input="gói giả", text=True, capture_output=True, timeout=10)
    assert kq.returncode == 0, kq.stderr
    assert (tmp_path / "da-chay.txt").read_text() == "CLI giả nhận FD token giả"
    assert "oauth-gia-lap" not in kq.stdout + kq.stderr
    assert json.loads((tmp_path / ".tram/argv-1.json").read_text()) == ["-p"]


@pytest.mark.parametrize("hong", [False, True], ids=["fd", "sai-quyen"])
def test_tham_so_tiem_van_kiem_file_va_dong_fd(tmp_path, hong):
    p = tmp_path / "claude/oauth-token"
    ghi(p, "oauth-gia-lap")
    if hong:
        p.chmod(0o644)
    da = []

    def exec_gia(cli, argv, env):
        fd = int(env[claude_token.FD_ENV])
        da.append(fd)
        assert cli == claude_token.CLI and argv == [cli, "-p"]
        assert os.get_inheritable(fd) and os.read(fd, 4096) == b"oauth-gia-lap"
        assert all("oauth-gia-lap" not in str(x) for x in (argv, env))
        raise RuntimeError("exec giả lỗi")

    with pytest.raises(ValueError if hong else RuntimeError):
        claude_token.chay(["-p"], kiem_token=lambda: p, exec_cli=exec_gia)
    if hong:
        assert da == []
    else:
        with pytest.raises(OSError):
            os.fstat(da[0])
