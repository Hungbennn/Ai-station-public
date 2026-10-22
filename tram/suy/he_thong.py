"""Đọc dịch vụ launchd + Keychain cho trang Cài đặt (D19; khảo sát §1.6, §1.10 mục 4–6). CHỈ ĐỌC.

argv chỉ dựng từ hằng số (+ uid của tiến trình), timeout 3 giây, gọi tuần tự. KHÔNG BAO GIỜ trả stdout, stderr,
argv, nội dung exception hay pid — chỉ trả boolean / mã trạng thái cố định. `security` không bao giờ kèm `-w`
(như `tram/chu/cai_dat.py::_co_keychain`). Bộ đệm trong tiến trình (mẫu `BoDemCcusage`): dịch vụ 30 giây,
Keychain 60 giây."""
import os
import subprocess
import threading
import time
from collections.abc import Callable
from pathlib import Path

from tram.chu.launchd import NHAN_API, NHAN_BAO_TIN, NHAN_NHO, NHAN_QUET, NHAN_SAO_LUU

DICH_VU = ((NHAN_API, "dashboard + API"), (NHAN_QUET, "quét + chấm cột"), (NHAN_NHO, "memory 127.0.0.1:7710"),
           (NHAN_BAO_TIN, "Telegram"), (NHAN_SAO_LUU, "sao lưu su-kien.db"))
# Tên mục Keychain: bao_tin/telegram.py, llm/claude.py, nho/khach.py, api/noi_bo.py — chỉ kiểm có/chưa.
KEYCHAIN = ("tram-telegram-bot-token", "tram-anthropic-api-key", "tram-nho-token", "tram-noi-bo-token")
MA_KEYCHAIN = {0: "co", 44: "chua"}          # 44 = errSecItemNotFound; mã khác (Keychain khoá…) → khong_ro
GIAY_CHO, GIAY_DICH_VU, GIAY_KEYCHAIN = 3, 30, 60

Chay = Callable[[list[str]], tuple[int, str]]


def chay_that(argv: list[str]) -> tuple[int, str]:
    """Chạy argv (không shell), trả (mã thoát, stdout). Lỗi/timeout ném ra — `DocHeThong` nuốt, không trả tiếp."""
    kq = subprocess.run(argv, capture_output=True, text=True, timeout=GIAY_CHO, stdin=subprocess.DEVNULL)
    return kq.returncode, kq.stdout


def _dang_chay(stdout: str) -> bool:
    """Dòng `state = …` đầu tiên của `launchctl print` (khối ngoài cùng đứng trước khối con)."""
    for dong in stdout.splitlines():
        s = dong.strip()
        if s.startswith("state ="):
            return s == "state = running"
    return False


class DocHeThong:
    def __init__(self, *, chay: Chay = chay_that, home: Path | None = None, uid: int | None = None,
                 dong_ho: Callable[[], float] = time.monotonic):
        self._chay, self._dong_ho = chay, dong_ho
        self._home = home if home is not None else Path.home()
        self._uid = uid if uid is not None else os.getuid()
        self._nho: dict[str, tuple[float, list[dict]]] = {}
        self._khoa = threading.Lock()

    def _dem(self, khoa: str, giay: int, doc: Callable[[], list[dict]]) -> list[dict]:
        with self._khoa:                                   # một lượt đọc tại một thời điểm; request khác chờ
            bay = self._dong_ho()
            cu = self._nho.get(khoa)
            if cu is None or bay - cu[0] >= giay:
                cu = self._nho[khoa] = (bay, doc())
            return [dict(x) for x in cu[1]]

    def _mot_dich_vu(self, nhan: str, viec: str) -> dict:
        da_cai = (self._home / "Library" / "LaunchAgents" / f"{nhan}.plist").is_file()
        try:
            ma, ra = self._chay(["launchctl", "print", f"gui/{self._uid}/{nhan}"])
        except Exception:                                  # không đưa exception ra ngoài (khảo sát §1.10 mục 4)
            return {"nhan": nhan, "viec": viec, "da_cai": da_cai, "dang_chay": None, "kiem_duoc": False}
        return {"nhan": nhan, "viec": viec, "da_cai": da_cai, "dang_chay": ma == 0 and _dang_chay(ra),
                "kiem_duoc": True}                         # mã ≠ 0: chưa nạp → không chạy

    def _mot_keychain(self, ten: str) -> dict:
        try:
            ma, _ = self._chay(["security", "find-generic-password", "-s", ten])   # KHÔNG -w: không đọc giá trị
        except Exception:
            return {"ten": ten, "trang_thai": "khong_ro"}
        return {"ten": ten, "trang_thai": MA_KEYCHAIN.get(ma, "khong_ro")}

    def dich_vu(self) -> list[dict]:
        return self._dem("dich_vu", GIAY_DICH_VU, lambda: [self._mot_dich_vu(n, v) for n, v in DICH_VU])

    def keychain(self) -> list[dict]:
        return self._dem("keychain", GIAY_KEYCHAIN, lambda: [self._mot_keychain(t) for t in KEYCHAIN])


_CHUNG: DocHeThong | None = None
_KHOA_CHUNG = threading.Lock()


def doc_he_thong() -> DocHeThong:
    """Một thể hiện dùng chung cho cả tiến trình (bộ đệm chung). Test thay `_CHUNG` bằng monkeypatch."""
    global _CHUNG
    with _KHOA_CHUNG:
        if _CHUNG is None:
            _CHUNG = DocHeThong()
        return _CHUNG
