"""Hoãn ngắt ở RANH GIỚI SỞ HỮU (V2-0 — review A03, R2-02): MỘT cơ chế cho mọi chỗ spawn/thu hồi (`vong_doi`,
`so_huu`, bộ chạy) và cho CLI cha (plan B thêm `term_thanh_ngat` vào file này). Trong khối `hoan()` ngoài cùng, SIGINT/
SIGTERM tới LUỒNG CHÍNH chỉ được GHI; ra khỏi khối: khôi phục MỌI handler cũ — kể cả khi một tín hiệu tới ngay giữa lúc
khôi phục — rồi PHÁT LẠI theo thứ tự nhận (`raise_signal`, handler cũ chạy đồng bộ: KeyboardInterrupt, handler của
người gọi, hay mặc định). Tín hiệu đầu ném thì các tín hiệu sau không phát lại; ngắt đang chờ thắng lỗi của thân khối.
Khối lồng nhau dùng chung một lần ghi. Không hoãn ngoài luồng chính (handler Python chỉ chạy ở luồng chính) và với tín
hiệu có handler đặt từ C (`getsignal` None). Không hứa gì với SIGKILL.
Plan B (bs-863.19, B03): `term_thanh_ngat` — CHỈ CLI cha cài, ở luồng chính — biến SIGTERM thành `NgatTerm` (một
`KeyboardInterrupt`), SIGINT thành `KeyboardInterrupt`; trong `hoan()` chúng được ghi rồi phát lại QUA chính handler này
khi rời khối (sau khi `Nhom` đã ở `chu` / sau khi thu hồi xong), ra khỏi thì khôi phục handler cũ của CẢ HAI."""
import signal
import threading
from contextlib import contextmanager

TIN_HIEU = (signal.SIGINT, signal.SIGTERM)
_dat = signal.signal                        # test thay để mô phỏng tín hiệu tới đúng lúc khôi phục handler
_muc, _cu, _nhan = 0, {}, []


def _ghi(so, khung):
    _nhan.append(so)


def _khoi_phuc() -> None:
    loi = None
    for s, h in list(_cu.items()):
        try:
            _dat(s, h)
        except BaseException as e:          # noqa: BLE001 — tín hiệu tới ngay khi handler cũ vừa về: khôi phục nốt
            loi = loi or e
    _cu.clear()
    nhan, _nhan[:] = list(_nhan), []
    if loi is not None:
        raise loi
    for s in nhan:
        signal.raise_signal(s)


@contextmanager
def hoan():
    global _muc
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    if _muc == 0:
        _nhan.clear()
        _cu.update({s: h for s in TIN_HIEU if (h := signal.getsignal(s)) is not None})
    _muc += 1
    try:
        if _muc == 1:                       # cài bộ ghi TRONG try: tín hiệu tới giữa lúc cài vẫn được khôi phục
            for s in _cu:
                _dat(s, _ghi)
        yield
    finally:
        _muc -= 1
        if _muc == 0:
            _khoi_phuc()


class NgatTerm(KeyboardInterrupt):
    """CLI cha nhận SIGTERM — đi đường dọn như Ctrl-C."""


def _thanh_ngat(so, khung):
    raise NgatTerm("SIGTERM") if so == signal.SIGTERM else KeyboardInterrupt()


@contextmanager
def term_thanh_ngat(dat=signal.signal):
    cu = [(so, signal.getsignal(so)) for so in (signal.SIGTERM, signal.SIGINT)]
    try:
        for so, _ in cu:
            dat(so, _thanh_ngat)
        yield
    finally:
        loi = None
        for so, h in reversed(cu):
            try:
                dat(so, h)
            except BaseException as e:          # ngắt ngay sau khi trả handler: khôi phục nốt
                loi = loi or e
        if loi is not None:
            raise loi
