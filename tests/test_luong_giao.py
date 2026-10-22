"""Hai luồng tick (spec 4 §10 "ràng buộc lúc nối 4a-2"; G5): bí của agent thành escalation trong khi kiểm lại dài
đang chạy; khoá mỗi pha; lịch nhịp cố định; khởi động lại giữa kiểm lại thì vòng sau kiểm lại lại, không trùng.
Kiểm lại "dài 15 phút" giả bằng `boc` chờ một Event — không ngủ thật."""
import threading
import time

import pytest

from giao_viec_gia import bug, dung
from test_tick import GIU, chuan_bi_code_xong, loai
from test_tick_hai_pha import bi
from test_xet_xong import F
from tram.giao_viec.luong import KHOA_GIT, KHOA_NHANH, bat_dau_luong_giao, chay_vong, giu_khoa, lap
from tram.giao_viec.tick import vong_git


class BdKhoa:
    """BdGia dùng chung giữa hai luồng tick (CHỈ DÙNG TRONG TEST): mọi lời gọi tuần tự hoá."""

    def __init__(self, g):
        self._g, self._k = g, threading.RLock()

    def __getattr__(self, ten):
        f = getattr(self._g, ten)

        def goi(*a, **kw):
            with self._k:
                return f(*a, **kw)
        return goi if callable(f) else f


def cho_toi(dieu_kien, giay: float = 10.0) -> bool:
    het = time.monotonic() + giay
    while time.monotonic() < het:
        if dieu_kien():
            return True
        time.sleep(0.02)
    return False


class DungGia:
    def __init__(self, n):
        self.n, self.cho = n, []

    def is_set(self):
        return len(self.cho) >= self.n

    def wait(self, giay):
        self.cho.append(giay)


def test_lap_giu_nhip_co_dinh_va_song_qua_loi(capsys):
    gio, buoc = [0.0], iter([10.0, 200.0, 5.0])

    def lam():
        gio[0] += (x := next(buoc))
        if x == 5.0:
            raise RuntimeError("lỗi một vòng")

    d = DungGia(3)
    lap(d, lam, 120, "thu", dong_ho=lambda: gio[0])
    assert d.cho == [110.0, 0.0, 115.0] and "[thu] lỗi: RuntimeError" in capsys.readouterr().err


def test_khoa_mot_vong_moi_pha():
    with giu_khoa(KHOA_GIT) as duoc:
        assert duoc and chay_vong(KHOA_GIT, lambda: {"x": 1}) is None
        assert chay_vong(KHOA_NHANH, lambda: {"x": 1}) == {"x": 1}
    assert chay_vong(KHOA_GIT, lambda: {}) == {}


def test_g5_bi_thanh_escalation_trong_khi_kiem_lai_dai(tmp_path):
    vao, tha = threading.Event(), threading.Event()

    def boc(argv):
        vao.set()
        tha.wait(20)                                    # "suite 15 phút" của bead hr-1
        return argv

    t = dung(tmp_path, bug(**GIU), bug("hr-2", **GIU), boc=boc)
    g = BdKhoa(t.g)
    t.bo.tao_bd = lambda d: g
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    dung_ev = threading.Event()
    luong = bat_dau_luong_giao(t.bo, dung_ev, chu_ky=0.05)
    try:
        assert vao.wait(10)                             # luồng Git đang kẹt trong kiểm lại
        bi(t, "hr-2")
        assert cho_toi(lambda: any("bead_goc: hr-2" in b.description for b in g.tat_ca()
                                   if b.issue_type == "decision"))
        assert not tha.is_set() and loai(t, "kiem.lai") == []
        tha.set()
        assert cho_toi(lambda: len(loai(t, "kiem.lai")) == 1)
    finally:
        tha.set()
        dung_ev.set()
        for x in luong:
            x.join(timeout=10)
    assert not any(x.is_alive() for x in luong) and len(loai(t, "kiem.lai")) == 1


def test_khoi_dong_lai_giua_kiem_lai_thi_vong_sau_kiem_lai_lai(tmp_path, tram_home_tam):
    lan = []

    def boc(argv):
        lan.append(argv)
        if len(lan) == 1:
            raise RuntimeError("tram-api tắt giữa chừng")
        return argv

    t = dung(tmp_path, bug(**GIU), boc=boc)
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    with pytest.raises(RuntimeError):
        chay_vong(KHOA_GIT, lambda: vong_git(t.bo))
    assert loai(t, "kiem.lai") == [] and list((tram_home_tam / "kiem").glob("*")) == []      # 3c: không còn bản chép
    assert chay_vong(KHOA_GIT, lambda: vong_git(t.bo))["kiem_lai"] == 1
    assert "kiem_lai" not in chay_vong(KHOA_GIT, lambda: vong_git(t.bo)) and len(loai(t, "kiem.lai")) == 1
