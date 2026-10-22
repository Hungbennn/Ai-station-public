"""Hạn TỔNG cho một lời gọi Anthropic (bs-2bd.1.1) — chấm cột (`claude._goi`) và memory (`nho.llm._goi`).

`timeout` của SDK chỉ là hạn từng lần chờ mạng (kết nối, ghi, MỖI lần đọc), không phải hạn cả lời gọi: máy chủ trả
nhỏ giọt, phân giải DNS treo, hay SDK ngủ chờ thử lại theo `retry-after` (SDK 1.13 không đặt trần) đều vượt được. Nên:
- SDK không tự thử lại (`max_retries=0` ở `claude.tao_client`): không có giấc ngủ nào trong SDK. Lỗi tạm thời
  (429/5xx/mạng) → `anthropic.APIError` như cũ; lượt quét/nạp sau thử lại.
- Người gọi chờ lời gọi chạy trong một luồng phụ tối đa `HAN_GOI_GIAY` TÍNH TỪ LÚC GỌI (gồm cả lúc chờ chỗ; hàm `cho`
  thay được trong test — đồng hồ điều khiển). Quá hạn → `QuaHanGoi` (một `anthropic.APITimeoutError`: mọi nơi gọi đã
  xử lý `anthropic.APIError`).
- TRẦN CƯỠNG CHẾ: tối đa `TOI_DA_LUONG` lời gọi còn sống cùng lúc trong một tiến trình — đang chạy hay đã bị bỏ. Chỗ
  được ĐẶT TRƯỚC dưới khoá rồi mới mở luồng; chính luồng trả chỗ khi lời gọi thật kết thúc (không phụ thuộc người gọi
  còn chờ hay đã bị ngắt). Hết chỗ → người gọi chờ chỗ trong hạn của mình; hết hạn → `QuaHanGoi`, không mở luồng,
  không gọi mạng. Python không huỷ được luồng: luồng quá hạn bị BỎ (kết quả muộn bị vứt), vẫn giữ chỗ tới khi một lần
  chờ mạng vượt `timeout` của SDK. Luồng là daemon: tiến trình thoát không chờ nó."""
import threading
import time
from collections.abc import Callable
from typing import TypeVar

import anthropic

HAN_GOI_GIAY = 120.0          # hạn tổng một lời gọi; cũng là `timeout` từng lần chờ mạng của SDK
TOI_DA_LUONG = 2              # lời gọi Anthropic còn sống cùng lúc trong một tiến trình (đang chạy + đã bị bỏ)
T = TypeVar("T")
_song: set[threading.Thread] = set()
_dk = threading.Condition()


class QuaHanGoi(anthropic.APITimeoutError):
    def __init__(self, thong_bao: str) -> None:
        anthropic.APIConnectionError.__init__(self, message=thong_bao, request=None)  # type: ignore[arg-type]


def _dat_cho(t: threading.Thread, het: float) -> None:
    """Dưới khoá: chờ chỗ trống tới `het`, ghi `t` vào `_song` rồi mới chạy nó — không bao giờ quá trần."""
    with _dk:
        while len(_song) >= TOI_DA_LUONG:
            con = het - time.monotonic()
            if con <= 0:
                raise QuaHanGoi(f"đã có {len(_song)} lời gọi Anthropic chưa dứt — không gọi thêm")
            _dk.wait(con)
        if time.monotonic() >= het:
            raise QuaHanGoi("đã hết hạn chờ Anthropic — không mở lời gọi mới")
        _song.add(t)
        try:
            t.start()
        except RuntimeError:
            if t.ident is None:                  # Thread.start từ chối tạo luồng; không phải ngắt bất đồng bộ
                _song.discard(t)
                _dk.notify_all()
            raise
        # KeyboardInterrupt/SystemExit: ident None KHÔNG chứng minh luồng OS chưa được tạo.
        # Giữ chỗ; luồng tự trả khi kết thúc. Nếu ngắt trước tạo thật, giữ chỗ tới khi khởi động lại dịch vụ.


def goi_trong_han(ham: Callable[[], T], *, cho: Callable[[threading.Thread, float], None] = threading.Thread.join) -> T:
    """Chạy `ham()` trong luồng phụ, chờ tối đa `HAN_GOI_GIAY`. Trả kết quả hoặc ném lại đúng lỗi của `ham`."""
    han = HAN_GOI_GIAY
    het, kq = time.monotonic() + han, {}

    def chay() -> None:
        try:
            kq["gia_tri"] = ham()
        except BaseException as e:          # noqa: BLE001 — chuyển nguyên lỗi về người gọi
            kq["loi"] = e
        finally:
            with _dk:
                _song.discard(threading.current_thread())
                _dk.notify_all()
    t = threading.Thread(target=chay, name="goi-anthropic", daemon=True)
    _dat_cho(t, het)
    cho(t, max(0.0, het - time.monotonic()))
    if t.is_alive():
        raise QuaHanGoi(f"lời gọi Anthropic quá {han:.0f} giây — bỏ chờ")
    if "loi" in kq:
        raise kq["loi"]
    return kq["gia_tri"]
