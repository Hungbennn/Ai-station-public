"""Sở hữu và thu hồi con trực tiếp do test tạo; không dùng cho lifecycle sản phẩm."""
from contextlib import contextmanager


def don_cac_con(ds):
    loi = False
    for p in ds:
        try:
            if p.pid is None:
                continue
            if p.is_alive():
                p.terminate()
            p.join(2)
            if p.is_alive():
                p.kill()
                p.join(2)
            if p.is_alive():
                loi = True
        except Exception:
            loi = True
    if loi:
        raise RuntimeError("Không dọn được tiến trình test do fixture sở hữu") from None


def dong_hang(hang):
    loi = False
    for dong in (hang.cancel_join_thread, hang.close):
        try:
            dong()
        except Exception:
            loi = True
    if loi:
        raise RuntimeError("Không đóng được queue test") from None


@contextmanager
def quan_ly_con(ds, hang):
    try:
        yield
    finally:
        try:
            don_cac_con(ds)
        finally:
            dong_hang(hang)
