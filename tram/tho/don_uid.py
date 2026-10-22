"""Dọn theo PHẠM VI UID của khe (V2-0; review vòng 1 A01/A02, bs-863.15) — lưới cuối cho MỌI tiến trình dưới principal
của khe, kể cả tiến trình đã lẩn khỏi tầm chụp của `Nhom` (fork + setsid + cha thoát giữa hai ảnh) và CLI mồ côi của lần
chạy trước. D53: chỉ cơ chế `user` — mỗi khe MỘT tài khoản macOS riêng (`tho.yaml` cấm trùng). Các bước: chứng minh UID
thực của principal (`xac_minh_uid`; không root, không người vận hành) → `kill -KILL -1` CHẠY DƯỚI chính UID đó (nhân chỉ
gửi tới tiến trình cùng UID: không thể trúng tài khoản khác dù số PID/nhóm đã cấp lại) → chụp bảng tiến trình của nhân
tới khi KHÔNG còn tàn dư UID (máy B lọc Apple theo D162). Mã thoát của `kill` không là bằng chứng. Bước nào không
chứng minh được → `LoiThuHoi`: khe dừng, không nhận lượt/phiếu mới. Cơ chế `sandbox` (một user dùng chung nhiều khe)
chưa có cách dọn theo phạm vi → `LoiThuHoi` ngay (D53: cổng sandbox đóng).
Chỉ gọi khi khe KHÔNG có việc nào khác đang chạy dưới principal: khởi động khe, đầu mỗi phiếu, sau mỗi lần chạy CLI
(đọc hạn mức lúc rảnh chỉ chạy khi khe không giữ phiếu — `vong_khe.nhip`). `tram tho kiem` chạy song song sẽ bị cắt
(kết quả "không kết luận") — sổ tay: dừng `tram tho chay` trước khi kiểm."""
import os
import subprocess
import time
from collections.abc import Callable

from tram.kiem import danh_tinh
from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi
from tram.kiem.ngoai_le_uid import con_uid

GIET = ["/bin/kill", "-KILL", "-1"]
HAN_HET = 5.0


def con_lai(uid: int, chup: Callable = chup_nhan, *, ten: str | None = None) -> int:
    """Số tàn dư UID sau lọc D162; thiếu tên không miễn. Lỗi đọc → OSError."""
    return len(con_uid(uid, chup, ten=ten))


def don_uid(pr, *, xac_minh: Callable = danh_tinh.xac_minh_uid, chay: Callable = chay_gioi_han,
            chup: Callable = chup_nhan, han: float = HAN_HET, ngu: Callable = time.sleep,
            tren_may_b: bool = False) -> None:
    if getattr(pr, "co_che", None) != "user":
        raise LoiThuHoi("principal không phải tài khoản riêng của khe (D53) — không dọn được theo UID, khe dừng")
    try:
        uid = xac_minh(pr.user, pr.boc, pr.kill_nhom)
    except danh_tinh.LoiDanhTinh:
        raise LoiThuHoi("UID thực của principal chưa chứng minh — không dọn theo UID, khe dừng") from None
    if uid in (0, os.getuid(), os.geteuid()):                     # phòng thủ thêm: kill -1 không bao giờ ngoài khe
        raise LoiThuHoi("UID principal trùng root/tài khoản đang chạy — không dọn, khe dừng")
    try:
        chay(pr.boc(GIET), kill=pr.kill_nhom, capture_output=True, timeout=10, env={"PATH": "/usr/bin:/bin"})
    except (OSError, subprocess.SubprocessError):
        raise LoiThuHoi("kill -1 dưới principal không chạy được — khe dừng") from None
    het = time.monotonic() + han
    while True:
        try:
            n = con_lai(uid, chup, ten=pr.user if tren_may_b else None)
        except (OSError, ValueError):
            raise LoiThuHoi("không đọc được bảng tiến trình sau kill -1 — khe dừng") from None
        if n == 0:
            return
        if time.monotonic() >= het:
            raise LoiThuHoi(f"còn {n} tiến trình của UID khe sau kill -1 (setuid hay kẹt trong nhân) — khe dừng")
        ngu(0.2)
