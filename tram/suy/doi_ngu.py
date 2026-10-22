"""Màn Đội ngũ AI (spec 2 §5.4): mỗi khe một thẻ — suy từ `trang_thai_khe` của phần 3 (spec 3 §10.1) — kèm
`phien_ban` cho thao tác bật/tắt/đóng cầu dao (§12.3), mức hạn mức theo luật nhận việc (spec 3 §8.2), luật
vai ↔ khe và bảng điểm thợ. Tên gợi nhớ, KHÔNG BAO GIỜ email (§5.4)."""
from datetime import datetime, timedelta

from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhTram
from tram.han_muc.luat import cham_nguong_ngung, duoc_nhan
from tram.han_muc.mo_hinh import HanMuc, co_chua_biet
from tram.phieu.khe import phien_ban_khe, su_kien_khe
from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.mo_hinh import VAI_CUA_BUOC
from tram.phieu.trang_thai import TrangThaiKhe, trang_thai_khe
from tram.suy.bang_diem import bang_diem
from tram.suy.lam_sach import lam_sach
from tram.suy.nhan_vat import ten_nhan_vat

SO_NGAY_BANG_DIEM = 30                    # D14: mặc định bảng điểm = 30 ngày gần nhất, mọi dự án
LUAT_VAI = (
    "Vai là ưu tiên, không cố định: khe cạn hạn mức thì khe khác nhận vai đó (kiến trúc Q14).",
    "Luật cứng: khe đã code một bead không bao giờ QC chính bead đó — thiếu khe khác thì bead chờ (Q14).",
    "Khe tắt, cầu dao ngắt, mất kết nối, hoặc có cửa sổ hạn mức đã biết ≥ ngưỡng ngừng: không nhận việc mới "
    "(spec 3 §6.2, §8.2); cửa sổ tuần ≥ ngưỡng ưu tiên: chỉ nhận P0–P1.",
    "Hạn mức chưa biết vẫn nhận việc, kèm cảnh báo vàng (#15).",
    "Chọn bead, bước và khe cụ thể là việc của bộ giao việc phần 4 (spec 4 §5.3 — chưa duyệt).",
)


def muc_han_muc(hm: HanMuc, ng: CauHinhHanMuc) -> str:
    """`ngung` (luật 1) | `chi_p0_p1` (luật 2) | `chua_biet` (luật 3, vàng) | `ok`."""
    if cham_nguong_ngung(hm, ngung=ng.ngung):
        return "ngung"
    if not duoc_nhan(hm, 2, ngung=ng.ngung, tuan_chi_uu_tien=ng.tuan_chi_uu_tien):
        return "chi_p0_p1"
    return "chua_biet" if co_chua_biet(hm) else "ok"


def _ten(tt: TrangThaiKhe) -> str:
    ten = lam_sach(tt.ten_goi_nho, 64)
    return tt.khe_id if not ten or "@" in ten else ten


def vi_sao_tat(kho: KhoPhieu, tt: TrangThaiKhe) -> str | None:
    """2f T1: lý do của `khe.tat` mới nhất, chỉ khi khe đang `tat`; rỗng → None."""
    x = su_kien_khe(kho, tt.khe_id, ("khe.bat", "khe.tat")) if tt.trang_thai == "tat" else None
    return (lam_sach(x[2].get("vi_sao"), 120) or None) if x and x[1] == "khe.tat" else None


def the_khe(kho: KhoPhieu, tt: TrangThaiKhe, ch: CauHinhTram, ten: str | None = None) -> dict:
    # Danh sách cho phép, không serialize cả phiếu nếu upstream thêm credential.
    phieu = None if tt.phieu is None else {
        **{k: tt.phieu[k] for k in ("giao_id", "du_an", "bead_id", "buoc", "vai") if k in tt.phieu},
        "tieu_de": lam_sach(tt.phieu["tieu_de"], 200)}
    return {"khe_id": tt.khe_id, "may": tt.khe_id.split("/")[0], "cli": tt.cli, "ten_goi_nho": _ten(tt),
            "vai_uu_tien": list(tt.vai_uu_tien), "trang_thai": tt.trang_thai, "phieu": phieu,
            "han_muc": tt.han_muc, "muc_han_muc": muc_han_muc(HanMuc.model_validate(tt.han_muc), ch.han_muc),
            "cau_dao": tt.cau_dao, "so_phien": tt.so_phien, "nhip_cuoi": tt.nhip_cuoi,
            "phien_ban": phien_ban_khe(kho, tt.khe_id),
            # 2f T1: tên nhân vật dùng chung với Văn phòng ("Claude 1"); `ten` None → tính riêng cho khe này
            "ten": ten or ten_nhan_vat([(tt.khe_id, tt.cli)])[tt.khe_id], "vi_sao_tat": vi_sao_tat(kho, tt)}


def du_hang_khe(hang: list[dict], ds: list[TrangThaiKhe]) -> list[dict]:
    """D41: mỗi (khe, vai ưu tiên) của khe đã khai — cùng nguồn `trang_thai_khe` với thẻ khe — có một hàng dù bộ lọc
    không còn phiếu nào: 0 phiếu, vai coder mẫu 0 (tỉ lệ null → "chưa có"), vai khác mẫu null (D29). Hàng có phiếu
    giữ nguyên, kể cả vai ngoài vai ưu tiên (vai không cố định — Q14). Xếp theo (khe, vai) như `bang_diem`."""
    theo = {(h["khe_id"], h["vai"]): h for h in hang}
    for tt in ds:
        for v in tt.vai_uu_tien:
            mau = 0 if v == "coder" else None
            theo.setdefault((tt.khe_id, v), {"khe_id": tt.khe_id, "vai": v, "so_phieu": 0, "so_xong": 0,
                                             "lan_chay_tb": None, "qua_lan_dau": None, "qua_lan_dau_mau": mau,
                                             "bi_tra_ve": None, "bi_tra_ve_mau": mau})
    return [theo[k] for k in sorted(theo)]


def doi_ngu(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram, du_an: str | None = None,
            so_ngay: int = SO_NGAY_BANG_DIEM) -> dict:
    """Bảng điểm lọc theo dự án (None = mọi dự án) và `so_ngay` × 24 giờ tính lùi từ `bay_gio` (D14, D28); bộ lọc
    không làm mất hàng của khe đã khai (D41)."""
    tu = chuoi_gio(bay_gio - timedelta(days=so_ngay))
    ds = trang_thai_khe(kho, bay_gio=bay_gio, ch=ch)
    ten = ten_nhan_vat([(tt.khe_id, tt.cli) for tt in ds])
    return {"bat": True, "khe": [the_khe(kho, tt, ch, ten[tt.khe_id]) for tt in ds],
            "luat_vai": {"vai_cua_buoc": dict(VAI_CUA_BUOC), "luat": list(LUAT_VAI)},
            "bang_diem": du_hang_khe(bang_diem(kho.db, du_an=du_an, tu=tu), ds)}
