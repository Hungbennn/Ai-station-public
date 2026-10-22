"""Ba luồng tick trong tiến trình tram-api (spec 4 §10; G5 ≤ 3 phút): `tram-giao-nhanh` (escalation, câu hỏi, hết
ngân sách — không bao giờ chờ Git hay lệnh kiểm), `tram-giao-git` (fetch, xét `bao.xong`, kiểm lại tới 15 phút/lệnh,
cột 3) và `tram-giao-deploy` (TM-3: chuỗi deploy → kiểm còn sống → lùi, tới ~32 phút — không chặn kiểm lại).
Lịch theo nhịp cố định: vòng sau bắt đầu `chu_ky` giây sau khi vòng trước BẮT ĐẦU (vòng dài hơn thì chạy
ngay) → bí/câu hỏi được xử lý trong ≤ chu_ky + một vòng nhanh. Khoá file (`flock`) mỗi pha giữ một vòng trên cả máy:
`tram giao tick` chạy tay song song với tram-api không làm trùng việc (khoá tự nhả khi tiến trình chết)."""
import fcntl
import sys
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from tram.duong_dan import tram_home
from tram.giao_viec.tick import vong_deploy, vong_git, vong_nhanh

KHOA_NHANH, KHOA_GIT, KHOA_DEPLOY = "giao-nhanh.lock", "giao-git.lock", "giao-deploy.lock"


@contextmanager
def giu_khoa(ten: str) -> Iterator[bool]:
    p = tram_home() / "khoa" / ten
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def chay_vong(khoa: str, lam: Callable[[], dict]) -> dict | None:
    """None = pha này đang có vòng khác chạy (luồng của tram-api hoặc lệnh tay)."""
    with giu_khoa(khoa) as duoc:
        return lam() if duoc else None


def lap(dung: threading.Event, lam: Callable[[], object], chu_ky: float, ten: str, *,
        dong_ho: Callable[[], float] = time.monotonic) -> None:
    while not dung.is_set():
        bat_dau = dong_ho()
        try:
            lam()
        except Exception as e:                          # noqa: BLE001 — ghi stderr, vòng sau làm lại (idempotent)
            print(f"[{ten}] lỗi: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        dung.wait(max(0.0, chu_ky - (dong_ho() - bat_dau)))


def bat_dau_luong_giao(bo, dung: threading.Event, *, chu_ky: float) -> list[threading.Thread]:
    ra = []
    for ten, khoa, pha in (("tram-giao-nhanh", KHOA_NHANH, lambda: vong_nhanh(bo)),
                           ("tram-giao-git", KHOA_GIT, lambda: vong_git(bo)),
                           ("tram-giao-deploy", KHOA_DEPLOY, lambda: vong_deploy(bo))):
        t = threading.Thread(target=lap, args=(dung, lambda k=khoa, p=pha: chay_vong(k, p), chu_ky, ten),
                             name=ten, daemon=True)
        t.start()
        ra.append(t)
    return ra
