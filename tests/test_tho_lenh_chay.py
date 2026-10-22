"""`tram tho chay | nhan-token | them-khe | bot-khe` và dọn worktree bead đã đóng (spec 3 §5.1, §7.1, §9.1)."""
import threading
import time
from contextlib import closing
from dataclasses import replace
from types import SimpleNamespace

import pytest

from tho_chay_gia import FILE_BG, dung_may, khoi_bg, tram_bao
from tram.cli import tao_parser
from tram.tho import lenh_khe
from tram.tho.cau_hinh_chay import CauHinhChay
from tram.tho.lenh_chay import chay_may, luu_token_may
from tram.tho.lenh_khe import sua_khe

THO = """may_id: B
tram_api: http://127.0.0.1:7700
khe:
- {ten: claude-1, cli: claude, principal: 'user:tram-k-1', thu_muc_cau_hinh: /Users/k1/.claude, ten_goi_nho: Claude 1,
   vai_uu_tien: [coder]}
"""


def test_tu_choi_chay_khi_chua_chot_phuong_an_hoac_principal(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [])
    assert chay_may(replace(m.nc, ch=replace(m.nc.ch, chay=CauHinhChay())), threading.Event()) == 2
    k = replace(m.nc.ch.khe[0], principal=None)
    assert chay_may(replace(m.nc, ch=replace(m.nc.ch, khe=(k,))), threading.Event()) == 2


def test_chay_may_tron_vong_roi_don_worktree_bead_da_dong(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"ghi": [FILE_BG, khoi_bg("Tên kết thúc 'ỷ' không mất byte")]},
                                         tram_bao("--xong", "--ban-giao", FILE_BG, "xong")])
    tat = threading.Event()
    th = threading.Thread(target=chay_may, args=(m.nc, tat), kwargs={"chu_ky_don": 0.2}, daemon=True)
    th.start()
    def con_cay():
        return any(m.nc.goc_wt.glob("*/cay"))
    het = time.monotonic() + 40
    da_dong = False
    while time.monotonic() < het:
        with closing(m.t.kho()) as kho:
            if not da_dong and kho.db.execute("SELECT 1 FROM su_kien WHERE loai = 'bao.xong'").fetchone():
                with kho.giao_dich():                                         # phần 4 phát bead.dong
                    kho.ghi_su_kien("hr-codex", "bead.dong", {"du_an": "hr-codex", "bead_id": "hr-1"},
                                    luc=m.t.gio[0], bead_id="hr-1", tac_nhan="tram/giao-viec")
                da_dong = True
        if da_dong and not con_cay():
            break
        time.sleep(0.1)
    tat.set()
    th.join(timeout=30)
    assert da_dong and not con_cay()


def test_luu_token_qua_stdin_khong_qua_argv():
    goi = []
    luu_token_may("t" * 43, chay=lambda argv, **kw: goi.append((argv, kw["input"])), doc=lambda: "t" * 43)
    assert goi[0][0] == ["security", "-i"] and "t" * 43 in goi[0][1] and "t" * 43 not in " ".join(goi[0][0])
    with pytest.raises(ValueError):
        luu_token_may("ngan", chay=lambda *a, **k: None, doc=lambda: None)
    with pytest.raises(RuntimeError):
        luu_token_may("t" * 43, chay=lambda *a, **k: None, doc=lambda: None)


def test_them_bot_khe_kiem_truoc_khi_ghi(tram_home_tam, monkeypatch):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "tho.yaml").write_text(THO)
    moi = sua_khe(tram_home_tam / "tho.yaml", them={"ten": "claude-2", "cli": "claude", "principal": "user:tram-k-2",
                                                     "thu_muc_cau_hinh": "/Users/k2/.claude", "ten_goi_nho": "C2",
                                                     "vai_uu_tien": ["qc"]})
    assert "claude-2" in moi and "claude-1" in moi
    with pytest.raises(ValueError):
        sua_khe(tram_home_tam / "tho.yaml", them={"ten": "X", "cli": "codex"})
    with pytest.raises(ValueError):
        sua_khe(tram_home_tam / "tho.yaml", bot="khong-co")
    goi = []
    monkeypatch.setattr("tram.tho.khach.KhachTram.goi", lambda self, m, d, than=None, **kw: goi.append(than) or (200, {}))
    monkeypatch.setattr("tram.tho.khach.doc_token_may", lambda **kw: "x")
    args = SimpleNamespace(ten="claude-1", dong_y=True)
    assert lenh_khe._bot_khe(args) == 2                                       # bỏ khe cuối → tho.yaml không hợp lệ
    args = SimpleNamespace(ten="claude-2", principal="user:tram-k-2", thu_muc_cau_hinh="/Users/k2/.claude",
                           ten_goi_nho="C2", vai=["qc"], dong_y=True)
    assert lenh_khe._them_khe(args) == 0 and [k["ten"] for k in goi[0]["khe"]] == ["claude-1", "claude-2"]


def test_dang_ky_lenh_cli():
    p = tao_parser()
    assert p.parse_args(["tho", "chay"]).ham.__name__ == "_chay"
    assert p.parse_args(["tho", "nhan-token"]).ham.__name__ == "_nhan_token"
    assert p.parse_args(["chu", "cai-dat-tho", "--khe", "claude-1=tram-k-1", "--co-che", "user"]).quan_ly == "tram-tho"
    assert p.parse_args(["chu", "kiem-cach-ly", "--principal", "user:a"]).principal == ["user:a"]
    with pytest.raises(SystemExit):                                     # 3c: tram-kiem chỉ khai ở cach_ly.tram_kiem
        p.parse_args(["chu", "kiem-cach-ly", "--tram-kiem", "user:tram-kiem"])
    assert p.parse_args(["tho", "them-khe", "claude-3", "--principal", "user:x", "--thu-muc-cau-hinh", "/a",
                         "--ten-goi-nho", "C3", "--vai", "coder"]).vai == ["coder"]


def test_chay_may_dang_ky_lai_giu_models_khe(monkeypatch):
    # 21/10: chay_may đăng ký lại khe khi daemon khởi động nhưng bỏ `models` → trạm quên khả năng Sonnet/Opus.
    from types import SimpleNamespace
    from tram.tho.cau_hinh import KheCauHinh
    from tram.tho.cau_hinh_chay import CauHinhChay
    k = KheCauHinh("claude-1", "claude", "user:tram-khe1", "/Users/tram-khe1/claude", "Claude 1", ("coder",),
                   models=("sonnet", "opus"))
    goi = []
    def tu_choi(method, duong, than):
        goi.append(than)
        return 500, {}
    ch = SimpleNamespace(may_id="B", khe=(k,), chay=CauHinhChay(day="kho-tho"))
    nc = SimpleNamespace(ch=ch, khach=SimpleNamespace(goi=tu_choi))
    monkeypatch.setattr("tram.tho.lenh_chay.doc_principal", lambda p: None)
    assert chay_may(nc, threading.Event()) == 2
    assert goi[0]["khe"][0]["models"] == ["sonnet", "opus"]
