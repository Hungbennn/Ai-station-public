"""Cổng lượt kiểm lại (3C-D2; C01, D45) — "lịch ngoài phạm vi hoặc cleanup không rõ thì chặn lượt sau", bền trên đĩa.

`vao(luot)`: chỉ đi tiếp khi tệp trạng thái ghi `mo` VÀ một lượt quan sát sạch (bắt tàn dư tái sinh sau khi mở); ghi
`dang-chay` TRƯỚC khi chép hay nhận môi trường kiểm. `ra()`: thu hồi (giết mọi tiến trình của `tram-kiem`) rồi quan
sát HAI lần cách `cho` giây; sạch mới ghi `mo`. Bất kỳ lỗi nào — quan sát thấy tàn dư, quan sát không chạy được, hết
hạn, định dạng lạ — ghi `dong` kèm lý do và ném `CongDong`. Trạm chết giữa lượt để lại `dang-chay` = đóng. Chỉ Đại ca mở
lại (`tram giao mo-cong-kiem` → `mo_lai`) sau khi xem; `mo_lai` cũng phải thu hồi + quan sát sạch. Quan sát chỉ là
bằng chứng bổ trợ; ranh giới cưỡng chế là hồ sơ Seatbelt của lượt (`boc_luot`, 3C-D1)."""
import json
import os
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from tram.giao_viec.ban_chep import LoiBanChep

TRANG_THAI = ("mo", "dang-chay", "dong")


class CongDong(LoiBanChep):
    """Cổng kiểm lại đóng: lượt trước chưa được thu hồi/xác nhận sạch — không chép, không nhận môi trường kiểm."""


@dataclass
class CongLuot:
    tep: Path
    thu_hoi: Callable[[], None]
    quan_sat: Sequence[Callable[[], None]]
    ngu: Callable[[float], None] = time.sleep
    cho: float = 5.0

    def trang_thai(self) -> dict:
        try:
            tt = json.loads(self.tep.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"trang_thai": "chua-mo"}
        except (OSError, ValueError):
            return {"trang_thai": "hong"}
        return tt if isinstance(tt, dict) and tt.get("trang_thai") in TRANG_THAI else {"trang_thai": "hong"}

    def _ghi(self, tt: dict) -> None:
        self.tep.parent.mkdir(parents=True, exist_ok=True)
        tam = self.tep.with_name(self.tep.name + ".tam")
        with open(tam, "w", encoding="utf-8") as f:
            f.write(json.dumps(tt, ensure_ascii=False))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tam, self.tep)
        fd = os.open(self.tep.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def dong(self, ly_do: str) -> None:
        self._ghi({"trang_thai": "dong", "ly_do": ly_do})

    def _sach(self, ly_do: str, *, lan: int) -> None:
        try:
            for i in range(lan):
                if i:
                    self.ngu(self.cho)                    # nguồn tái sinh trễ phải lộ ra giữa hai lần quan sát
                for q in self.quan_sat:
                    q()
        except Exception as e:                            # noqa: BLE001 — mọi lỗi quan sát đều đóng cổng
            self.dong(f"{ly_do}: {type(e).__name__}: {e}")
            raise CongDong(f"{ly_do}: {e}") from e

    def vao(self, luot: str) -> None:
        tt = self.trang_thai()
        if tt["trang_thai"] != "mo":
            raise CongDong(f"cổng kiểm lại {tt['trang_thai']} ({tt.get('ly_do') or tt.get('luot') or 'chưa xác nhận'})"
                           " — Đại ca xem rồi chạy `tram giao mo-cong-kiem`")
        self._sach(f"trước lượt {luot}", lan=1)
        self._ghi({"trang_thai": "dang-chay", "luot": luot})

    def ra(self, luot: str) -> None:
        if self.trang_thai() != {"trang_thai": "dang-chay", "luot": luot}:
            self.dong(f"sau lượt {luot}: trạng thái cổng không phải dang-chay của lượt này")
            raise CongDong(f"sau lượt {luot}: trạng thái cổng bị đổi giữa lượt")
        self._thu_hoi_va_xet(f"sau lượt {luot}")

    def mo_lai(self) -> None:
        self._thu_hoi_va_xet("mở lại")

    def _thu_hoi_va_xet(self, ly_do: str) -> None:
        try:
            self.thu_hoi()
        except Exception as e:                            # noqa: BLE001
            self.dong(f"{ly_do}: thu hồi lỗi: {type(e).__name__}: {e}")
            raise CongDong(f"{ly_do}: thu hồi lỗi: {e}") from e
        self._sach(ly_do, lan=2)
        self._ghi({"trang_thai": "mo"})
