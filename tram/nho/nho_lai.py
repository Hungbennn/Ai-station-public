"""Recall (spec 1b §7) — lấy ứng viên RIÊNG từng nhóm, chấm, chọn 3/1/1, không bù chéo.

Phỏng theo crewAI (MIT — xem NOTICE): mỗi nhóm là một "lát" phạm vi (ý MemorySlice), nhưng lát chỉ do vùng cấp
của trạm quyết, lọc `pham_vi IN` so khớp chính xác."""
import threading
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from tram.nho.cham_diem import chon
from tram.nho.embed import Embedder
from tram.nho.kho import KhoKyUc
from tram.nho.pham_vi import NHOM_MAC_DINH, chia_nhom, mo_rong

SO_UNG_VIEN = 50
CHU_KY_GHI_DUNG = timedelta(minutes=10)


@dataclass(frozen=True)
class KyUcTra:
    """Đầu ra cho 1a và gói ngữ cảnh: KHÔNG có `nguon` (tránh lộ dự án/bead khác qua /chung, /vai)."""
    id: str
    noi_dung: str
    pham_vi: str

    def sang_dict(self) -> dict:
        return {"id": self.id, "noi_dung": self.noi_dung, "pham_vi": self.pham_vi}


def iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class BoDemDung:
    """Gom thống kê dùng (`dung_luc`, `so_lan_dung`) — ghi kho tối đa mỗi 10 phút (§7 bước 5)."""

    def __init__(self, chu_ky: timedelta = CHU_KY_GHI_DUNG):
        self._chu_ky, self._dem, self._khoa = chu_ky, Counter(), threading.Lock()
        self._xa_cuoi: datetime | None = None

    def ghi_nhan(self, ids: Iterable[str]) -> None:
        with self._khoa:
            self._dem.update(ids)

    def xa_neu_den_han(self, kho: KhoKyUc, bay_gio: datetime, *, ep: bool = False) -> int:
        with self._khoa:
            if self._xa_cuoi is None:
                self._xa_cuoi = bay_gio
            if not self._dem or (not ep and bay_gio - self._xa_cuoi < self._chu_ky):
                return 0
            dem, self._dem, self._xa_cuoi = self._dem, Counter(), bay_gio
        kho.cap_nhat_dung(dem, iso(bay_gio))
        return sum(dem.values())


def nho_lai(kho: KhoKyUc, embedder: Embedder, truy_van: str, vung_cap: list[str], *,
            nhom: Mapping[str, int] | None = None, bay_gio: datetime | None = None,
            dem_dung: BoDemDung | None = None) -> list[KyUcTra]:
    tap = mo_rong(vung_cap)                                 # sai vùng cấp → LoiVungCap, chưa gọi embedder
    han = dict(NHOM_MAC_DINH if nhom is None else nhom)
    if not isinstance(truy_van, str) or not truy_van.strip():
        raise ValueError("Truy vấn rỗng")
    bg = bay_gio or datetime.now(timezone.utc)
    v = embedder.embed([truy_van])[0]                       # lỗi → LoiEmbedder, không lùi về gì khác
    chon_ra = []
    for ten, ds in chia_nhom(tap).items():
        if han.get(ten, 0) <= 0:
            continue
        uv = kho.tim(v, ds, mo_hinh=embedder.mo_hinh, gioi_han=SO_UNG_VIEN, bay_gio=iso(bg))
        chon_ra += chon(uv, han[ten], bg)
    if dem_dung is not None:
        dem_dung.ghi_nhan(k.id for k in chon_ra)
    return [KyUcTra(k.id, k.noi_dung, k.pham_vi) for k in chon_ra]
