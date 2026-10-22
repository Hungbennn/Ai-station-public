"""Tiếp nhận yêu cầu tạo feature trên máy B (D46/D47; plan 4d 4D-0, 4D-1) — máy trạng thái trên `SoNhan`.

Bất biến: mỗi `ma_yeu_cau` gọi `bd create` NHIỀU NHẤT MỘT lần trong đời — chỉ lần gửi đổi được `nhan → dang_tao` mới
gọi. Trước khi tạo luôn đối soát theo dấu dòng đầu. Kết quả không rõ (lỗi, timeout, chết giữa chừng, quá hạn) →
`khong_ro`: chỉ đối soát lại theo dấu, KHÔNG BAO GIỜ tạo lại. Lý do trả ra là mã cố định — không chép argv, stderr hay
nội dung phiếu (Q06)."""
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass

from tram.beads.bd import LoiBd
from tram.yeu_cau.mau import LOAI, NHAN, YeuCau, digest, mo_ta, tim_theo_dau
from tram.yeu_cau.so_nhan import SoNhan

HAN_GIAY = 300.0        # > 2 × timeout 120 s của `chay_bd`: chủ còn sống không bị coi là chết


@dataclass(frozen=True)
class KetQua:
    trang_thai: str     # da_tao | da_co | dang_xu_ly | khong_ro | xung_dot | chua_tao
    bead_id: str | None = None
    ly_do: str | None = None


def _doi_soat(bd, ma: str) -> tuple[str | None, str | None]:
    """(id, None): thấy đúng một feature mang dấu · (None, None): chưa thấy · (None, lý do): không kết luận được."""
    try:
        ds = tim_theo_dau(bd.tat_ca_yeu_cau(), ma)
    except Exception:                           # LoiBd, JSON/giải mã lạ: không kết luận, không lộ chi tiết
        return None, "doc_bd_loi"
    if len(ds) > 1:
        return None, "nhieu_feature"
    return (ds[0], None) if ds else (None, None)


def _khong_ro(so: SoNhan, bd, ma: str) -> KetQua:
    co, ly_do = _doi_soat(bd, ma)
    if co is not None:
        so.da_tao(ma, co)
        return KetQua("da_co", co)
    so.doi_soat(ma)
    return KetQua("khong_ro", ly_do=ly_do or "chua_thay")


def _tao(so: SoNhan, bd, yc: YeuCau, chu: str, dong_ho: Callable[[], float]) -> KetQua:
    co, ly_do = _doi_soat(bd, yc.ma)            # đối soát TRƯỚC mọi lần tạo: sổ có thể mất, bead có thể đã có
    if ly_do == "nhieu_feature":                # đã có hơn một feature mang dấu: Đại ca xử lý tay, không chọn bừa
        so.chu_bao_loi(yc.ma, chu=chu, ly_do=ly_do)
        return KetQua("khong_ro", ly_do=ly_do)
    if ly_do is not None:
        so.nha(yc.ma, chu=chu)
        return KetQua("chua_tao", ly_do=ly_do)
    if co is not None:
        so.da_tao(yc.ma, co)
        return KetQua("da_co", co)
    if not so.bat_dau_tao(yc.ma, chu=chu, han=dong_ho() + HAN_GIAY):
        return KetQua("dang_xu_ly")             # quá hạn khi đang đọc bd, lần gửi khác đã giành chỗ — không tạo
    try:
        moi = bd.tao(yc.tieu_de, loai=LOAI, mo_ta=mo_ta(yc), nhan=NHAN, uu_tien=yc.uu_tien)
    except LoiBd:
        so.chu_bao_loi(yc.ma, chu=chu, ly_do="bd_loi")
    except Exception:
        so.chu_bao_loi(yc.ma, chu=chu, ly_do="bd_khong_ro")
    else:
        so.da_tao(yc.ma, moi)
        return KetQua("da_tao", moi)
    return _khong_ro(so, bd, yc.ma)


def tiep_nhan(so: SoNhan, bd, yc: YeuCau, *, nguoi_gui: str,
              dong_ho: Callable[[], float] = time.time) -> KetQua:
    dg, chu = digest(yc), secrets.token_hex(8)
    if so.nhan(yc.ma, du_an=yc.du_an, digest=dg, nguoi_gui=nguoi_gui, chu=chu, han=dong_ho() + HAN_GIAY):
        return _tao(so, bd, yc, chu, dong_ho)
    bn = so.lay(yc.ma)
    if bn.digest != dg:
        return KetQua("xung_dot")               # không ghi đè, không tạo — kể cả khi đang xử lý hay chưa rõ
    if bn.trang_thai == "da_tao":
        return KetQua("da_co", bn.bead_id)
    if bn.trang_thai == "nhan":
        if so.gianh(yc.ma, chu=chu, han=dong_ho() + HAN_GIAY, luc=dong_ho()):
            return _tao(so, bd, yc, chu, dong_ho)
        return KetQua("dang_xu_ly")
    if bn.trang_thai == "dang_tao" and not so.het_han(yc.ma, luc=dong_ho()):
        return KetQua("dang_xu_ly")
    return _khong_ro(so, bd, yc.ma)
