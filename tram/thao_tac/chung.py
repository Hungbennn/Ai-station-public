"""Phần dùng chung của các thao tác ghi dashboard."""
from collections.abc import Callable
from dataclasses import dataclass

from tram.beads.bd import Bd
from tram.beads.mo_hinh import Bead
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chay import cung_version
from tram.thao_tac.duyet_merge import NguonDuyet
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import XungDot

TAC_NHAN = "dai-ca/dashboard"


@dataclass(frozen=True)
class NguCanhGhi:
    bd: Bd               # actor dai-ca/dashboard (test: BdGia)
    kho: KhoSuKien
    kho_tt: KhoThaoTac
    du_an: str
    nguon_duyet: Callable[[str], NguonDuyet] | None = None


def kiem_version(bead: Bead, expected: str) -> None:
    if not cung_version(bead.updated_at, expected):
        raise XungDot(f"Bead {bead.id} đã đổi (hiện {bead.updated_at}, đang xem {expected}) — tải lại")


def co_su_kien(kho: KhoSuKien, du_an: str, bead_id: str | None, loai: str, ma: str) -> bool:
    def khop(s) -> bool:
        return s.du_lieu.get("ma_thao_tac") == ma

    if bead_id is not None:
        return kho.moi_nhat(du_an, bead_id, loai, dieu_kien=khop) is not None
    return any(khop(s) for s in kho.gan_day(du_an, loai, 50))


def ghi_su_kien_mot_lan(kho: KhoSuKien, du_an: str, bead_id: str | None, loai: str, du_lieu: dict,
                        *, ma: str) -> bool:
    """Ghi sự kiện kèm ma_thao_tac nếu chưa có — crash giữa 'ghi' và 'đánh dấu bước' không sinh bản thứ hai (G7)."""
    if co_su_kien(kho, du_an, bead_id, loai, ma):
        return False
    kho.ghi(du_an, loai, {**du_lieu, "ma_thao_tac": ma}, bead_id=bead_id, tac_nhan=TAC_NHAN)
    return True
