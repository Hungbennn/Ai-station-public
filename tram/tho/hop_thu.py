"""Hộp thư đi BỀN của một khe (spec 3 §6.6, 3a-1 G35): thân `POST /api/tho/bao|su-kien` (gồm `request_id`) được GHI
+ fsync TRƯỚC khi gửi, gửi đúng thứ tự (`chay.bat_dau` trước `chay.xong`); restart hay mất mạng → gửi lại phần chưa
xác nhận với CÙNG thân. Trạm trả 2xx/4xx là đã xử lý xong (4xx: từ chối dứt khoát — người gọi xem mã); 5xx hoặc
không gọi được → dừng, lần sau gửi tiếp. `da-push` KHÔNG qua đây (idempotent theo request_id tất định, có vòng thử lại
riêng) để công bố treo không chặn được báo dừng mềm."""
import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path

from tram.tho.khach import KhachTram, LoiKhachTram


@dataclass(frozen=True)
class DaGui:
    so: int
    duong: str
    than: dict
    ma: int
    kq: dict


class HopThu:
    def __init__(self, goc: Path):
        self.p, self.moc = goc / "hop-thu.jsonl", goc / "hop-thu.da-gui"
        self._khoa = threading.RLock()          # nhịp tim, bộ đọc hàng đợi và vòng chính cùng gửi

    def _dong(self) -> list[dict]:
        return [json.loads(d) for d in self.p.read_text(encoding="utf-8").splitlines()] if self.p.exists() else []

    def _da_gui(self) -> int:
        return int(self.moc.read_text() or 0) if self.moc.exists() else 0

    def them(self, duong: str, than: dict) -> int:
        so = len(self._dong())
        with open(self.p, "a", encoding="utf-8") as f:
            f.write(json.dumps({"so": so, "duong": duong, "than": than}, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return so

    def co(self, dieu_kien) -> bool:
        """Đã từng ghi dòng thoả `dieu_kien(duong, than)` chưa (vd đã có `chay.xong` của lần này)."""
        return any(dieu_kien(d["duong"], d["than"]) for d in self._dong())

    def cho_gui(self) -> list[dict]:
        return self._dong()[self._da_gui():]

    def gui(self, khach: KhachTram) -> list[DaGui]:
        with self._khoa:
            return self._gui(khach)

    def _gui(self, khach: KhachTram) -> list[DaGui]:
        ra = []
        for d in self.cho_gui():
            try:
                ma, kq = khach.goi("POST", d["duong"], d["than"])
            except LoiKhachTram:
                break
            if ma >= 500 or ma == 401:
                break
            self.moc.write_text(str(d["so"] + 1))
            ra.append(DaGui(d["so"], d["duong"], d["than"], ma, kq))
        return ra

    def gui_mot(self, khach: KhachTram, duong: str, than: dict) -> DaGui | None:
        """Ghi rồi gửi mọi thứ đang chờ; trả kết quả của chính dòng này nếu đã tới được trạm."""
        with self._khoa:
            so = self.them(duong, than)
            return next((x for x in self._gui(khach) if x.so == so), None)

    def don(self) -> bool:
        """Xoá hộp thư khi đã gửi hết (phiếu kết thúc). Còn dòng chờ → giữ, trả False."""
        if self.cho_gui():
            return False
        self.p.unlink(missing_ok=True)
        self.moc.unlink(missing_ok=True)
        return True
