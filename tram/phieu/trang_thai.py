"""`trang_thai_khe(kho, …) -> list[TrangThaiKhe]` — giao diện cho phần 2b (Đội ngũ AI), 2c (Văn phòng 3D) và phần 4
(tập khe hợp lệ), SUY lúc đọc (spec 3 §10.1). Sáu giá trị `trang_thai`, xét theo thứ tự:
`tat` → `mat_ket_noi` → `loi` → `can_nguoi` → `lam` → `ranh`."""
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from tram.cau_hinh.tram import CauHinhTram
from tram.duong_dan import doc_luc
from tram.phieu.cau_dao import trang_thai_cau_dao
from tram.phieu.kho import BanGhiPhieu, KhoPhieu
from tram.phieu.khe import cac_khe, khe_dang_bat
from tram.phieu.nhip_tim import doc_nhip, han_muc_hieu_luc


@dataclass(frozen=True)
class TrangThaiKhe:
    khe_id: str
    cli: str
    ten_goi_nho: str
    vai_uu_tien: tuple[str, ...]
    trang_thai: str               # tat | mat_ket_noi | loi | can_nguoi | lam | ranh
    phieu: dict | None            # {giao_id, bead_id, du_an, buoc, tieu_de} khi lam / can_nguoi
    han_muc: dict                 # HanMuc đã làm mới — cửa sổ chưa biết hiện rõ
    cau_dao: dict                 # {ngat, ly_do, toi_luc}
    so_phien: int
    nhip_cuoi: str | None
    models: tuple[str, ...] = ()


# "dung" = trạm/thợ cố ý dừng (bí, cần hỏi, thu hồi, estop) — không phải lỗi; tính lỗi thì khe không bao giờ rảnh lại.
KHONG_LOI = (None, "xong", "dung")

def _ket_thuc_lan_chay_cuoi(kho: KhoPhieu, khe_id: str) -> str | None:
    h = kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'chay.xong' AND json_extract(du_lieu, '$.khe_id') = ?"
                       " ORDER BY id DESC LIMIT 1", (khe_id,)).fetchone()
    return json.loads(h[0])["ket_thuc"] if h else None


def _co_can_hoi(kho: KhoPhieu, b: BanGhiPhieu) -> bool:
    """Phiếu hiệu lực có `bao.can_hoi` (escalation liên kết là của phần 4 — 4a bổ sung)."""
    return kho.db.execute("SELECT 1 FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = 'bao.can_hoi'"
                          " AND json_extract(du_lieu, '$.giao_id') = ? LIMIT 1",
                          (b.phieu.du_an, b.phieu.bead_id, b.phieu.giao_id)).fetchone() is not None


def _mot_khe(kho: KhoPhieu, khe_id: str, dk: dict, bay_gio: datetime, ch: CauHinhTram) -> TrangThaiKhe:
    b, nhip, cd = kho.phieu_hieu_luc_cua_khe(khe_id), doc_nhip(kho, khe_id), trang_thai_cau_dao(kho, khe_id, bay_gio)
    if not khe_dang_bat(kho, khe_id):
        tt = "tat"
    elif nhip is None or bay_gio - doc_luc(nhip.luc) > timedelta(seconds=ch.tho.mat_ket_noi_giay):
        tt = "mat_ket_noi"
    elif cd.ngat or (b is None and _ket_thuc_lan_chay_cuoi(kho, khe_id) not in KHONG_LOI):
        tt = "loi"
    elif b is not None and _co_can_hoi(kho, b):
        tt = "can_nguoi"
    else:
        tt = "lam" if b is not None else "ranh"
    lam = tt in ("lam", "can_nguoi")
    phieu = {k: getattr(b.phieu, k) for k in ("giao_id", "bead_id", "du_an", "buoc", "tieu_de")} if lam else None
    return TrangThaiKhe(khe_id, dk["cli"], dk["ten_goi_nho"], tuple(dk["vai_uu_tien"]), tt, phieu,
                        han_muc_hieu_luc(kho, khe_id, bay_gio, ch.han_muc).model_dump(), asdict(cd), int(lam),
                        nhip.luc if nhip else None, tuple(dk.get("models", ())))


def trang_thai_khe(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram) -> list[TrangThaiKhe]:
    return [_mot_khe(kho, khe_id, dk, bay_gio, ch) for khe_id, dk in sorted(cac_khe(kho).items())]
