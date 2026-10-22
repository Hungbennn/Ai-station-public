"""Gửi tín hiệu cho nhóm tiến trình (P1; V2-0 — review vòng 1 A01). Kiểm "nhóm còn là của cây" rồi mới gửi KHÔNG
nguyên tử (thành viên cuối chết, số được cấp lại giữa hai bước — kể cả giữa hai kênh của `gop_kill`), nên phạm vi phải
do CHÍNH lệnh gửi giới hạn:
- `kill_cuc_bo` gửi dưới user của chính tiến trình này (quản lý/trạm chạy nhiều việc khác) → chỉ hợp lệ cho nhóm gốc
  CHƯA GẶT (số không thể cấp lại) hoặc khi mọi tiến trình là của chính user (test).
- `kill_uid(kill)`: phần của `kill` chạy DƯỚI UID DÀNH RIÊNG — `kill_nhom` của principal cơ chế `user`: `Principal` của
  khe (D53: mỗi khe một tài khoản macOS, `tho.yaml` cấm trùng) hay `PrincipalKiem` (`tram-kiem`). Nhân macOS chỉ cho
  user thường gửi tới tiến trình có UID thực/UID lưu = UID của mình, nên số nhóm có bị cấp lại cho tài khoản khác thì
  lệnh gửi cũng không trúng; trúng tiến trình khác CÙNG UID thì đó vẫn là việc của khe/`tram-kiem`. Cơ chế `sandbox`
  (một user dùng chung nhiều khe) và kênh cục bộ KHÔNG phải kênh theo UID.
- `gop_kill(*ds)` → `GopKill`: gửi lần lượt từng kênh (cây harness có tiến trình của quản lý lẫn principal); `Nhom` chỉ
  dùng nó cho nhóm gốc chưa gặt, nhóm khác đi qua `kill_uid(GopKill)` = phần theo UID đầu tiên."""
import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass

Kill = Callable[[int, int], None]
LOI_GUI = (OSError, subprocess.SubprocessError)


def kill_cuc_bo(pgid: int, sig: int) -> None:
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError):
        pass


@dataclass(frozen=True)
class GopKill:
    ds: tuple[Kill, ...]

    def __call__(self, pgid: int, sig: int) -> None:
        for k in self.ds:
            try:
                k(pgid, sig)
            except LOI_GUI:
                pass


def gop_kill(*ds: Kill) -> GopKill:
    return GopKill(ds)


def kill_uid(kill: Kill) -> Kill | None:
    if isinstance(kill, GopKill):
        return next((k for k in map(kill_uid, kill.ds) if k is not None), None)
    chu, ham = getattr(kill, "__self__", None), getattr(kill, "__func__", None)
    return kill if getattr(ham, "__name__", None) == "kill_nhom" and getattr(chu, "co_che", None) == "user" else None
