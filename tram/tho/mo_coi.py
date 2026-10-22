"""CLI mồ côi và khoá worktree (spec 3 §7.2, H1; V2-0 bs-863.15, review vòng 1 A01/A02). `dang-chay.pid` = {pid, pgid,
giao_id, luot, lan} của lần chạy đang sống — ghi NGAY sau khi spawn, xoá khi lần chạy kết thúc VÀ khe đã dọn theo UID.
`tram tho chay` khởi động: dọn TOÀN UID của khe (`don` — `tho.don_uid`: kill -1 dưới chính principal rồi chứng minh
không còn tiến trình nào của UID đó) rồi mới xoá bản ghi; KHÔNG BAO GIỜ gửi tín hiệu theo số pid/pgid đọc từ file (số có
thể đã cấp lại — lỗi .15). Bản ghi chỉ còn để gửi `chay.xong {ket_thuc: "mo-coi"}` sau `chay.bat_dau` đã ghi bền (G35);
bản ghi cũ/hỏng không cản việc dọn. Dọn không chứng minh được → `LoiThuHoi`, GIỮ bản ghi, khe dừng.
Khoá `.tram/khoa` trong worktree (pid + giao_id): còn pid sống → không chạy lần mới (lớp bổ sung — agent ghi được
`.tram/`; hàng rào thật là kho phiếu của trạm + pid của tiến trình quản lý)."""
import json
import os
from collections.abc import Callable
from pathlib import Path

from tram.kiem.vong_doi import Kill, kill_cuc_bo  # noqa: F401 — tên cũ; một định nghĩa ở primitive P1


def con_song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True                                     # tiến trình của user khác (principal) vẫn đang sống
    return True


def ghi_pid(p: Path, *, pid: int, giao_id: str, luot: int, lan: int) -> None:
    p.write_text(json.dumps({"pid": pid, "pgid": pid, "giao_id": giao_id, "luot": luot, "lan": lan}))


def doc_pid(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def don_mo_coi(p: Path, *, don: Callable[[], None]) -> dict | None:
    """Bản ghi của lần chạy dở (dict có `giao_id`, `lan`; hỏng → None) SAU KHI `don()` đã chứng minh khe sạch; xoá file.
    `don` ném (`LoiThuHoi`) → file giữ nguyên, lỗi nổi lên."""
    x = doc_pid(p)
    don()
    p.unlink(missing_ok=True)
    return x if isinstance(x, dict) and isinstance(x.get("giao_id"), str) and isinstance(x.get("lan"), int) else None


def dat_khoa(wt: Path, *, pid: int, giao_id: str) -> bool:
    """False khi worktree đang bị khoá bởi pid còn sống của phiếu khác (H1)."""
    k = wt / ".tram" / "khoa"
    cu = (doc_pid(k) or {}).get("pid")
    if isinstance(cu, int) and cu > 0 and cu != pid and con_song(cu):
        return False
    k.parent.mkdir(parents=True, exist_ok=True)
    k.write_text(json.dumps({"pid": pid, "giao_id": giao_id}))
    return True


def go_khoa(wt: Path) -> None:
    (wt / ".tram" / "khoa").unlink(missing_ok=True)
