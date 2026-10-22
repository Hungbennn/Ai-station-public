"""Dựng kho phiếu tạm + phiếu hiệu lực cho test (CHỈ DÙNG TRONG TEST) — chưa qua luật cấp phiếu của Task 17."""
from datetime import datetime, timedelta, timezone

from phieu_gia import de_xuat
from tram.phieu.ghi import giao_id_moi, tang_luot, them_phieu
from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.mo_hinh import Phieu, sinh_ma_giao

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


def kho_tam(tmp_path) -> KhoPhieu:
    return KhoPhieu(tmp_path / "su-kien.db")


def dat_phieu(kho: KhoPhieu, khe_id: str = "B/claude-1", *, luc: datetime = LUC, **kw) -> Phieu:
    dx = de_xuat(**kw)
    with kho.giao_dich() as db:
        p = Phieu(**dx.model_dump(), giao_id=giao_id_moi(db, luc), luot=tang_luot(db, dx.du_an, dx.bead_id),
                  khe_id=khe_id, han_giu=chuoi_gio(luc + timedelta(minutes=10)), ma_giao=sinh_ma_giao())
        them_phieu(db, p, may_id=khe_id.split("/")[0], cap_luc=luc)
    return p
