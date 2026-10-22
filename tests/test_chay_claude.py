"""`ChayClaude` với CLI GIẢ (tests/cli_gia.py) — không gọi Claude thật (spec 3 §7.2, §7.8)."""
import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

from tram.chay_cli.claude import ChayClaude
from tram.chay_cli.giao_dien import ket_thuc_tu
from tram.han_muc.claude import NguonHanMucClaude

CLI = str(Path(__file__).parent / "cli_gia.py")


def boc_gia(argv):
    return [sys.executable, CLI, *argv[1:]]


def chay(tmp_path, monkeypatch, buoc, *, dung=None, sau=None, **kw):
    kb = tmp_path / "kb.json"
    kb.write_text(json.dumps(buoc))
    (tmp_path / "goi.md").write_text("# Gói\n")
    monkeypatch.setenv("CLI_GIA_KICH_BAN", str(kb))
    dung = dung or threading.Event()
    if sau:
        threading.Timer(sau, dung.set).start()
    pid = []
    r = ChayClaude(boc_gia, khe_id="B/claude-1", khi_bat_dau=pid.append, cho_kill=2, **kw)
    kq = r.chay(["claude", "-p"], cwd=tmp_path, env=dict(os.environ), stdin=tmp_path / "goi.md",
                log=tmp_path / "log" / "g-1-1-1.jsonl", dung=dung, nguon=NguonHanMucClaude())
    return kq, pid


def test_lan_chay_binh_thuong(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_MA_GIAO", "MA-BI-MAT")
    kq, pid = chay(tmp_path, monkeypatch, [
        {"in": {"type": "system", "subtype": "init", "model": "claude-gia"}},
        {"in": {"type": "assistant", "message": {"id": "m1", "usage": {"output_tokens": 40}}}},
        {"in_tho": "dòng không phải json MA-BI-MAT"},
        {"in": {"type": "result", "usage": {"input_tokens": 9, "output_tokens": 42}}}])
    log = tmp_path / "log" / "g-1-1-1.jsonl"
    assert ket_thuc_tu(kq) == "xong" and kq.ma_thoat == 0 and kq.token_ra == 42 and kq.mo_hinh == "claude-gia"
    assert kq.digest_log == "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest() and len(pid) == 1
    assert "MA-BI-MAT" not in log.read_text()
    assert "dòng không phải json" in log.read_text() and (tmp_path / ".tram" / "stdin-1.md").read_text() == "# Gói\n"


def test_dung_kill_ca_nhom_ke_ca_chau(tmp_path, monkeypatch):
    bat = time.monotonic()
    kq, _ = chay(tmp_path, monkeypatch, [{"con": 60}, {"in": {"type": "assistant", "message": {"id": "m"}}},
                                         {"ngu": 60}], sau=0.5)
    assert time.monotonic() - bat < 10 and kq.bi_dung and ket_thuc_tu(kq) == "dung"


def test_vuot_token_ra_thi_dung(tmp_path, monkeypatch):
    kq, _ = chay(tmp_path, monkeypatch, [{"in": {"type": "assistant", "message": {"id": "m", "usage": {
        "output_tokens": 500}}}}, {"ngu": 60}], tran_token_ra=100)
    assert kq.bi_dung and kq.token_ra == 500


def test_het_han_muc_va_khong_khoi_chay_duoc(tmp_path, monkeypatch):
    kq, _ = chay(tmp_path, monkeypatch, [{"in": {"type": "rate_limit_event", "rate_limit_info": {
        "status": "rejected", "rateLimitType": "five_hour", "resetsAt": 1760335200}}}, {"thoat": 1}])
    assert ket_thuc_tu(kq) == "het_han_muc" and kq.reset_luc == "2025-10-13T06:00:00Z"
    (tmp_path / "goi.md").write_text("x")
    r = ChayClaude(lambda a: [str(tmp_path / "khong-co")], khe_id="B/claude-1")
    kq = r.chay(["claude"], cwd=tmp_path, env={}, stdin=tmp_path / "goi.md", log=tmp_path / "l.jsonl",
                dung=threading.Event(), nguon=NguonHanMucClaude())
    assert kq.ma_thoat is None and ket_thuc_tu(kq) == "loi_he" and "lỗi khởi chạy" in (tmp_path / "l.jsonl").read_text()


def test_cli_thoat_ma_chau_giu_stdout_khong_treo(tmp_path, monkeypatch):
    bat = time.monotonic()
    kq, _ = chay(tmp_path, monkeypatch, [{"con": 60}, {"in": {"type": "assistant", "message": {"id": "m"}}},
                                         {"thoat": 0}])
    assert time.monotonic() - bat < 10 and ket_thuc_tu(kq) == "xong" and kq.co_assistant
