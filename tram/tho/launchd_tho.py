"""LaunchAgent của tiến trình quản lý thợ trên Mac thợ từ xa (spec 3 §9.2; kiến trúc §7): `vn.tram.tho` chạy
`tram tho chay` (vòng của 3a-2) dưới tài khoản quản lý thợ. Mac thợ cài trạm bằng `uv tool install` nên chạy thẳng
file `tram` (đường dẫn tuyệt đối), không `uv run --project`. Chỉ SINH plist/lệnh — nạp thật sau `dong-y`."""
import plistlib
from pathlib import Path

from tram.chu.launchd import PATH_HE_THONG

NHAN_THO = "vn.tram.tho"


def tao_plist_tho(*, tram: str, log: Path, home: Path) -> bytes:
    if not Path(tram).is_absolute():
        raise ValueError("cần đường dẫn tuyệt đối tới `tram` (vd ~/.local/bin/tram của uv tool)")
    return plistlib.dumps({
        "Label": NHAN_THO,
        "ProgramArguments": [tram, "tho", "chay"],
        "WorkingDirectory": str(home),
        "StandardOutPath": str(log),
        "StandardErrorPath": str(log),
        "EnvironmentVariables": {"PATH": f"{home / '.local/bin'}:{PATH_HE_THONG}"},
        "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False},
    })


def lenh_nap_launchd(plist: Path, *, uid: int) -> list[list[str]]:
    """`bootout` được phép lỗi (chưa nạp lần nào); `bootstrap` phải thành công."""
    mien = f"gui/{uid}"
    return [["launchctl", "bootout", f"{mien}/{NHAN_THO}"], ["launchctl", "bootstrap", mien, str(plist)]]
