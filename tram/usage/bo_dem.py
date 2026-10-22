"""Bộ đệm kết quả ccusage theo khoảng ngày: `ok` giữ 10 phút, lỗi giữ 1 phút — ccusage quét toàn bộ log Claude
Code nên chậm; màn Usage tải lại không được chạy nó mỗi lần (plan 2b G6)."""
import threading
import time
from collections.abc import Callable
from datetime import date

from tram.usage.ccusage import KetQuaCcusage

GIAY_OK, GIAY_LOI, TOI_DA = 600, 60, 32


class BoDemCcusage:
    def __init__(self, doc: Callable[[date, date], KetQuaCcusage], *, dong_ho: Callable[[], float] = time.monotonic):
        self._doc, self._dong_ho = doc, dong_ho
        self._nho: dict[tuple[date, date], tuple[float, KetQuaCcusage]] = {}
        self._khoa = threading.Lock()

    def lay(self, tu: date, den: date) -> KetQuaCcusage:
        with self._khoa:
            bay_gio = self._dong_ho()
            cu = self._nho.get((tu, den))
            if cu is not None and bay_gio - cu[0] < (GIAY_OK if cu[1].trang_thai == "ok" else GIAY_LOI):
                return cu[1]
            # Một adapter ngoài tại một thời điểm; request đồng thời cùng khoảng dùng kết quả này.
            kq = self._doc(tu, den)
            if len(self._nho) >= TOI_DA:
                self._nho.clear()
            self._nho[(tu, den)] = (self._dong_ho(), kq)
            return kq
