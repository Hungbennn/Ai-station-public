"""Cửa kiểm TƯƠI sát mỗi lệnh ghi (Q11, V2-Q3; D107, D134). `kiem` đọc nút, estop, khoá ghi rồi ngân sách.
`truoc_ghi` gọi `kiem` và tiêu suất trước khi gửi lệnh. Một dự án đã bắt đầu đọc trước hạn được dự phòng MỘT
lệnh ghi dù đọc chậm hết giờ; không miễn bất kỳ cửa an toàn nào. Sau lệnh đầu, hết giờ thì GIỮ để nhịp sau đối soát
và tiếp tục (kể cả giữa create và dep add). Nút tắt → BỎ; estop / khoá ghi / hết giờ → GIỮ."""
from collections.abc import Callable
from dataclasses import dataclass, field

from tram.chu import estop
from tram.de_nghi.cai_dat import bat_ghi_an_toan, doc_cai_dat

GIU = ("estop", "khoa-ghi", "het-gio")


class DungGhi(Exception):
    def __init__(self, ly_do: str):
        super().__init__(ly_do)
        self.ly_do = ly_do


@dataclass
class Cua:
    kho: object
    du_an: str
    bat_ghi: Callable[[str], bool]
    dong_ho: Callable[[], float]
    het: float                                  # mốc `dong_ho()` hết ngân sách của nhịp này
    so_ghi: int = field(default=0, init=False)     # suất ghi đầu không bị lần đọc chậm ăn mất

    def kiem(self, loai: str) -> None:
        if not doc_cai_dat(self.kho.db, self.du_an)[0].cho_ghi(loai):
            raise DungGhi("tat")
        if estop.dang_bat():
            raise DungGhi("estop")
        if not bat_ghi_an_toan(self.bat_ghi, self.du_an):
            raise DungGhi("khoa-ghi")
        if self.so_ghi and self.dong_ho() >= self.het:
            raise DungGhi("het-gio")

    def truoc_ghi(self, loai: str) -> None:
        self.kiem(loai)                          # mọi cửa an toàn vẫn kiểm trước MỖI lệnh ghi
        self.so_ghi += 1                         # tiêu suất ngay cả khi lệnh lỗi / mất phản hồi
