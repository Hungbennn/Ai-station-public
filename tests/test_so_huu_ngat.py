"""Hoãn ngắt ở ranh giới sở hữu (`tram/kiem/ngat.py`; review vòng 1 A03, vòng 2 R2-02): Ctrl-C tới NGAY sau Popen được
hoãn, `Nhom` vào `chu` rồi tín hiệu mới phát lại qua handler cũ; tín hiệu tới đúng lúc khôi phục handler không để
handler nào kẹt ở bộ ghi. Tiến trình thật chỉ là `python -c` của chính user đang test; tín hiệu chỉ phát vào CHÍNH tiến
trình test (`raise_signal`) với handler của test."""
import signal
import subprocess
import sys

import pytest

from test_vong_doi import _song
from tram.kiem import ngat as ngat_mod
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo

NGU = [sys.executable, "-c", "import time; time.sleep(60)"]


class Ngat(Exception):
    pass


def ngat(so, khung):
    raise Ngat(so)


def popen_ngat(goi):
    def popen(argv, **kw):
        p = subprocess.Popen(argv, **kw)
        goi.append(p)
        signal.raise_signal(signal.SIGINT)                  # Ctrl-C tới khi Popen đã có PID mà chưa trả
        return p
    return popen


def don(goi):
    for p in goi:
        if p.poll() is None:
            p.kill()
            p.wait(5)


def test_ngat_luc_spawn_duoc_hoan_nhom_da_trong_chu_roi_moi_phat_lai():
    goi, chu, cu = [], [], signal.signal(signal.SIGINT, ngat)          # handler của người gọi (vd. `tram tho chay`)
    try:
        with pytest.raises(Ngat):
            khoi_chay(NGU, kill=kill_cuc_bo, chu=chu, popen=popen_ngat(goi))
        assert [n.p for n in chu] == goi and _song(goi[0].pid)          # khoi_chay không tự giết: đã bàn giao
        assert signal.getsignal(signal.SIGINT) is ngat                    # handler cũ khôi phục rồi mới phát lại
        assert thu_hoi_con_lai(chu) is True and not _song(goi[0].pid)
    finally:
        signal.signal(signal.SIGINT, cu)
        don(goi)


def test_tin_hieu_toi_dung_luc_khoi_phuc_handler_van_khoi_phuc_het(monkeypatch):
    goi, chu, da = [], [], []
    cu = {s: signal.signal(s, ngat) for s in (signal.SIGINT, signal.SIGTERM)}

    def dat(so, h):
        r = signal.signal(so, h)
        if h is ngat and not da:                          # tín hiệu tới NGAY khi handler đầu tiên vừa khôi phục
            da.append(so)
            signal.raise_signal(so)
        return r
    monkeypatch.setattr(ngat_mod, "_dat", dat)
    try:
        with pytest.raises(Ngat):
            khoi_chay(NGU, kill=kill_cuc_bo, chu=chu, popen=lambda a, **kw: goi.append(subprocess.Popen(a, **kw))
                      or goi[-1])
        assert signal.getsignal(signal.SIGINT) is ngat and signal.getsignal(signal.SIGTERM) is ngat
        assert [n.p for n in chu] == goi and thu_hoi_con_lai(chu) is True and not _song(goi[0].pid)
    finally:
        for s, h in cu.items():
            signal.signal(s, h)
        don(goi)
