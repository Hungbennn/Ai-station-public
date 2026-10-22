"""Bộ đệm beads theo dự án (spec 2 §3): tuổi tối đa 30 s, làm mới ngay khi bị đánh dấu cũ (G1)."""
import threading
import time
from collections.abc import Callable

from tram.beads.mo_hinh import Bead


class BoDemBeads:
    def __init__(self, tao_bd: Callable[[str], object], *, tuoi_toi_da: float = 30.0,
                 dong_ho: Callable[[], float] = time.monotonic):
        self._tao_bd, self._tuoi, self._dong_ho = tao_bd, tuoi_toi_da, dong_ho
        self._khoa = threading.Lock()
        self._du_lieu: dict[str, tuple[float, list[Bead]]] = {}
        self._cu: set[str] = set()
        self._dau: dict[str, tuple] = {}
        self._phien_ban: dict[str, int] = {}

    def lay(self, du_an: str) -> list[Bead]:
        with self._khoa:
            co = self._du_lieu.get(du_an)
            if co is not None and du_an not in self._cu and self._dong_ho() - co[0] < self._tuoi:
                return co[1]
            self._cu.discard(du_an)          # đánh dấu xảy ra trong lúc đọc sẽ được giữ cho lần sau
        beads = self._tao_bd(du_an).tat_ca()
        dau = tuple(sorted((b.id, b.updated_at, b.status, tuple(sorted(b.labels))) for b in beads))
        with self._khoa:
            self._du_lieu[du_an] = (self._dong_ho(), beads)
            if self._dau.get(du_an) != dau:
                self._dau[du_an] = dau
                self._phien_ban[du_an] = self._phien_ban.get(du_an, 0) + 1
        return beads

    def danh_dau_cu(self, du_an: str) -> None:
        with self._khoa:
            self._cu.add(du_an)

    def phien_ban(self, du_an: str) -> int:
        with self._khoa:
            return self._phien_ban.get(du_an, 0)
