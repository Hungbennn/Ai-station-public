import json
import sqlite3
from collections.abc import Callable
from pathlib import Path

from tram.duong_dan import bay_gio, tram_home
from tram.su_kien.ket_noi import LUOC_DO, mo_kho_su_kien
from tram.su_kien.mo_hinh import SuKien
from tram.su_kien.yeu_cau import YeuCauChamLai

_CHON = ("SELECT luc, du_an, bead_id, loai, tac_nhan, du_lieu, id,"
         " token_vao, token_ra, mo_hinh, thoi_gian_ms FROM su_kien")
# Sự kiện cắt chuỗi lỗi liên tiếp: chấm được, hoặc Đại ca bấm "thử lại" (spec 0+1a §5.6).
_CAT_CHUOI_LOI = ("cham_cot.ket_qua", "cham_cot.thu_lai")


class KhoSuKien:
    """Bảng chỉ thêm. Trạng thái hiển thị tính lúc đọc."""

    def __init__(self, duong_dan: Path):
        self._db = mo_kho_su_kien(duong_dan)
        self._db.executescript(LUOC_DO)
        self.yeu_cau = YeuCauChamLai(self._db)

    @property
    def db(self) -> sqlite3.Connection:
        """Kết nối thô, như `KhoPhieu.db` — `tram/tu_dong/luu.py` đọc/ghi trong giao dịch của riêng nó (TM-1)."""
        return self._db

    def ghi(self, du_an: str, loai: str, du_lieu: dict, *, bead_id: str | None = None,
            tac_nhan: str = "tram/cham-cot", token_vao: int | None = None,
            token_ra: int | None = None, mo_hinh: str | None = None,
            thoi_gian_ms: int | None = None) -> str:
        luc = bay_gio()
        with self._db:
            self._db.execute(
                "INSERT INTO su_kien (luc, du_an, bead_id, loai, tac_nhan, du_lieu,"
                " token_vao, token_ra, mo_hinh, thoi_gian_ms) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (luc, du_an, bead_id, loai, tac_nhan,
                 json.dumps(du_lieu, ensure_ascii=False, sort_keys=True),
                 token_vao, token_ra, mo_hinh, thoi_gian_ms))
        return luc

    def _doc(self, sql: str, tham_so: tuple) -> list[SuKien]:
        hang = self._db.execute(sql, tham_so).fetchall()
        return [SuKien(h[0], h[1], h[2], h[3], h[4], json.loads(h[5]), *h[6:11]) for h in hang]

    def moi_nhat(self, du_an: str, bead_id: str, loai: str, *,
                 dieu_kien: Callable[[SuKien], bool] | None = None) -> SuKien | None:
        ds = self._doc(f"{_CHON} WHERE du_an=? AND bead_id=? AND loai=? ORDER BY id DESC",
                       (du_an, bead_id, loai))
        return next((s for s in ds if dieu_kien is None or dieu_kien(s)), None)

    def moi_nhat_cac_loai(self, du_an: str, bead_id: str, loai: tuple[str, ...], *,
                          dieu_kien: Callable[[SuKien], bool] | None = None) -> SuKien | None:
        """Sự kiện ghi sau cùng (theo thứ tự ghi trong bảng) trong nhiều loại."""
        ds = self._doc(
            f"{_CHON} WHERE du_an=? AND bead_id=? AND loai IN ({','.join('?' * len(loai))}) ORDER BY id DESC",
            (du_an, bead_id, *loai))
        return next((s for s in ds if dieu_kien is None or dieu_kien(s)), None)

    def gan_day(self, du_an: str, loai: str, gioi_han: int, *, du_lieu_co: dict[str, str] | None = None
                ) -> list[SuKien]:
        """`du_lieu_co`: lọc theo trường của `du_lieu` ngay trong truy vấn (khoá do mã đặt, không từ ngoài)."""
        loc = [x for k, v in (du_lieu_co or {}).items() for x in (f"$.{k}", v)]
        return self._doc(f"{_CHON} WHERE du_an=? AND loai=?{' AND json_extract(du_lieu, ?) = ?' * (len(loc) // 2)}"
                         " ORDER BY id DESC LIMIT ?", (du_an, loai, *loc, gioi_han))

    def doc_moc(self, du_an: str) -> str | None:
        h = self._db.execute("SELECT updated_at FROM moc_quet WHERE du_an=?", (du_an,)).fetchone()
        return h[0] if h else None

    def ghi_moc(self, du_an: str, updated_at: str) -> None:
        with self._db:
            self._db.execute(
                "INSERT INTO moc_quet (du_an, updated_at) VALUES (?, ?)"
                " ON CONFLICT(du_an) DO UPDATE SET updated_at=excluded.updated_at",
                (du_an, updated_at))

    def dem_loi_lien_tiep(self, du_an: str, bead_id: str) -> int:
        dem = 0
        for s in self._doc(f"{_CHON} WHERE du_an=? AND bead_id=? AND loai IN (?, ?, ?) ORDER BY id DESC",
                           (du_an, bead_id, "cham_cot.loi", *_CAT_CHUOI_LOI)):
            if s.loai == "cham_cot.ket_qua" and s.du_lieu.get("huy"):
                continue  # kết quả bị huỷ không phải lần chấm thành công (§5.6)
            if s.loai != "cham_cot.loi":
                break
            dem += 1
        return dem

    def sau_id(self, id: int, gioi_han: int) -> list[SuKien]:
        """Sự kiện có id > `id`, tăng dần — SSE và tram-bao-tin đọc theo mốc riêng (spec 2 §6, §12.2)."""
        return self._doc(f"{_CHON} WHERE id > ? ORDER BY id LIMIT ?", (id, gioi_han))

    def id_moi_nhat(self) -> int:
        return self._db.execute("SELECT COALESCE(MAX(id), 0) FROM su_kien").fetchone()[0]

    def cua_bead(self, du_an: str, bead_id: str, gioi_han: int = 200) -> list[SuKien]:
        """Dòng thời gian của bead: `gioi_han` sự kiện mới nhất, xếp cũ → mới."""
        ds = self._doc(f"{_CHON} WHERE du_an=? AND bead_id=? ORDER BY id DESC LIMIT ?",
                       (du_an, bead_id, gioi_han))
        return ds[::-1]

    def cac_du_an(self) -> list[str]:
        return [h[0] for h in self._db.execute("SELECT DISTINCT du_an FROM su_kien ORDER BY du_an")]

    def close(self) -> None:
        """tram-api mở một kho cho mỗi yêu cầu và đóng bằng `contextlib.closing` (N5)."""
        self._db.close()


def mo_kho() -> KhoSuKien:
    return KhoSuKien(tram_home() / "su-kien.db")
