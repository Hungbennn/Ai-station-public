"""Trạng thái bền của MỘT khe phía tiến trình quản lý thợ (spec 3 §7.2, §8.3): `~/.tram/tho/<máy>/<khe>/` (0700,
chỉ tài khoản quản lý thợ — chứa `ma_giao` trong `phieu.json`). Hàng đợi `tram bao` ở cây riêng
`~/.tram/hang-doi/<máy>/<khe>/` để S6 trao quyền ghi cho principal của khe mà không mở thư mục này."""
import json
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tram.duong_dan import doc_luc, tram_home
from tram.han_muc.mo_hinh import HanMuc
from tram.tho.cau_hinh_chay import CauHinhChay


def gio_utc(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ghi_nguyen_tu(p: Path, noi_dung: str, che_do: int = 0o600) -> None:
    """Ghi file tạm riêng của luồng rồi `os.replace` — nhiều luồng cùng ghi không giẫm file tạm của nhau."""
    tam = p.with_name(f"{p.name}.{os.getpid()}-{threading.get_ident()}.tam")
    fd = os.open(tam, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, che_do)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(noi_dung)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tam, p)


@dataclass
class TrangThaiPhieu:
    """Phiếu đang giữ + tiến độ — đọc lại khi `tram tho chay` khởi động lại (không xin lại phiếu — 3a-1 G12)."""
    phieu: dict                       # Phieu.model_dump() — GỒM ma_giao
    nhan_luc: str                     # mốc trần thời gian của phiếu (§7.6: wall-clock từ lúc nhận)
    lan: int = 0                      # số lần chạy CLI đã bắt đầu
    token_ra: int = 0
    vi_tri_hang_doi: int = 0
    ban_giao_tam: dict | None = None  # bàn giao tạm gần nhất (từ `moc`/`bi`)
    ket_thuc: dict = field(default_factory=dict)    # đã quyết kết thúc gì (để làm lại sau restart)


class SoKhe:
    def __init__(self, may_id: str, ten: str, goc: Path | None = None):
        """`goc`: ~/.tram của tài khoản quản lý thợ (test truyền thư mục tạm)."""
        goc = goc or tram_home()
        self.goc, self.hang_doi = goc / "tho" / may_id / ten, goc / "hang-doi" / may_id / ten
        self.goc.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.hang_doi.mkdir(parents=True, exist_ok=True)
        self.pid = self.goc / "dang-chay.pid"

    def luu_phieu(self, tt: TrangThaiPhieu) -> None:
        ghi_nguyen_tu(self.goc / "phieu.json", json.dumps(asdict(tt), ensure_ascii=False))

    def doc_phieu(self) -> TrangThaiPhieu | None:
        p = self.goc / "phieu.json"
        return TrangThaiPhieu(**json.loads(p.read_text(encoding="utf-8"))) if p.exists() else None

    def xoa_phieu(self) -> None:
        (self.goc / "phieu.json").unlink(missing_ok=True)

    def ghi_lan_chay(self, luc: datetime) -> None:
        with open(self.goc / "lan-chay.txt", "a", encoding="utf-8") as f:
            f.write(gio_utc(luc) + "\n")

    def con_cho_chay(self, bay_gio: datetime, ch: CauHinhChay) -> bool:
        """Trần cục bộ trước MỖI lần spawn (§8.3) — cửa sổ trượt 60 phút / 24 giờ như phía trạm (3a-1 G19)."""
        p = self.goc / "lan-chay.txt"
        moc = [doc_luc(x) for x in p.read_text().split()] if p.exists() else []
        return (sum(m > bay_gio - timedelta(hours=1) for m in moc) < ch.lan_chay_moi_gio
                and sum(m > bay_gio - timedelta(days=1) for m in moc) < ch.lan_chay_moi_ngay)

    def ngat_cau_dao(self, toi_luc: datetime, ly_do: str) -> None:
        ghi_nguyen_tu(self.goc / "cau-dao.json", json.dumps({"toi_luc": gio_utc(toi_luc), "ly_do": ly_do}))

    def cau_dao_ngat(self, bay_gio: datetime) -> bool:
        p = self.goc / "cau-dao.json"
        return p.exists() and doc_luc(json.loads(p.read_text())["toi_luc"]) > bay_gio

    def dem_loi_he(self, ket_thuc: str) -> int:
        """Chuỗi `loi_he` liên tiếp (§8.3) — lần chạy khác `loi_he` cắt chuỗi."""
        p = self.goc / "loi-he.txt"
        n = (int(p.read_text() or 0) if p.exists() else 0) + 1 if ket_thuc == "loi_he" else 0
        p.write_text(str(n))
        return n

    def luu_han_muc(self, hm: HanMuc) -> None:
        ghi_nguyen_tu(self.goc / "han-muc.json", hm.model_dump_json())

    def doc_han_muc(self) -> HanMuc | None:
        p = self.goc / "han-muc.json"
        return HanMuc.model_validate_json(p.read_text()) if p.exists() else None
