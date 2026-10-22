"""CLI của phiếu dùng primitive vòng đời P1: `dung` → thu hồi có hạn; không xác nhận thu hồi → dừng khe (RuntimeError),
không treo ở `wait()`. CLI giả là `python` của chính user đang test; `kill` không làm gì = principal bị từ chối."""
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path

import pytest

from tram.chay_cli.claude import ChayClaude
from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.han_muc.claude import NguonHanMucClaude
from tram.tho.mo_coi import kill_cuc_bo

CLI = str(Path(__file__).parent / "cli_gia.py")
EXEC = str(Path(__file__).parent / "du_lieu" / "codex" / "exec_gia.py")
FIXTURE = str(Path(__file__).parent / "du_lieu" / "codex" / "exec_xong.jsonl")


def _dung_sau(giay: float) -> threading.Event:
    d = threading.Event()
    threading.Timer(giay, d.set).start()
    return d


def _claude(tmp_path, kill):
    (tmp_path / "kb.json").write_text(json.dumps([{"ngu": 60}]))
    env = dict(os.environ, CLI_GIA_KICH_BAN=str(tmp_path / "kb.json"))
    return ChayClaude(lambda a: [sys.executable, CLI], khe_id="B/claude-1", kill=kill, cho_kill=0.3,
                      khi_bat_dau=_PID.append), env, NguonHanMucClaude()


def _codex(tmp_path, kill):
    env = {"FIXTURE": FIXTURE, "GHI": str(tmp_path / "stdin.txt"), "CHE_DO": "treo"}
    return ChayCodex(lambda a: [sys.executable, EXEC], kill=kill, cho_dung_giay=0.3,
                     khi_bat_dau=_PID.append), env, NguonHanMucCodex()


_PID: list[int] = []


@pytest.mark.parametrize("dung_cli", [_claude, _codex])
def test_kill_bi_tu_choi_thi_dung_khe_trong_han(tmp_path, dung_cli):
    _PID.clear()
    (tmp_path / "goi.md").write_text("# Gói\n")
    r, env, nguon = dung_cli(tmp_path, lambda g, s: None)
    t0 = time.monotonic()
    try:
        with pytest.raises(RuntimeError, match="Không dọn được nhóm CLI"):
            r.chay(["cli"], cwd=tmp_path, env=env, stdin=tmp_path / "goi.md", log=tmp_path / "l.jsonl",
                   dung=_dung_sau(0.3), nguon=nguon)
        assert time.monotonic() - t0 < 10
    finally:
        os.killpg(_PID[0], signal.SIGKILL)


@pytest.mark.parametrize("dung_cli", [_claude, _codex])
def test_dung_thu_hoi_ca_cay_qua_kill_cua_principal(tmp_path, dung_cli):
    _PID.clear()
    (tmp_path / "goi.md").write_text("# Gói\n")
    gui = []
    r, env, nguon = dung_cli(tmp_path, lambda g, s: gui.append((g, s)) or kill_cuc_bo(g, s))
    kq = r.chay(["cli"], cwd=tmp_path, env=env, stdin=tmp_path / "goi.md", log=tmp_path / "l.jsonl",
                dung=_dung_sau(0.3), nguon=nguon)
    assert kq.bi_dung and (_PID[0], signal.SIGTERM) in gui
    with pytest.raises(ProcessLookupError):
        os.killpg(_PID[0], 0)


def test_loi_giua_spawn_va_cho_van_thu_hoi(tmp_path):
    _PID.clear()
    (tmp_path / "goi.md").write_text("# Gói\n")
    r, env, nguon = _codex(tmp_path, kill_cuc_bo)

    def hong(pid):
        _PID.append(pid)
        raise OSError("đĩa đầy")
    r.khi_bat_dau = hong
    with pytest.raises(OSError):
        r.chay(["cli"], cwd=tmp_path, env=env, stdin=tmp_path / "goi.md", log=tmp_path / "l.jsonl",
               dung=threading.Event(), nguon=nguon)
    with pytest.raises(ProcessLookupError):
        os.killpg(_PID[0], 0)


def test_cli_khong_thu_hoi_duoc_giu_pid_va_dung_khe(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from tho_chay_gia import dung_may, lay_phieu
    from tram.kiem.vong_doi import LoiThuHoi
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.mot_lan import chay_mot_lan
    from tram.tho.vong_khe import VongKhe
    m = dung_may(tmp_path / "worker", monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)

    def tao(boc, **kw):
        def chay(argv, **k2):
            kw["khi_bat_dau"](999999)                              # PID không tồn tại trên macOS
            raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal")
        return SimpleNamespace(chay=chay)
    m.nc.tao_cli = tao
    with pytest.raises(LoiThuHoi):
        chay_mot_lan(pc, m.nc, threading.Event())
    assert json.loads(so.pid.read_text())["pid"] == 999999             # dọn mồ côi lần khởi động sau còn dữ liệu
    vk, tat = VongKhe(m.nc, k), threading.Event()
    vk.khoi_dong, vk.nhip, vk.phieu_moi, vk.da_xac_nhan = (lambda: None), (lambda: None), tt, True
    monkeypatch.setattr("tram.tho.vong_khe.chay_phieu", lambda *a: (_ for _ in ()).throw(LoiThuHoi("x")))
    hen = threading.Timer(10, tat.set)
    hen.start()
    vk.chay(tat)
    hen.cancel()
    assert vk.hong and not tat.is_set()
