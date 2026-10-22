"""Bảo trì hằng đêm của memory service (spec 1b §9.4): thăng cấp (1b-3, §8), dọn phiên bản LanceDB + sao lưu, mỗi
ngày (giờ VN) một lần.

Ngày bảo trì gần nhất ghi bền vào `<thu_muc_nho>/bao-tri-cuoi` — khởi động lại trong cùng ngày không làm lần hai."""
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from tram.cham_cot.ghi import GIO_VN
from tram.nho.dich_vu import DichVuNho
from tram.nho.sao_luu import sao_luu_nho
from tram.nho.vong import NguCanhNho
from tram.nho.vong_thang_cap import mot_lan_thang_cap

GIO_BAO_TRI = 3            # giờ VN
TEP_BAO_TRI = "bao-tri-cuoi"


@dataclass
class BaoTri:
    ngay_cuoi: date | None = None
    tep: Path | None = None            # None → chỉ nhớ trong tiến trình

    @classmethod
    def doc(cls, tep: Path) -> "BaoTri":
        try:
            return cls(date.fromisoformat(tep.read_text(encoding="utf-8").strip()), tep)
        except (OSError, ValueError):
            return cls(None, tep)

    def ghi(self, ngay: date) -> None:
        self.ngay_cuoi = ngay
        if self.tep is not None:
            tam = self.tep.with_name(self.tep.name + ".tam")
            tam.write_text(ngay.isoformat(), encoding="utf-8")
            os.replace(tam, self.tep)


def bao_tri_neu_den_han(nc: NguCanhNho, dv: DichVuNho, bt: BaoTri, bay_gio: datetime, *, thu_muc: Path,
                        dich: Path) -> bool:
    dv.dem_dung.xa_neu_den_han(nc.kho, bay_gio)
    vn = bay_gio.astimezone(GIO_VN)
    if vn.hour < GIO_BAO_TRI or bt.ngay_cuoi == vn.date():
        return False
    if nc.vai_thang_cap is not None:                      # 1b-3 (spec 1b §8): thăng cấp mỗi ngày, trước khi chụp
        bc = mot_lan_thang_cap(nc, bay_gio, vai_soan=nc.vai_thang_cap)
        if bc.cap or bc.loi:
            print(f"thăng cấp: {bc}"[:500], file=sys.stderr, flush=True)
    with nc.kho.khoa_gop:  # chặn /ghi trước khi chụp LanceDB + nhật ký; thứ tự khoa_gop → khoa
        nc.kho.don_dep()
        sao_luu_nho(thu_muc, dich, kho=nc.kho, nhat_ky=nc.nhat_ky, luc=bay_gio)
    bt.ghi(vn.date())
    return True
