"""Cột "Mới xong" của bảng "Theo dự án" ở Tổng quan (mockup trang-tong-quan.js `VIEC_MOI_XONG`): bead đã đóng có
`closed_at` lớn nhất trong bộ đệm beads (`bd list --all`). Chỉ mã, tiêu đề đã làm sạch, giờ."""
from tram.beads.mo_hinh import Bead
from tram.suy.lam_sach import lam_sach


def moi_xong(beads: list[Bead]) -> dict | None:
    xong = [b for b in beads if b.status == "closed" and b.closed_at]
    if not xong:
        return None
    b = max(xong, key=lambda x: x.closed_at)
    return {"id": b.id, "tieu_de": lam_sach(b.title, 200), "luc": b.closed_at}
