"""Gốc của một `Nhom` (V2-0, dot7-C01): biết gốc đã THOÁT mà KHÔNG GẶT. Popen thật → kqueue `EVFILT_PROC` +
`NOTE_EXIT|NOTE_EXITSTATUS` trên con của CHÍNH tiến trình này (đo trên macOS 15.6.1: sự kiện mang mã chờ, tiến trình
còn là xác tới khi `waitpid`). Còn xác thì số pid — cũng là số NHÓM và PHIÊN của gốc, vì gốc luôn `start_new_session`
— không thể được cấp lại: mọi tiến trình mang nhóm đó là hậu duệ của gốc, tín hiệu gửi nhóm gốc không trúng ai khác.
Chỉ gặt ở `gat()`, sau khi thu hồi đã xác nhận. Đăng ký trên xác (gốc thoát trước khi kịp đăng ký) trả ESRCH → gặt
ngay để lấy mã, TRƯỚC mọi lần gửi; nhóm gốc khi đó mất bảo vệ, ai còn mang số đó thành "mơ hồ" (không gửi, không xác
nhận). Review vòng 2 R2-01: lỗi khác ESRCH (hay không tạo được kqueue) → KHÔNG gặt — gốc vẫn là con chưa gặt nên số
nhóm vẫn được giữ (gửi nhóm gốc vẫn an toàn); `hong` = không bao giờ xác nhận gốc đã thoát → `thu_hoi` không bao giờ
True, người gọi giữ `Nhom` trong danh sách sở hữu, cổng đóng. Popen GIẢ của test (không phải `subprocess.Popen`) → chờ
bằng `wait`/`poll` của chính nó."""
import errno
import os
import select
import subprocess
import time

EV_RECEIPT = 0x0040                                 # <sys/event.h>; Python không xuất hằng này
NOTE_EXITSTATUS = 0x04000000
_kqueue = select.kqueue                             # test thay để tiêm lỗi đăng ký


class Goc:
    def __init__(self, p):
        self.p, self._kq, self._ma, self.hong = p, None, None, False
        if not isinstance(p, subprocess.Popen) or p.returncode is not None:
            return
        try:
            self._kq = _kqueue()
            (r,) = self._kq.control([select.kevent(p.pid, select.KQ_FILTER_PROC, select.KQ_EV_ADD | EV_RECEIPT,
                                                   select.KQ_NOTE_EXIT | NOTE_EXITSTATUS)], 1, 0)
            loi = r.data if r.flags & select.KQ_EV_ERROR else 0
        except Exception:                           # noqa: BLE001 — không theo dõi được gốc: như đăng ký lỗi
            loi = -1
        if loi == errno.ESRCH:
            self.gat()
        elif loi:
            self._dong()
            self.hong = True

    @property
    def pid(self) -> int:
        return self.p.pid

    def chua_gat(self) -> bool:
        """Số pid/nhóm gốc còn được giữ (gốc còn sống hoặc còn là xác)."""
        return self.p.returncode is None

    def thoat(self, giay: float = 0.0) -> bool:
        """True khi gốc đã thoát (còn xác hoặc đã gặt). Chờ tối đa `giay`; KHÔNG gặt. `hong` → luôn False."""
        if self.p.returncode is not None or self._ma is not None:
            return True
        if self.hong:
            time.sleep(max(0.0, giay))
            return False
        if self._kq is None:
            try:
                self.p.wait(timeout=max(0.0, giay))
                return True
            except subprocess.TimeoutExpired:
                return False
        try:
            su_kien = self._kq.control(None, 1, max(0.0, giay))
        except OSError:
            self.hong = True
            self._dong()
            return False
        for e in su_kien:
            if e.fflags & select.KQ_NOTE_EXIT:
                self._ma = os.waitstatus_to_exitcode(e.data)
        return self._ma is not None

    def ma(self) -> int | None:
        return self.p.returncode if self.p.returncode is not None else self._ma

    def _dong(self) -> None:
        if self._kq is not None:
            kq, self._kq = self._kq, None
            try:
                kq.close()
            except OSError:
                pass                            # lỗi đóng không được cắt ngang bàn giao/thu hồi tiến trình

    def gat(self) -> None:
        self._dong()
        self.p.poll()
