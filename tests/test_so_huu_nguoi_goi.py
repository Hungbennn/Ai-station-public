"""Hợp đồng sở hữu (`so_huu`, review vòng 2 R2-02): MỌI người gọi `khoi_chay` trên HEAD — lệnh kiểm, CLI Claude/Codex,
app-server, dò danh tính — đặt spawn trong khối sở hữu: Ctrl-C tới NGAY sau Popen (hoãn trong `khoi_chay`, phát lại
khi `Nhom` đã ở `chu`) thì con vẫn bị thu hồi rồi ngắt mới nổi lên. Tiến trình thật chỉ là `python -c` của chính user
đang test; tín hiệu chỉ phát vào CHÍNH tiến trình test (`raise_signal`) với handler của test."""
import os
import signal
import threading

import pytest

from test_so_huu_ngat import NGU, Ngat, don, ngat, popen_ngat
from test_vong_doi import _song
from tram.chay_cli.claude import ChayClaude
from tram.chay_cli.codex.app_server import hoi_app_server
from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.han_muc.claude import NguonHanMucClaude
from tram.kiem.chay_lenh import chay_mot_lenh
from tram.kiem.danh_tinh import quan_sat
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo


def _chay_lenh(tmp_path, khoi, popen):
    chay_mot_lenh("x", NGU, cwd=tmp_path, env=dict(os.environ), log=tmp_path / "l.log", thoi_gian_cho=5,
                  boc=lambda a: a, kill=kill_cuc_bo, khoi=khoi)


def _claude(tmp_path, khoi, popen):
    (tmp_path / "goi.md").write_text("x")
    ChayClaude(lambda a: a, khe_id="k", khoi=khoi, cho_kill=1).chay(
        NGU, cwd=tmp_path, env=dict(os.environ), stdin=tmp_path / "goi.md", log=tmp_path / "c.log",
        dung=threading.Event(), nguon=NguonHanMucClaude())


def _codex(tmp_path, khoi, popen):
    (tmp_path / "goi.md").write_text("x")
    ChayCodex(lambda a: a, popen=popen, cho_dung_giay=1).chay(
        NGU, cwd=tmp_path, env=dict(os.environ), stdin=tmp_path / "goi.md", log=tmp_path / "c.log",
        dung=threading.Event(), nguon=NguonHanMucCodex())


def _app_server(tmp_path, khoi, popen):
    hoi_app_server(NGU, env=dict(os.environ), thoi_gian_cho=5, kill=kill_cuc_bo, khoi=khoi)


def _quan_sat(tmp_path, khoi, popen):
    quan_sat(lambda a: NGU, kill_cuc_bo, khoi=khoi, han=5)


@pytest.mark.parametrize("nguoi_goi", [_chay_lenh, _claude, _codex, _app_server, _quan_sat])
def test_moi_nguoi_goi_so_huu_tu_pid_ngat_luc_spawn_van_thu_hoi(tmp_path, nguoi_goi):
    goi, cu = [], signal.signal(signal.SIGINT, ngat)
    p = popen_ngat(goi)
    try:
        with pytest.raises(Ngat):
            nguoi_goi(tmp_path, lambda a, **kw: khoi_chay(a, popen=p, **kw), p)
        assert len(goi) == 1 and not _song(goi[0].pid)
    finally:
        signal.signal(signal.SIGINT, cu)
        don(goi)
