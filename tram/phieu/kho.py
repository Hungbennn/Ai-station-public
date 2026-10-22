"""Kho phiếu bền (spec 3 §6.6) + định nghĩa DUY NHẤT của "phiếu hiệu lực" (§4, #10) + thẻ chắn `luot` (§6.3).

Một kết nối SQLite (WAL, busy_timeout) cho mỗi người dùng; mọi thay đổi trạng thái đi qua `giao_dich()` =
`BEGIN IMMEDIATE` — hai nhịp tim đồng thời được tuần tự hoá. Khởi động lại: mọi thứ đọc lại từ kho."""
import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tram.duong_dan import tram_home
from tram.phieu.luoc_do import LUOC_DO
from tram.phieu.mo_hinh import LuotCu, Phieu
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.su_kien.ket_noi import LUOC_DO as LUOC_DO_SU_KIEN, mo_kho_su_kien
from tram.su_kien.yeu_cau import LUOC_DO as LUOC_DO_YEU_CAU

DU_AN_TRAM = "_tram"
TAC_NHAN = "tram/api"
_COT = "noi_dung, trang_thai, ket_thuc, dung_mem, han_giu, cap_luc, nhip_cuoi, ket_thuc_luc, may_id"


def chuoi_gio(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class BanGhiPhieu:
    phieu: Phieu
    trang_thai: str               # 'hieu_luc' | 'ket_thuc'
    ket_thuc: str | None
    dung_mem: str | None
    cap_luc: str
    nhip_cuoi: str | None
    ket_thuc_luc: str | None
    may_id: str


class KhoPhieu:
    def __init__(self, duong_dan: Path):
        self.db = mo_kho_su_kien(duong_dan)
        self.db.executescript(LUOC_DO_SU_KIEN + LUOC_DO_YEU_CAU + LUOC_DO)
        self.db.isolation_level = None       # tự quản giao dịch: không có giao dịch ngầm nào ngoài giao_dich()

    @contextmanager
    def giao_dich(self) -> Iterator:
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield self.db
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        self.db.execute("COMMIT")

    def ghi_su_kien(self, du_an: str, loai: str, du_lieu: dict, *, luc: datetime, bead_id: str | None = None,
                    tac_nhan: str = TAC_NHAN, **kw) -> int:
        """Chỉ gọi bên trong `giao_dich()`."""
        return ghi_trong_giao_dich(self.db, du_an, loai, du_lieu, bead_id=bead_id, tac_nhan=tac_nhan,
                                   luc=chuoi_gio(luc), **kw)

    def _mot(self, where: str, tham_so: tuple) -> BanGhiPhieu | None:
        h = self.db.execute(f"SELECT {_COT} FROM phieu WHERE {where}", tham_so).fetchone()
        if h is None:
            return None
        return BanGhiPhieu(Phieu.model_validate({**json.loads(h[0]), "han_giu": h[4]}), *h[1:4], *h[5:9])

    def lay(self, giao_id: str) -> BanGhiPhieu | None:
        return self._mot("giao_id = ?", (giao_id,))

    def phieu_hieu_luc(self, du_an: str, bead_id: str) -> BanGhiPhieu | None:
        return self._mot("du_an = ? AND bead_id = ? AND trang_thai = 'hieu_luc'", (du_an, bead_id))

    def phieu_hieu_luc_cua_khe(self, khe_id: str) -> BanGhiPhieu | None:
        return self._mot("khe_id = ? AND trang_thai = 'hieu_luc'", (khe_id,))

    def cac_phieu_hieu_luc(self) -> list[BanGhiPhieu]:
        return [self.lay(g) for (g,) in self.db.execute(
            "SELECT giao_id FROM phieu WHERE trang_thai = 'hieu_luc' ORDER BY giao_id")]

    def luot_hien_hanh(self, du_an: str, bead_id: str) -> int:
        h = self.db.execute("SELECT luot FROM luot_bead WHERE du_an = ? AND bead_id = ?", (du_an, bead_id)).fetchone()
        return h[0] if h else 0

    def kiem_the_chan(self, khe_id: str, giao_id: str | None, luot: int | None) -> BanGhiPhieu:
        if (b := self.lay(giao_id) if giao_id else None) is None:
            raise LuotCu(None, None, None, False)
        p = b.phieu
        dung = self.luot_hien_hanh(p.du_an, p.bead_id)
        if b.trang_thai != "hieu_luc" or p.khe_id != khe_id or p.luot != luot or dung != luot:
            raise LuotCu(p.bead_id, p.du_an, dung, b.ket_thuc == "thu_hoi" and p.khe_id == khe_id)
        return b

    def ghi_tu_choi(self, loi: LuotCu, *, khe_id: str, giao_id: str | None, luot: int | None, luc: datetime) -> None:
        """`tho.tu_choi` (H2) — trong giao dịch của người gọi."""
        self.ghi_su_kien(loi.du_an or DU_AN_TRAM, "tho.tu_choi", {"khe_id": khe_id, "giao_id": giao_id,
                         "bead_id": loi.bead_id, "luot_gui": luot, "luot_dung": loi.luot_dung},
                         luc=luc, bead_id=loi.bead_id, tac_nhan=TAC_NHAN)

    def phieu_theo_giao_id(self, giao_id: str) -> dict | None:
        """Cho memory 1b-2 (§10): trả cả khi phiếu đã hết hiệu lực; `ma_giao` CHỈ khi còn hiệu lực."""
        if (b := self.lay(giao_id)) is None:
            return None
        con = b.trang_thai == "hieu_luc"
        return {"du_an": b.phieu.du_an, "vai": b.phieu.vai, "ma_giao": b.phieu.ma_giao if con else None,
                "con_hieu_luc": con}

    def close(self) -> None:
        self.db.close()


def mo_kho_phieu() -> KhoPhieu:
    return KhoPhieu(tram_home() / "su-kien.db")
