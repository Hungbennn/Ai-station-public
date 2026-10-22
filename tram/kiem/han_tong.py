"""Hạn TỔNG cho harness dài (lát 3C-B, dot6-C02) — thay `daemon thread + join(timeout)` (chỉ thôi chờ, không thu
hồi). Harness chạy trong TIẾN TRÌNH CON nhóm riêng (`vong_doi`); quá hạn → thu hồi cả cây qua `kill` gộp (quản lý +
principal); sau đó, kể cả khi harness tự xong, `don()` (gỡ lịch + tiến trình của principal qua `CongLich` — mã 3c)
phải trả đúng True. Cổng = file dấu `dau`, tạo O_EXCL TRƯỚC khi spawn, chỉ xoá khi cả thu hồi cây lẫn `don()` xác
nhận. Còn dấu → lượt sau bị từ chối không spawn (`cong_dong`), chờ Đại ca dọn và kiểm tay. Review A03/R2-02/R2-03
(hợp đồng `so_huu`): tạo dấu + spawn nằm trong `try` VÀ trong `ngat.hoan()` — ngắt tới lúc đó chỉ ném khi `Nhom` đã ở
`chu`; thu hồi trong `hoan()` (ngắt lần hai không cắt ngang, ném sau khi xong); `don()` luôn chạy sau thu hồi, vẫn ngắt
được → dấu GIỮ. `khoi` ném lỗi khác OSError (vd. `LoiThuHoi` — `Nhom` đã ở `chu` — hay `khoi` giả hỏng) → không xác
nhận: dấu giữ, cổng đóng."""
import math
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.kiem.gui_tin import gop_kill  # noqa: F401 — tên cũ; định nghĩa và phạm vi gửi ở `gui_tin` (A01)
from tram.kiem.ngat import hoan
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import Kill, LoiThuHoi, khoi_chay


class HetHanTong(LoiThuHoi):
    """Harness vượt hạn tổng — đã thu hồi + dọn; kết quả không được công nhận (cổng còn đóng nếu dọn chưa xác nhận)."""


def cong_dong(dau: Path) -> bool:
    return dau.exists()


def _don(don: Callable[[], bool]) -> bool:
    try:
        return don() is True
    except Exception:                       # noqa: BLE001 — lỗi dọn nào cũng là "không xác nhận", cổng giữ đóng
        return False


def chay_han_tong(argv: list[str], *, han: float, kill: Kill, dau: Path, don: Callable[[], bool],
                  khoi: Callable = khoi_chay, **kw) -> int:
    """Mã thoát của harness khi xong trong hạn VÀ dọn xác nhận; ngược lại ném (HetHanTong | LoiThuHoi). `don()` LUÔN
    chạy sau khi đã thử thu hồi — kể cả khi thu hồi không xác nhận — để gỡ lịch harness đã cài."""
    if not (math.isfinite(han) and han > 0):
        raise ValueError("hạn tổng phải hữu hạn, dương")
    dau.parent.mkdir(parents=True, exist_ok=True)
    chu, co_dau, ma, sach, xong = [], False, None, False, False
    try:
        with hoan():                            # tạo dấu + spawn: ngắt chỉ ném khi Nhom đã ở `chu` (finally thu hồi)
            try:
                os.close(os.open(dau, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
            except FileExistsError:
                raise LoiThuHoi(f"cổng đang đóng ({dau.name}): lượt trước chưa xác nhận dọn — không chạy") from None
            co_dau = True
            try:
                n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, chu=chu, **kw)
                chu[:] = chu or [n]             # `khoi` giả không tự ghi `chu`: nhận Nhom nó trả
            except OSError:
                if chu:
                    raise
                sach = True                     # Popen chưa tạo được tiến trình: không có gì để thu hồi
        ma = chu[0].cho(han) if chu else None
    finally:
        if co_dau:
            try:
                with hoan():                    # ngắt lần hai ném SAU khi thu hồi xong VÀ đã ghi kết quả
                    if chu:
                        sach = thu_hoi_con_lai(chu)
            finally:
                xong = _don(don) and sach
                if xong:
                    dau.unlink()
    if not chu:
        raise LoiThuHoi("không khởi chạy được harness")
    if ma is None:
        raise HetHanTong(f"harness quá hạn tổng {han:g} s — " + ("đã thu hồi và dọn" if xong else "CỔNG GIỮ ĐÓNG"))
    if not xong:
        raise LoiThuHoi("harness xong nhưng chưa xác nhận thu hồi/dọn — cổng giữ đóng")
    return ma
