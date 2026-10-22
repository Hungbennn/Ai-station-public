"""Chờ điều kiện tạm sau boot; chung một hạn cho đăng nhập và đăng ký API."""
import signal
import sys
import threading
import time

import yaml

from tram.tho.khach import KhachTram, LoiKhachTram
from tram.tho.ngu_canh import NguCanhTho

HAN_KHOI_DONG = 15 * 60.0
CHO_DAU = 10.0
CHO_TOI_DA = 60.0
NHAC_CAU_HINH = "Cấu hình thợ chưa sẵn sàng; giữ tắt, đối soát rồi khởi động lại."
NHAC_DANG_NHAP = "Chưa xác nhận đăng nhập nền của hai khe; đăng nhập rồi khởi động lại thợ."


class ChoKhoiDong:
    def __init__(self, tat):
        self.tat = tat
        self.han = time.monotonic() + HAN_KHOI_DONG
        self.cho = CHO_DAU
        self.lan = 0

    def thu_lai(self, ly_do, *, co_han=True):
        """`co_han=False`: chờ tram-api không giới hạn (nó chỉ lên sau khi Đại ca đăng nhập GUI)."""
        con = self.han - time.monotonic() if co_han else CHO_TOI_DA
        if self.tat.is_set() or con <= 0:
            return False
        self.lan += 1
        if self.lan <= 5 or self.lan % 30 == 0:      # chờ lâu thì log thưa: ~30 phút một dòng
            print(f"Chờ {ly_do}; thử lại lần {self.lan}.", flush=True)
        dung = self.tat.wait(min(self.cho, con))
        self.cho = min(self.cho * 2, CHO_TOI_DA)
        return not dung and not self.tat.is_set() and (not co_han or time.monotonic() < self.han)


def dang_ky(nc, tat, cho=None):
    """Chỉ thử lại lỗi kết nối trước khi mở luồng khe; HTTP lỗi giữ mã thoát cũ."""
    ch = nc.ch
    than = {"may_id": ch.may_id, "khe": [
        {"ten": k.ten, "cli": k.cli, "ten_goi_nho": k.ten_goi_nho, "vai_uu_tien": list(k.vai_uu_tien),
         **({"models": list(k.models)} if k.models else {})} for k in ch.khe]}
    while not tat.is_set():
        try:
            ma, _ = nc.khach.goi("POST", "/api/tho/dang-ky", than)
        except LoiKhachTram:
            if cho is None:
                raise
            if cho.thu_lai("tram-api chưa gọi được", co_han=False):
                continue
            if not tat.is_set():
                print("Tram-api chưa sẵn sàng; giữ tắt, đối soát rồi khởi động lại thợ.", file=sys.stderr)
            return False, 0
        if ma != 200:
            print(f"Đăng ký khe thất bại: HTTP {ma}", file=sys.stderr)
            return False, 2
        return not tat.is_set(), 0
    return False, 0


def khoi_dong(chay_may, doc_token_may):
    from tram.tho.cau_hinh import nap_cau_hinh_tho
    from tram.tho.san_sang_b import san_sang_b
    try:
        ch = nap_cau_hinh_tho()
    except (ValueError, OSError, yaml.YAMLError):
        print(NHAC_CAU_HINH)
        return 0
    token = doc_token_may(tren_may_b=ch.tren_may_b)
    if not token:
        print("Chưa có token máy hợp lệ; đối soát kho token rồi khởi động lại thợ.", file=sys.stderr)
        return 0
    tat = threading.Event()
    for s in (signal.SIGTERM, signal.SIGINT):
        signal.signal(s, lambda *_: tat.set())
    cho = ChoKhoiDong(tat)
    try:
        while not tat.is_set() and not san_sang_b(ch):
            if not cho.thu_lai("đăng nhập nền hai khe chưa sẵn sàng"):
                if not tat.is_set():
                    print(NHAC_DANG_NHAP)
                return 0
    except (ValueError, OSError, yaml.YAMLError):
        print(NHAC_CAU_HINH)
        return 0
    return 0 if tat.is_set() else chay_may(NguCanhTho(ch, KhachTram(ch.tram_api, token)), tat, cho=cho)
