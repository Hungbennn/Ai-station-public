import hashlib
import sys
import threading
import time
from pathlib import Path

from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.chay_cli.codex.luong import DocLuongCodex
from tram.chay_cli.giao_dien import ChayCLI, ket_thuc_tu

DL = Path(__file__).parent / "du_lieu" / "codex"


def _chay(tmp_path, fixture, *, ma=0, che_do="", dung=None, **kw):
    (tmp_path / "goi.md").write_text("# Gói ngữ cảnh\n", encoding="utf-8")
    env = {"FIXTURE": str(DL / fixture), "GHI": str(tmp_path / "stdin.txt"), "MA": str(ma), "CHE_DO": che_do,
           "TRAM_MA_GIAO": "MA-GIAO-BI-MAT"}
    return ChayCodex(**kw).chay([sys.executable, str(DL / "exec_gia.py")], cwd=tmp_path, env=env,
                                stdin=tmp_path / "goi.md", log=tmp_path / "log" / "lan-1.jsonl",
                                dung=dung or threading.Event(), nguon=NguonHanMucCodex())


def test_xong_dem_token_va_log_che_ma_giao(tmp_path):
    boc, pid, kills = [], [], []
    from tram.tho.mo_coi import kill_cuc_bo
    def kill(p, sig):
        kills.append((p, sig))
        kill_cuc_bo(p, sig)
    kq = _chay(tmp_path, "exec_xong.jsonl", boc=lambda a: (boc.append(a) or a),
               khe_id="C/codex-1", khi_bat_dau=pid.append, kill=kill)
    assert len(boc) == len(pid) == 1 and all(g == pid[0] for g, _ in kills)      # chỉ nhóm của CLI, nếu còn sống
    assert isinstance(ChayCodex(), ChayCLI) and ket_thuc_tu(kq) == "xong"
    assert (kq.ma_thoat, kq.co_assistant, kq.het_han_muc, kq.chua_dang_nhap) == (0, True, False, False)
    assert (kq.token_vao, kq.token_cache_doc, kq.token_ra) == (315, 24448, 1122)
    assert (tmp_path / "stdin.txt").read_text(encoding="utf-8") == "# Gói ngữ cảnh\n"
    log = (tmp_path / "log" / "lan-1.jsonl").read_bytes()
    assert b"MA-GIAO-BI-MAT" not in log and "mã *** không".encode() in log and b"stderr" in log
    assert kq.digest_log == "sha256:" + hashlib.sha256(log).hexdigest() and kq.thoi_gian_ms >= 0


def test_het_han_muc_va_chua_dang_nhap(tmp_path):
    kq = _chay(tmp_path, "exec_het_han_muc.jsonl", ma=1)
    assert kq.het_han_muc and ket_thuc_tu(kq) == "het_han_muc"
    kq = _chay(tmp_path, "exec_chua_dang_nhap.jsonl", ma=1)
    assert kq.chua_dang_nhap and not kq.co_assistant and ket_thuc_tu(kq) == "loi_he"


def test_dung_giet_ca_nhom_ke_ca_khi_bo_qua_sigterm(tmp_path):
    dung = threading.Event()
    threading.Timer(0.5, dung.set).start()
    t0 = time.monotonic()
    kq = _chay(tmp_path, "exec_xong.jsonl", che_do="treo", dung=dung, cho_dung_giay=0.5)
    assert ket_thuc_tu(kq) == "dung" and kq.bi_dung and time.monotonic() - t0 < 10
    kq = _chay(tmp_path, "exec_xong.jsonl", tran_token_ra=100)
    assert kq.bi_dung and kq.token_ra == 1122


def test_doc_luong_bo_qua_dong_la_va_usage_thieu():
    d = DocLuongCodex(NguonHanMucCodex())
    for dong in ({"type": "turn.completed"}, {"type": "turn.completed", "usage": {"input_tokens": "x"}},
                 {"type": "item.completed", "item": "x"}, {"type": "item.completed", "item": {"type": "reasoning"}},
                 {"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 30}}):
        d.nap(dong)
    kq = d.ket_qua(ma_thoat=1, bi_dung=False, thoi_gian_ms=5, digest_log="sha256:x")
    assert (kq.token_vao, kq.token_cache_doc, kq.token_ra, kq.co_assistant) == (0, 30, 0, False)
    assert ket_thuc_tu(kq) == "loi_he"
