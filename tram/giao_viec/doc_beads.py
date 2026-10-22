"""Đọc beads cho bộ chọn việc qua bộ đệm của tram-api (`BoDemBeads`, tuổi ≤ 30 s — 4a-1 rủi ro c): mỗi lần khe xin
việc không còn chạy `bd list` cho mọi dự án. `bd ready` đệm cùng tuổi, hết hạn khi danh sách beads đổi phiên bản.
Snapshot cũ ≤ 30 s chấp nhận được vì bộ chọn luôn đọc lại bead được chọn ngay trước cấp (`doc_lai.py`)."""
import threading
import time
from collections.abc import Callable

from tram.api.bo_dem import BoDemBeads
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn


class DocBeads:
    def __init__(self, bo_dem: BoDemBeads, *, tuoi: float = 30.0, dong_ho: Callable[[], float] = time.monotonic):
        self._bo_dem, self._tuoi, self._dong_ho = bo_dem, tuoi, dong_ho
        self._khoa = threading.Lock()
        self._san: dict[str, tuple[int, float, set[str]]] = {}

    def lay(self, da: DuAn, bd) -> tuple[list[Bead], set[str]]:
        """(beads từ bộ đệm, id trong `bd ready`)."""
        beads = self._bo_dem.lay(da.ten)
        pb = self._bo_dem.phien_ban(da.ten)
        with self._khoa:
            co = self._san.get(da.ten)
        if co is not None and co[0] == pb and self._dong_ho() - co[1] < self._tuoi:
            return beads, co[2]
        san = bd.san_sang()
        with self._khoa:
            self._san[da.ten] = (pb, self._dong_ho(), san)
        return beads, san

    def danh_dau_cu(self, du_an: str) -> None:
        """Sau khi trạm ghi beads (claim): lần đọc sau — của bộ chọn và của dashboard — đọc mới."""
        self._bo_dem.danh_dau_cu(du_an)
        with self._khoa:
            self._san.pop(du_an, None)
