"""Đọc hạn mức lúc khe RẢNH cho vòng nhịp tim (spec 3 §8.1; bs-78r.10 = dot6-Q02). Chạy SAU khi nhịp đã gửi: lỗi hay
quá hạn của quota không làm trễ/chết nhịp tim. Principal lấy từ ngữ cảnh của CHÍNH khe (`nc.principal(k, None, …)` —
hồ sơ sandbox với `wt=None` không mở thêm thư mục khe khác); thiếu/sai principal → không spawn gì. Nhịp đầu chỉ xác
minh UID THỰC của principal (3C-B `xac_minh_uid` — `user:<quản lý>` cấu hình nhầm bị chặn; sai → thôi đọc hạn mức của
khe), nhịp sau mới hỏi app-server: mỗi nhịp tốn tối đa một việc, cận trên XẤU NHẤT 48 s (`app_server`) → nhịp kế tiếp
trễ tối đa ~78 s, vẫn < `mat_ket_noi_giay` 90 s. Không xác nhận thu hồi (`LoiThuHoi`, kể cả cây dò UID) → `doc` trả
True: vòng khe DỪNG (như CLI không thu hồi được — P1). Thông báo cố định: không in exception, argv hay env (token)."""
import time

from tram.chay_cli.bo_cli import BO_CLI
from tram.kiem import danh_tinh
from tram.kiem.vong_doi import LoiThuHoi


class DocHanMucRanh:
    def __init__(self, nc, k, khe_id: str, so):
        self.nc, self.k, self.khe_id, self.so = nc, k, khe_id, so
        self.lan_sau = 0.0
        self.khoa = self.da_xac_minh = False

    def _doc(self):
        pr = self.nc.principal(self.k, None, "han-muc")
        if not self.da_xac_minh:
            danh_tinh.xac_minh_uid(pr.user, pr.boc, pr.kill_nhom)
            self.da_xac_minh, self.lan_sau = True, 0.0           # hỏi app-server ở nhịp kế tiếp
            return
        hm = BO_CLI[self.k.cli].doc_han_muc_ranh(self.khe_id, self.k.thu_muc_cau_hinh, bay_gio=self.nc.dong_ho(),
                                                 principal=pr, path=self.nc.ch.chay.path_cli)
        if hm is not None:
            self.so.luu_han_muc(hm)

    def doc(self, ranh: bool) -> bool:
        """True = không xác nhận thu hồi tiến trình đọc hạn mức: người gọi dừng khe."""
        chu_ky = BO_CLI[self.k.cli].chu_ky_han_muc_ranh_giay
        if self.khoa or not ranh or chu_ky is None or time.monotonic() < self.lan_sau:
            return False
        self.lan_sau = time.monotonic() + chu_ky
        try:
            self._doc()
        except LoiThuHoi:
            self.khoa = True
            print(f"{self.khe_id}: không xác nhận thu hồi tiến trình đọc hạn mức — dừng khe để kiểm principal")
            return True
        except danh_tinh.LoiDanhTinh:
            self.khoa = True
            print(f"{self.khe_id}: chưa chứng minh được UID của principal — không đọc hạn mức dưới principal này")
        except Exception:                   # noqa: BLE001 — quota hỏng không được làm chết luồng nhịp tim
            print(f"{self.khe_id}: không đọc được hạn mức khe rảnh; nhịp tim tiếp tục")
        return False
