import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tram.chay_cli.codex.app_server import LoiAppServer, doc_han_muc_ranh, hoi_app_server

GIA = Path(__file__).parent / "du_lieu" / "codex" / "app_server_gia.py"
LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


def _hoi(tmp_path, che_do, **kw):
    env = {"CHE_DO": che_do, "GHI": str(tmp_path / "nhan.json"), "CODEX_HOME": str(tmp_path / "khe")}
    return hoi_app_server([sys.executable, str(GIA)], env=env, **kw)


def test_bat_tay_roi_hoi_rate_limits(tmp_path):
    kq = _hoi(tmp_path, "ok")
    assert kq["rateLimits"]["primary"]["windowDurationMins"] == 300
    nhan = json.loads((tmp_path / "nhan.json").read_text())
    assert nhan[0] == {"CODEX_HOME": str(tmp_path / "khe")}
    assert [(t.get("method"), t.get("id")) for t in nhan[1:]] == [
        ("initialize", 0), ("initialized", None), ("account/rateLimits/read", 1)]
    assert nhan[1]["params"]["clientInfo"]["name"] == "tram"


@pytest.mark.parametrize("che_do, mau", [("loi", r"trả lỗi \(mã -32600\)"), ("dong", "đóng trước")])
def test_loi_hoac_dong_som(tmp_path, che_do, mau):
    with pytest.raises(LoiAppServer, match=mau):
        _hoi(tmp_path, che_do)


def test_treo_thi_het_gio_va_giet(tmp_path):
    t0 = time.monotonic()
    with pytest.raises(LoiAppServer, match="không trả lời trong 1 giây"):
        _hoi(tmp_path, "treo", thoi_gian_cho=1)
    assert time.monotonic() - t0 < 10


class _PGia:
    """Principal giả: chỉ dựng tiền tố như sudo — `hoi` là spy nên không có gì được chạy."""
    user = "tram-k-c-codex-1"

    def boc(self, argv):
        return ["/usr/bin/sudo", "-n", "-H", "-u", self.user, "--", *argv]

    def kill_nhom(self, pgid, sig):
        pass


def test_doc_han_muc_ranh_chuan_hoa_va_moi_truong_toi_thieu(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_TOKEN_BAT_KY", "bi-mat")
    monkeypatch.setenv("HOME", "/Users/quan-ly")
    goi, pr = [], _PGia()
    mau = json.loads((GIA.parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))["plus"]
    hm = doc_han_muc_ranh("C/codex-1", tmp_path / "khe", bay_gio=LUC, principal=pr, path="/opt/cli/bin",
                          hoi=lambda argv, env, kill: goi.append((argv, env, kill)) or mau)
    assert hm.nguon == "app-server" and {c.loai for c in hm.cua_so} == {"5h", "tuan"}
    argv, env, kill = goi[0]
    assert argv == pr.boc(["codex", "app-server"]) and kill == pr.kill_nhom
    assert env == {"PATH": "/opt/cli/bin", "LANG": "C.UTF-8", "CODEX_HOME": str(tmp_path / "khe")}

    def hong(argv, env, kill):
        raise LoiAppServer("x")
    kw = {"bay_gio": LUC, "path": "/opt/cli/bin"}
    assert doc_han_muc_ranh("C/codex-1", tmp_path, principal=pr, hoi=hong, **kw) is None
    assert doc_han_muc_ranh("C/codex-1", tmp_path, principal=pr, hoi=lambda a, env, kill: {}, **kw) is None
    assert doc_han_muc_ranh("C/codex-1", tmp_path, principal=None, hoi=lambda *a, **k: goi.append("KHONG"),
                            **kw) is None and len(goi) == 1


def test_treo_thu_hoi_qua_kill_nguoi_goi_khong_de_luong_nen(tmp_path):
    import threading
    from tram.kiem.vong_doi import kill_cuc_bo
    gui, truoc = [], threading.active_count()

    def kill(g, sig):
        gui.append((g, sig))
        kill_cuc_bo(g, sig)
    with pytest.raises(LoiAppServer, match="không trả lời"):
        _hoi(tmp_path, "treo", thoi_gian_cho=0.5, kill=kill)
    assert gui and threading.active_count() == truoc


def test_dong_qua_dai_bi_chan(tmp_path):
    with pytest.raises(LoiAppServer, match="quá dài"):
        _hoi(tmp_path, "dai", thoi_gian_cho=5)


def test_khong_thu_hoi_duoc_thi_nem_loi_thu_hoi(tmp_path):
    import os
    import signal
    from tram.kiem.vong_doi import LoiThuHoi
    pid = []

    def khoi(argv, **kw):
        from tram.kiem.vong_doi import khoi_chay
        n = khoi_chay(argv, **kw)
        pid.append(n.p.pid)
        return n
    try:
        with pytest.raises(LoiThuHoi):
            _hoi(tmp_path, "treo", thoi_gian_cho=0.3, kill=lambda g, s: None, khoi=khoi)
    finally:
        os.killpg(pid[0], signal.SIGKILL)


def test_loi_khong_chep_chu_cua_app_server(tmp_path, capfd):
    bi_mat = "SENTINEL-APP-SERVER-7f3a"
    env = {"CHE_DO": "lo", "LO": bi_mat, "CODEX_HOME": str(tmp_path / "khe")}
    with pytest.raises(LoiAppServer) as e:
        hoi_app_server([sys.executable, str(GIA)], env=env)
    assert "mã 401" in str(e.value) and bi_mat not in str(e.value) and bi_mat not in "".join(capfd.readouterr())
