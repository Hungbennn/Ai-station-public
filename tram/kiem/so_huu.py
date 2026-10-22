"""HỢP ĐỒNG SỞ HỮU tiến trình con (V2-0 — review vòng 1 A03, vòng 2 R2-01/R2-02; plan B dựa vào, thay "H-A03"):

1. `vong_doi.khoi_chay(argv, *, kill, chu, …)` là nơi DUY NHẤT spawn; `chu` (list) BẮT BUỘC. Popen + dựng `Nhom` +
   `chu.append` nằm trong `ngat.hoan()`. Ném `OSError` ⇒ `chu` không đổi: Popen chưa tạo được tiến trình (lỗi exec thì
   Popen tự gặt con). MỌI lối ra khác sau khi Popen trả — trả `Nhom`, `LoiThuHoi` vì không theo dõi được gốc, ngắt
   được phát lại khi ra khỏi `hoan()` — đều xảy ra khi `Nhom` ĐÃ ở `chu`.
2. Người gọi: MỘT khối sở hữu bao lời gọi `khoi_chay` và mọi bước sau — `with so_huu(...) as chu:`, hoặc `chu = []` +
   `try/finally` với `thu_hoi_con_lai(chu)` (bộ chạy một chủ: `chay_gioi_han`, `chay_han_tong`). Mỗi `Nhom` chưa thu
   hồi lần nào được thu hồi trong `hoan()` (ngắt lần hai ném SAU khi xong).
3. `LoiThuHoi` KHÔNG có nghĩa "không còn con": con/hậu duệ có thể còn sống (kill bị từ chối, treo sau SIGKILL, hậu duệ
   tách phiên, không theo dõi được gốc). Nó nghĩa là KHÔNG XÁC NHẬN: `Nhom` vẫn trong `chu` (gốc chưa gặt giữ số nhóm),
   kết quả không công nhận, cổng/khe giữ đóng; tầng trên dọn theo UID dành riêng (khe: `tho.don_uid`; `tram-kiem`:
   `cong_that.thu_hoi_theo_uid`). Lệnh dưới chính tài khoản quản lý không có lưới UID: chỉ cổng đóng + Đại ca kiểm.
4. Chỉ `Nhom.thu_hoi` đã xác nhận mới gặt gốc; nhánh lỗi không bao giờ gặt (`giu_xac`, R2-01)."""
from contextlib import contextmanager

from tram.kiem.ngat import hoan
from tram.kiem.vong_doi import LoiThuHoi


def thu_hoi_con_lai(chu: list, **kw) -> bool:
    """Thu hồi mọi `Nhom` trong `chu` CHƯA thu hồi lần nào (`ket_thu_hoi` None), trong `hoan()`. True khi mọi `Nhom`
    vừa thu hồi đều xác nhận (không còn gì → True); người gọi đã tự thu hồi, tự xử lý kết quả thì không thu hồi lại."""
    with hoan():
        return all([n.thu_hoi(**kw) for n in chu if getattr(n, "ket_thu_hoi", None) is None])


@contextmanager
def so_huu(loi: str, **kw):
    """`with so_huu("…") as chu:` — ra khỏi khối (xong, lỗi, ngắt) thì `thu_hoi_con_lai(chu, **kw)`. Chưa xác nhận →
    `LoiThuHoi(loi)` THAY lỗi thường (`from None` — không nối chuỗi có thể mang byte đầu ra); ngắt vẫn là ngắt."""
    chu: list = []
    try:
        yield chu
    except KeyboardInterrupt:
        thu_hoi_con_lai(chu, **kw)
        raise
    except BaseException:
        if not thu_hoi_con_lai(chu, **kw):
            raise LoiThuHoi(loi) from None
        raise
    if not thu_hoi_con_lai(chu, **kw):
        raise LoiThuHoi(loi)
