"""Cổng thao tác LỊCH (lát 3C-B, dot6-C02 — sau sự cố subagent chạy crontab dưới tài khoản người vận hành): mọi lệnh
của bước dọn/harness `tram-kiem` (kể cả cron/at/batch/launchctl) đi qua `CongLich`. Mở cổng = `xac_minh_uid` đạt (UID
thực, không tin env/argv). Cổng chỉ chuyển:
- lệnh nằm SAU đúng tiền tố `boc` đã xác minh (chạy dưới principal — gỡ lịch của chính nó là việc được phép);
- hoặc lệnh QUAN SÁT của tài khoản quản lý trong danh sách đóng `CHO_QUAN_LY` (đường dẫn tuyệt đối), `find` không có
  `-exec/-ok/-delete`. Không lọc theo chữ trong shell (`sh -c "…|crontab -"` lọt được bộ lọc chữ): mọi shell, mọi lệnh
  khác chạy dưới quyền quản lý bị từ chối TRƯỚC khi chạy.
Mặc định mọi lệnh chạy bằng `chay_gioi_han` (có hạn) với kill GỘP principal + cục bộ (lệnh quan sát chạy dưới quyền
quản lý). Chỉ test dựng `CongLich` trực tiếp; mã chạy thật phải mở bằng `mo_cong_lich`."""
import functools
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
from tram.kiem.han_tong import gop_kill
from tram.kiem.vong_doi import Kill, kill_cuc_bo

LICH = frozenset({"crontab", "at", "atq", "atrm", "batch", "launchctl"})
CHO_QUAN_LY = frozenset({"/usr/bin/find", "/usr/bin/pgrep", "/bin/ps", "/usr/bin/stat"})
CAM_FIND = frozenset({"-exec", "-execdir", "-ok", "-okdir", "-delete"})


def duoc_chay(argv: list[str], tien_to: tuple[str, ...]) -> bool:
    if len(argv) > len(tien_to) and tuple(argv[:len(tien_to)]) == tien_to:
        return True
    return bool(argv) and argv[0] in CHO_QUAN_LY and not CAM_FIND & set(argv)


@dataclass(frozen=True)
class CongLich:
    tien_to: tuple[str, ...]
    uid: int
    chay: Callable

    def __call__(self, argv: list[str], **kw):
        argv = [str(a) for a in argv]
        if not duoc_chay(argv, self.tien_to):
            raise LoiDanhTinh("lệnh không chạy dưới principal đã xác minh UID và không phải lệnh quan sát cho phép")
        return self.chay(argv, **kw)


def mo_cong_lich(ten: str, boc: Callable[[list[str]], list[str]], kill: Kill, *, chay: Callable | None = None,
                 xac_minh: Callable = xac_minh_uid) -> CongLich:
    tien_to = tuple(boc([]))
    if not tien_to or any(Path(a).name in LICH for a in tien_to):
        raise LoiDanhTinh("boc rỗng hoặc tự chứa lệnh lịch — lệnh sẽ không đổi principal")
    uid = xac_minh(ten, boc, kill)
    return CongLich(tien_to, uid, chay or functools.partial(chay_gioi_han, kill=gop_kill(kill, kill_cuc_bo)))
