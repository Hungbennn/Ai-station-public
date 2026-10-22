"""Ngữ cảnh của `tram tho chay` (spec 3 §5, §7): phụ thuộc gom một chỗ để test thay bằng bản giả (CLI giả, principal
chạy cùng user, đồng hồ, chu kỳ ngắn). `request_id` của thợ TẤT ĐỊNH theo (giao_id, luot, việc, …) — gửi lại sau
restart vẫn cùng id (§6.6); thân đã ghi bền trong hộp thư trước khi gửi."""
import hashlib
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from tram.chay_cli.bo_cli import BO_CLI
from tram.duong_dan import tram_home
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.don_uid import don_uid
from tram.tho.khach import KhachTram
from tram.tho.principal import ChuaCoPrincipal
from tram.tho.principal_khe import principal_cua


def rid(giao_id: str, luot: int, *phan: object) -> str:
    return "r-" + hashlib.sha256(":".join(map(str, (giao_id, luot, *phan))).encode()).hexdigest()[:32]


@dataclass
class NguCanhTho:
    ch: CauHinhTho
    khach: KhachTram
    goc: Path = field(default_factory=tram_home)                                  # ~/.tram của tài khoản quản lý
    goc_kho: Path = field(default_factory=lambda: Path.home() / "tram" / "kho")
    goc_wt: Path = field(default_factory=lambda: Path.home() / "tram" / "worktrees")
    principal_cua: Callable | None = None      # (khe, wt, tên hồ sơ) -> Principal; None → principal_khe.principal_cua
    tao_cli: Callable | None = None             # (boc, *, khe_id, kill, khi_bat_dau, khi_han_muc, tran_token_ra)
    nguon: object | None = None                # NguonHanMuc; None → NguonHanMucClaude(thang=chay.thang_utilization)
    dong_ho: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    chay_lenh: Callable = subprocess.run       # lệnh hệ thống của tiến trình quản lý (chmod +a)
    chu_ky_nhip: float = 30.0                  # §6.2
    cho_doc: float = 1.0                       # đọc hàng đợi `tram bao`
    cho_xong: float = 60.0                     # §7.4: chờ CLI thoát sau `xong`
    cho_thu_lai: float = 5.0                   # gửi lại da-push tạm
    don_uid: Callable | None = None             # (principal) -> None | ném LoiThuHoi; None → tho.don_uid.don_uid (A02)

    def principal(self, k: KheCauHinh, wt: Path | None, ten: str):
        if self.principal_cua is not None:
            return self.principal_cua(k, wt, ten)
        return principal_cua(self.ch, k, goc=self.goc, goc_wt=self.goc_wt, wt=wt, ten=ten)

    def don_khe(self, k: KheCauHinh) -> None:
        """Dọn theo UID của khe (A02); không chứng minh được khe sạch → `LoiThuHoi` (khe dừng, không nhận việc)."""
        try:
            pr = self.principal(k, None, "don-uid")
        except ChuaCoPrincipal:
            raise LoiThuHoi("khe chưa có principal hợp lệ — không chứng minh được khe sạch") from None
        if self.don_uid is not None:
            self.don_uid(pr)
        else:
            don_uid(pr, tren_may_b=self.ch.tren_may_b)

    def nguon_han_muc(self, cli="claude"):
        return self.nguon or BO_CLI[cli].tao_nguon(thang=self.ch.chay.thang_utilization)
