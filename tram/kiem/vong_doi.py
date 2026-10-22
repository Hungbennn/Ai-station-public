"""Vòng đời MỘT tiến trình con có hạn (P1): primitive DUY NHẤT spawn rồi chờ/giết; `khoi_chay` LUÔN `start_new_session`,
sở hữu từ PID theo `so_huu` (A03, R2-02). `cho` chụp cây theo định danh (pid, sinh) mỗi `CHU_KY_CHUP` giây, biết gốc
thoát mà KHÔNG gặt (`giu_xac`). `thu_hoi`: SIGTERM → `cho_term` → SIGKILL → `cho_cuoi`, mỗi pha chụp mới; nhóm gốc
chưa gặt qua `kill`, nhóm khác CHỈ qua `kill_uid(kill)` sau `van_o_nhom` (`gui_tin`, A01). True = cây QUAN SÁT ĐƯỢC
đã hết, không mơ hồ — rồi mới gặt; KHÔNG chứng minh hết tàn dư lẩn khỏi tầm chụp (khe thợ: `tho.don_uid`, A02)."""
import math
import os
import signal
import subprocess
import time
from collections.abc import Callable

from tram.kiem.bang_tien_trinh import chup_nhan, mot_nhan, van_o_nhom
from tram.kiem.cay_tien_trinh import TienTrinh, cay, mo_ho
from tram.kiem.giu_xac import Goc
from tram.kiem.gui_tin import LOI_GUI, Kill, kill_cuc_bo, kill_uid  # noqa: F401 — tên cũ, người gọi import từ đây
from tram.kiem.ngat import hoan

CHU_KY_CHUP = 0.25


class LoiThuHoi(RuntimeError):
    """Không xác nhận được cây tiến trình đã hết — kết quả không được công nhận, cổng giữ đóng."""


class Nhom:
    def __init__(self, p: subprocess.Popen, *, kill: Kill, chup: Callable[[], list[TienTrinh]] = chup_nhan,
                 mot: Callable[[int], TienTrinh | None] = mot_nhan):
        self.p, self.kill, self.chup, self.mot, self.goc = p, kill, chup, mot, Goc(p)
        self.kill_uid, self.ket_thu_hoi = kill_uid(kill), None          # kênh theo UID | None; None: chưa thu hồi
        # khoá (pid, sinh) của cây ở ảnh gần nhất; số nhóm cây từng có — CHỈ để nhận ra "mơ hồ", không để gửi
        self.biet, self.nhom_biet, self.mo_ho = set(), {p.pid}, False
        self.lan_chup = time.monotonic() - CHU_KY_CHUP + 0.05         # lần chụp đầu sau 0,05 s

    def cho(self, giay: float) -> int | None:
        if not math.isfinite(giay):
            raise ValueError("hạn chờ phải hữu hạn")
        het = time.monotonic() + max(0.0, giay)
        while True:
            if self.goc.thoat(max(0.0, min(het, self.lan_chup + CHU_KY_CHUP) - time.monotonic())):
                return self.goc.ma()
            if time.monotonic() >= self.lan_chup + CHU_KY_CHUP:
                self.cay()
            if time.monotonic() >= het:
                return None

    def cay(self) -> list[TienTrinh] | None:
        """Cây hiện tại; None khi không chụp được (không xác nhận được gì, giữ những gì đã biết)."""
        self.lan_chup = time.monotonic()
        try:
            ds = self.chup()
        except (OSError, subprocess.SubprocessError, ValueError):
            return None
        goc = self.p.pid if self.goc.chua_gat() else None
        con = cay(ds, goc, self.biet)
        self.mo_ho |= bool(mo_ho(ds, con, self.nhom_biet))
        self.biet = {t.khoa for t in con if t.khoa is not None}
        self.nhom_biet = {t.pgid for t in con} | ({goc} if goc else set())
        return con

    def _gui(self, sig: int, han: float) -> None:
        con, goc = self.cay() or [], self.p.pid if self.goc.chua_gat() else None
        for g in sorted(({t.pgid for t in con} | ({goc} if goc else set())) - {0, 1, os.getpgrp()}):
            if time.monotonic() >= han:
                return
            gui = self.kill if g == goc else self.kill_uid
            if gui is None or (g != goc and not van_o_nhom([t for t in con if t.pgid == g], g, mot=self.mot)):
                continue
            try:
                gui(g, sig)
            except LOI_GUI:
                pass

    def _cho_het(self, giay: float) -> list[TienTrinh] | None:
        het = time.monotonic() + giay
        self.goc.thoat(giay)
        while True:
            con = self.cay()
            if self._sach(con) or time.monotonic() >= het:
                return con
            time.sleep(0.05)

    def _sach(self, con: list[TienTrinh] | None) -> bool:       # gốc đã thoát, chỉ còn xác gốc, chưa gặp mơ hồ
        return con is not None and not self.mo_ho and self.goc.thoat() and all(t.pid == self.p.pid for t in con)

    def thu_hoi(self, *, cho_term: float = 2.0, cho_cuoi: float = 2.0, han_gui: float = 10.0) -> bool:
        con = self.cay()
        for sig, cho in ((signal.SIGTERM, cho_term), (signal.SIGKILL, cho_cuoi)):
            if self._sach(con):
                break
            self._gui(sig, time.monotonic() + han_gui)
            con = self._cho_het(cho)
        self.ket_thu_hoi = self._sach(con)
        if self.ket_thu_hoi:
            self.goc.gat()
        return self.ket_thu_hoi


def khoi_chay(argv: list[str], *, kill: Kill, chu: list, popen: Callable = subprocess.Popen,
              chup: Callable[[], list[TienTrinh]] = chup_nhan, **kw) -> Nhom:
    """Hợp đồng `so_huu` mục 1: `Nhom` vào `chu` TRONG `hoan()`, trước mọi lối ra sau Popen; gốc không theo dõi được
    (`Goc.hong`) → `LoiThuHoi`, `Nhom` vẫn ở `chu` — người gọi thu hồi (không bao giờ xác nhận), cổng đóng."""
    if not isinstance(chu, list):
        raise TypeError("chu phải là list sở hữu của người gọi")
    kw["start_new_session"] = True
    with hoan():
        n = Nhom(popen(argv, **kw), kill=kill, chup=chup)
        chu.append(n)
    if n.goc.hong:
        raise LoiThuHoi("không theo dõi được gốc — tiến trình ở danh sách sở hữu của người gọi, chưa xác nhận thu hồi")
    return n


def cho_den_dung(n: Nhom, dung, *, cho_term: float) -> tuple[int | None, bool]:
    """CLI của phiếu: chờ thoát hoặc `dung` được đặt (hạn của lần chạy là bộ hẹn đặt `dung` — `mot_lan`), rồi thu hồi cả
    cây trong hạn hữu hạn. Trả (mã thoát | None, đã xác nhận thu hồi)."""
    while (ma := n.cho(0.05)) is None and not dung.is_set():
        pass
    sach = n.thu_hoi(cho_term=cho_term)
    return (n.p.returncode if ma is None else ma), sach
