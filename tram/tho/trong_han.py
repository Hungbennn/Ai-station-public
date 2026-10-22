"""Chạy MỘT việc không hủy được giữa chừng (I/O mạng, đẩy mốc) trong luồng riêng với hạn TUYỆT ĐỐI `het` (V2-6c, review
vòng 1 A06): xong trong hạn → trả (lỗi của việc ném lại ở luồng gọi); quá hạn → đặt `ngung` (việc tự thôi ở ranh giới
an toàn kế tiếp) rồi ném `LoiThuHoi` — người gọi không bao giờ bị giữ quá hạn. Luồng vào `luong` để người gọi
chờ/kiểm."""
import threading
import time
from collections.abc import Callable

from tram.kiem.vong_doi import LoiThuHoi


def chay_trong_han(ham: Callable[[], None], het: float, *, ngung: threading.Event, ten: str, luong: list) -> None:
    loi: list[BaseException] = []

    def chay() -> None:
        try:
            ham()
        except BaseException as e:                      # noqa: BLE001 — chuyển về luồng gọi
            loi.append(e)
    t = threading.Thread(target=chay, daemon=True, name=ten)
    luong.append(t)
    t.start()
    t.join(max(0.0, het - time.monotonic()))
    if t.is_alive():
        ngung.set()
        raise LoiThuHoi(f"{ten}: chưa xong trong hạn — dừng khe, giữ phiếu")
    if loi:
        raise loi[0]
