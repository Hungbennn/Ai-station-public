"""Danh tính THỰC của principal (lát 3C-B, dot6-C02). Không tin tên (`getpass.getuser()` đọc env), không so argv của
`boc`: chạy `/bin/sleep` qua ĐÚNG `boc` của principal, đọc UID hiệu lực + UID thực mà NHÂN ghi cho cả cây đó (`ps`,
chỉ cột số), rồi thu hồi cây (P1). Chờ tới khi mọi LÁ của cây (tiến trình không có con trong cây) không còn là root —
tức `sudo` đã đổi UID và exec xong. Đạt khi: tài khoản đích có thật, không phải root, không phải người vận hành; mọi lá
có uid = ruid = UID đích; mọi tiến trình không phải lá là root (chính `sudo`, monitor pty). Sai lệch, wrapper không đổi
UID, không thấy tiến trình dò, quá hạn hay lỗi `ps` → `LoiDanhTinh`; không thu hồi được cây dò → `LoiThuHoi` (người gọi
dừng như mọi ca chưa thu hồi). Cả hai: KHÔNG được chạm lịch."""
import os
import pwd
import subprocess
import time
from collections.abc import Callable

from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.so_huu import so_huu
from tram.kiem.vong_doi import Kill, khoi_chay

SLEEP = "/bin/sleep"


class LoiDanhTinh(RuntimeError):
    """Chưa chứng minh được tiến trình chạy dưới đúng UID của principal."""


def la_cua(cay: list[TienTrinh]) -> list[TienTrinh]:
    cha = {t.ppid for t in cay}
    return [t for t in cay if t.pid not in cha]


def quan_sat(boc: Callable[[list[str]], list[str]], kill: Kill, *, khoi: Callable = khoi_chay,
             chup: Callable[[], list[TienTrinh]] = chup_nhan, han: float = 10.0) -> list[TienTrinh]:
    """Cây của tiến trình dò lúc mọi lá đã rời UID root. Sở hữu theo `so_huu` (R2-02): spawn trong khối sở hữu."""
    with so_huu("không xác nhận thu hồi tiến trình dò", cho_term=1.0, cho_cuoi=1.0, han_gui=2.0) as chu:
        try:
            n = khoi(boc([SLEEP, "30"]), kill=kill, chup=chup, chu=chu, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin"})
        except (OSError, ValueError) as e:
            raise LoiDanhTinh(f"không khởi chạy được tiến trình dò: {type(e).__name__}") from None
        het = time.monotonic() + han
        while time.monotonic() < het and not n.goc.thoat():          # A03: chỉ `Nhom.thu_hoi` gặt gốc
            con = n.cay()
            if con and all(t.uid != 0 for t in la_cua(con)):
                return con
            time.sleep(0.05)
        raise LoiDanhTinh("không thấy tiến trình dò dưới boc (wrapper lỗi, bị từ chối hoặc quá hạn)")


def uid_cua(ten: str) -> int:
    return pwd.getpwnam(ten).pw_uid


def xac_minh_uid(ten: str, boc: Callable[[list[str]], list[str]], kill: Kill, *, toi: int | None = None,
                 tra_uid: Callable[[str], int] = uid_cua, quan_sat_: Callable = quan_sat) -> int:
    """UID đã chứng minh của principal `ten`."""
    toi = os.getuid() if toi is None else toi
    try:
        mong = tra_uid(ten)
    except (KeyError, OSError, TypeError):
        raise LoiDanhTinh("tài khoản principal không có trên máy") from None
    if mong in (0, toi):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành — không phải tài khoản cách ly")
    cay = quan_sat_(boc, kill)
    la = la_cua(cay)
    uid_la = {(t.uid, t.ruid) for t in la}
    khac = {t.uid for t in cay if t not in la and t.uid != 0}
    if uid_la != {(mong, mong)} or khac:
        raise LoiDanhTinh(f"UID thực của tiến trình dò {sorted(uid_la)} (khác: {sorted(khac)}) ≠ {mong}")
    return mong
