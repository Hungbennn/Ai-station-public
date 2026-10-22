"""Một chuỗi deploy (spec `tu-deploy`: Kiểm còn sống sau mỗi lần deploy · Deploy hỏng thì tự lùi · Lùi cũng hỏng thì
dừng hẳn; D75, D97 luật 1) — hàm thuần trên `chay(buoc, lenh) -> KetQuaBuoc`:

    deploy ─đạt→ kiểm còn sống ─đạt→ `dat`
       └hỏng/quá hạn────┴hỏng/quá hạn→ lùi ─đạt→ kiểm còn sống ─đạt→ `da_lui`
                                         └hỏng/quá hạn──────┴hỏng/quá hạn→ `lui_hong`

Bước nào không xác nhận được đã thu hồi cả cây tiến trình (`da_thu_hoi=False`) → DỪNG ngay, `khong_ro`: không chạy
lùi chồng lên một lệnh có thể còn sống (D97 luật 2 — không chạy lại mù). Không xét estop/tạm dừng giữa chuỗi: chuỗi
đã bắt đầu thì làm nốt (spec "Đang làm dở thì làm nốt an toàn")."""
from collections.abc import Callable

from tram.deploy.lenh import KetQuaBuoc
from tram.tu_dong.cai_dat import CaiDatTuDong

Chay = Callable[[str, str], KetQuaBuoc]


def chay_chuoi(cd: CaiDatTuDong, chay: Chay) -> str:
    """→ `dat` | `da_lui` | `lui_hong` | `khong_ro`."""
    kq = chay("deploy", cd.lenh_deploy)
    if not kq.da_thu_hoi:
        return "khong_ro"
    if kq.dat:
        kq = chay("kiem_song", cd.lenh_kiem_song)
        if not kq.da_thu_hoi:
            return "khong_ro"
        if kq.dat:
            return "dat"
    kq = chay("lui", cd.lenh_lui)
    if not kq.da_thu_hoi:
        return "khong_ro"
    if kq.dat:
        kq = chay("kiem_song_sau_lui", cd.lenh_kiem_song)
        if not kq.da_thu_hoi:
            return "khong_ro"
        if kq.dat:
            return "da_lui"
    return "lui_hong"
