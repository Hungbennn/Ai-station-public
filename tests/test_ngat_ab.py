"""R2-02/R2-03 (vòng 2): SIGTERM THẬT đi qua CẢ HAI lớp trên đường A+B — `hoan()` + hợp đồng sở hữu của plan A (bộ ghi
trong `khoi_chay`/thu hồi) và `term_thanh_ngat` của plan B (CLI cha). Tín hiệu chỉ phát vào CHÍNH tiến trình test
(`signal.raise_signal`), luôn có handler canh của test bên dưới (`chan_sigterm_mac_dinh`) — không bao giờ để SIGTERM
mặc định giết pytest. Tiến trình thật chỉ là `python -c` của user test; backend kill/Popen giả cho ca
kill bị từ chối, gốc treo."""
import signal
import subprocess
import sys

import pytest

from test_lenh_nghiem_thu import args, cau_hinh  # noqa: F401 — fixture `cau_hinh` dùng chung
from test_lenh_nghiem_thu_ngat import chan_sigterm_mac_dinh  # noqa: F401 — handler canh tự dùng
from test_vong_doi import PopenGia, _song
from tram.giao_viec import lenh_nghiem_thu as lnt
from tram.kiem.han_tong import chay_han_tong
from tram.kiem.ngat import NgatTerm, term_thanh_ngat
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo

NGU = [sys.executable, "-c", "import time; time.sleep(60)"]


def sigterm_that():
    assert callable(signal.getsignal(signal.SIGTERM)), "SIGTERM mặc định ở đoạn này sẽ giết CLI cha"
    signal.raise_signal(signal.SIGTERM)


def don_con(goi):
    for p in goi:
        if p.poll() is None:
            p.kill()
            p.wait(5)


def test_sigterm_that_ngay_sau_popen_harness_con_co_chu_thu_hoi_don_roi_moi_ngat(tmp_path):
    goi, don = [], []

    def popen(a, **kw):
        goi.append(subprocess.Popen(a, **kw))
        sigterm_that()                                              # bộ ghi của `hoan()` trong `chay_han_tong`
        return goi[-1]
    try:
        with term_thanh_ngat(), pytest.raises(NgatTerm):
            chay_han_tong(NGU, han=30, kill=kill_cuc_bo, dau=tmp_path / "dau", don=lambda: don.append(1) or True,
                          khoi=lambda a, **kw: khoi_chay(a, popen=popen, **kw))
        assert not _song(goi[0].pid) and don == [1] and not (tmp_path / "dau").exists()
    finally:
        don_con(goi)


def test_sigterm_that_lan_hai_luc_thu_hoi_khong_cat_ngang_roi_thay_het_han(tmp_path):
    goi, gui = [], []

    def kill(g, s):
        if not gui:
            sigterm_that()                                          # tới giữa lúc thu hồi: bộ ghi của `hoan()`
        gui.append(s)
        kill_cuc_bo(g, s)
    try:
        with term_thanh_ngat(), pytest.raises(NgatTerm):
            chay_han_tong(NGU, han=0.3, kill=kill, dau=tmp_path / "dau", don=lambda: True,
                          khoi=lambda a, **kw: goi.append(khoi_chay(a, **kw)) or goi[-1])
        assert gui and not _song(goi[0].p.pid) and not (tmp_path / "dau").exists()
    finally:
        don_con([n.p for n in goi])


def test_sigterm_that_kill_bi_tu_choi_goc_treo_dau_giu_nhom_con_trong_chu(tmp_path):
    chu = []

    def tu_choi(g, s):
        if g == 4242 and s == signal.SIGTERM:
            sigterm_that()
        raise PermissionError

    def khoi(a, **kw):
        chu.append(kw["chu"])
        return khoi_chay(a, popen=lambda *x, **k: PopenGia(), chup=lambda: [], **kw)
    with term_thanh_ngat(), pytest.raises(NgatTerm):
        chay_han_tong(["gia"], han=0.2, kill=tu_choi, dau=tmp_path / "dau", don=lambda: True, khoi=khoi)
    assert (tmp_path / "dau").exists() and chu[0][0].ket_thu_hoi is False             # không xác nhận: cổng đóng


def test_sigterm_that_luc_preflight_cli_cha_tra_143_khong_dau_khong_harness(cau_hinh, tram_home_tam, capsys):
    goi, truoc = [], signal.getsignal(signal.SIGTERM)

    def xac_minh(*a):
        sigterm_that()                                              # bộ ghi của `hoan()` quanh preflight
        goi.append("do-xong")
        return 777
    assert lnt.lenh_nghiem_thu(args(), xac_minh=xac_minh, han_tong=lambda *a, **kw: goi.append("harness")) == 143
    assert goi == ["do-xong"] and not (tram_home_tam / "kiem-lai.dong").exists()
    assert "SIGTERM" in capsys.readouterr().err and signal.getsignal(signal.SIGTERM) is truoc
