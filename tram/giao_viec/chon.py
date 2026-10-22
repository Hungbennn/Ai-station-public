"""Thứ tự bead (spec 4 §5.2) và luật khe nào nhận bước nào (§5.3) — hàm thuần trên `trang_thai_khe()` của phần 3."""
from dataclasses import dataclass

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.tram import CauHinhTram
from tram.han_muc.luat import duoc_nhan
from tram.han_muc.mo_hinh import HanMuc
from tram.phieu.trang_thai import TrangThaiKhe

VAI = {"code": "coder", "qc": "qc", "spec": "spec"}
UU_TIEN_MAC_DINH = 2           # bd bỏ `priority` khỏi JSON khi rỗng; mặc định của bd là P2


@dataclass(frozen=True)
class UngVien:
    du_an: DuAn
    bead: Bead
    buoc: str                  # "code" | "qc"
    do: bool                   # bead dở: phiếu cuối kết thúc không phải `xong`, chờ giao lại
    da_code: frozenset[str]    # khe đã chạy BẤT KỲ phiếu `code` nào của bead (tra `giao.nhan`)


def uu_tien(b: Bead) -> int:
    return b.priority if b.priority is not None else UU_TIEN_MAC_DINH


def khoa_sap_xep(uv: UngVien) -> tuple:
    """(1) bead dở trước; (2) `qc` trước `code`; (3) P0 → P4; (4) `created_at` cũ trước; (5) `id`."""
    return (not uv.do, uv.buoc != "qc", uu_tien(uv.bead), uv.bead.created_at or "~", uv.bead.id)


def _nhan_duoc(han_muc: HanMuc | None, uv: UngVien, ch: CauHinhTram) -> bool:
    return duoc_nhan(han_muc, uu_tien(uv.bead), ngung=ch.han_muc.ngung, tuan_chi_uu_tien=ch.han_muc.tuan_chi_uu_tien)


def khe_hop_le(cac_khe: list[TrangThaiKhe], uv: UngVien, ch: CauHinhTram) -> list[TrangThaiKhe]:
    """Đang bật, cầu dao đóng, `duoc_nhan` đúng, không bị Q14 cấm với bead (§5.3 mục 3)."""
    return [t for t in cac_khe if t.trang_thai != "tat" and not t.cau_dao.get("ngat")
            and _nhan_duoc(HanMuc.model_validate(t.han_muc), uv, ch)
            and not (uv.buoc == "qc" and t.khe_id in uv.da_code)]


def khe_nhan(khe_id: str, han_muc: HanMuc | None, uv: UngVien, cac_khe: list[TrangThaiKhe],
             ch: CauHinhTram, *, model: str | None = None) -> bool:
    if model is not None:
        cac_khe = [t for t in khe_hop_le(cac_khe, uv, ch)
                   if t.trang_thai == "ranh" and t.cli == "claude" and model in t.models]
        if not any(t.khe_id == khe_id for t in cac_khe):
            return False
    if not _nhan_duoc(han_muc, uv, ch):                                       # 1. hạn mức
        return False
    if uv.buoc == "qc" and khe_id in uv.da_code:                              # 2. Q14 — luật cứng (G2)
        return False
    hop_le = [t for t in khe_hop_le(cac_khe, uv, ch) if t.khe_id != khe_id]
    x = next((t for t in cac_khe if t.khe_id == khe_id), None)
    vai = VAI[uv.buoc]
    if (x is None or vai not in x.vai_uu_tien) and any(                       # 4. vai ưu tiên, rồi mới lan
            vai in t.vai_uu_tien and t.trang_thai in ("ranh", "lam") for t in hop_le):
        return False
    if uv.buoc == "code" and khe_id not in uv.da_code and any(               # 5. ưu tiên khe đã code
            t.khe_id in uv.da_code and t.trang_thai == "ranh" for t in hop_le):
        return False
    return True
