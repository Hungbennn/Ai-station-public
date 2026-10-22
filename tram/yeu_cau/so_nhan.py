"""Sổ tiếp nhận yêu cầu tạo feature từ máy A (D46/D47; plan 4d 4D-0, 4D-1) — bảng `yeu_cau_feature` trong su-kien.db.

Một hàng cho mỗi `ma_yeu_cau` (khoá chính, mã cố định độc lập nội dung) kèm `digest` payload đã chuẩn hoá và người gửi
đã xác thực. Trạng thái: `nhan` (đã giữ chỗ, CHƯA gọi bd) → `dang_tao` (đúng MỘT lần, người đổi được trạng thái này gọi
`bd create`) → `da_tao` | `khong_ro`. Mỗi lần đổi là MỘT câu UPDATE có điều kiện (so sánh rồi đổi) — đúng giữa nhiều
luồng và nhiều tiến trình tram-api dùng chung file SQLite (WAL). Không câu nào đưa hàng về `nhan` hay xoá hàng."""
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from tram.duong_dan import bay_gio, tram_home
from tram.su_kien.ket_noi import mo_kho_su_kien

LUOC_DO = """
CREATE TABLE IF NOT EXISTS yeu_cau_feature (
  ma_yeu_cau TEXT PRIMARY KEY,
  du_an TEXT NOT NULL,
  digest TEXT NOT NULL,
  trang_thai TEXT NOT NULL CHECK (trang_thai IN ('nhan', 'dang_tao', 'da_tao', 'khong_ro')),
  chu TEXT,
  han REAL,
  bead_id TEXT,
  ly_do TEXT,
  nguoi_gui TEXT NOT NULL,
  lan_doi_soat INTEGER NOT NULL DEFAULT 0,
  tao_luc TEXT NOT NULL,
  doi_luc TEXT NOT NULL
);
"""
_COT = "ma_yeu_cau, du_an, digest, trang_thai, chu, han, bead_id, ly_do, nguoi_gui, lan_doi_soat"
_DOI = "UPDATE yeu_cau_feature SET "


@dataclass(frozen=True)
class BienNhan:
    ma_yeu_cau: str
    du_an: str
    digest: str
    trang_thai: str
    chu: str | None
    han: float | None
    bead_id: str | None
    ly_do: str | None
    nguoi_gui: str
    lan_doi_soat: int


class SoNhan:
    def __init__(self, duong_dan: Path):
        self._db = mo_kho_su_kien(duong_dan)
        self._db.executescript(LUOC_DO)

    def lay(self, ma: str) -> BienNhan | None:
        h = self._db.execute(f"SELECT {_COT} FROM yeu_cau_feature WHERE ma_yeu_cau=?", (ma,)).fetchone()
        return None if h is None else BienNhan(*h)

    def _doi(self, gan: str, dieu_kien: str, *tham) -> bool:
        with self._db:
            cur = self._db.execute(f"{_DOI}{gan}, doi_luc=? WHERE ma_yeu_cau=? AND {dieu_kien}", tham)
            return cur.rowcount == 1

    def nhan(self, ma: str, *, du_an: str, digest: str, nguoi_gui: str, chu: str, han: float) -> bool:
        """Giữ chỗ lần đầu. False: mã đã có hàng (của lần gửi nào đó) — đọc lại bằng `lay`."""
        try:
            with self._db:
                self._db.execute(
                    "INSERT INTO yeu_cau_feature (ma_yeu_cau, du_an, digest, trang_thai, chu, han, nguoi_gui, tao_luc,"
                    " doi_luc) VALUES (?,?,?,'nhan',?,?,?,?,?)", (ma, du_an, digest, chu, han, nguoi_gui,
                                                                  bay_gio(), bay_gio()))
            return True
        except sqlite3.IntegrityError:
            if self.lay(ma) is None:                # vi phạm CHECK/NOT NULL, không phải trùng khoá
                raise
            return False

    def gianh(self, ma: str, *, chu: str, han: float, luc: float) -> bool:
        """`nhan` mà hạn đã qua (chủ chết/treo khi chưa gọi bd) → chủ mới. An toàn vì ở `nhan` chưa ai gọi bd."""
        return self._doi("chu=?, han=?", "trang_thai='nhan' AND han<?", chu, han, bay_gio(), ma, luc)

    def nha(self, ma: str, *, chu: str) -> bool:
        """Chủ `nhan` trả chỗ (đọc bd lỗi, CHƯA gọi create) — lần gửi lại giành được ngay."""
        return self._doi("han=0", "trang_thai='nhan' AND chu=?", bay_gio(), ma, chu)

    def bat_dau_tao(self, ma: str, *, chu: str, han: float) -> bool:
        """`nhan` → `dang_tao`, chỉ chủ hiện tại. True nhiều nhất MỘT lần trong đời mã: chỉ người nhận True gọi bd."""
        return self._doi("trang_thai='dang_tao', han=?", "trang_thai='nhan' AND chu=?", han, bay_gio(), ma, chu)

    def da_tao(self, ma: str, bead_id: str) -> bool:
        """→ `da_tao` khi THẤY bead (create trả id, hoặc đối soát thấy đúng một bead mang dấu)."""
        return self._doi("trang_thai='da_tao', bead_id=?, chu=NULL, han=NULL, ly_do=NULL",
                         "trang_thai!='da_tao'", bead_id, bay_gio(), ma)

    def chu_bao_loi(self, ma: str, *, chu: str, ly_do: str) -> bool:
        """`nhan`/`dang_tao` → `khong_ro`, chỉ chủ hiện tại: create lỗi/không rõ, hoặc thấy nhiều feature mang dấu
        trước khi tạo. Từ `khong_ro` không bao giờ quay lại tạo."""
        return self._doi("trang_thai='khong_ro', ly_do=?, chu=NULL, han=NULL",
                         "trang_thai IN ('nhan','dang_tao') AND chu=?", ly_do, bay_gio(), ma, chu)

    def het_han(self, ma: str, *, luc: float) -> bool:
        """`dang_tao` quá hạn (chủ chết sau khi gọi bd) → `khong_ro`. Hết hạn KHÔNG cho phép tạo lại."""
        return self._doi("trang_thai='khong_ro', ly_do='het_han', chu=NULL, han=NULL",
                         "trang_thai='dang_tao' AND han<?", bay_gio(), ma, luc)

    def doi_soat(self, ma: str) -> bool:
        """Đếm một lần đối soát chưa kết luận của hàng `khong_ro`; giữ nguyên `ly_do` gốc."""
        return self._doi("lan_doi_soat=lan_doi_soat+1", "trang_thai='khong_ro'", bay_gio(), ma)

    def close(self) -> None:
        self._db.close()


def mo_so_nhan() -> SoNhan:
    return SoNhan(tram_home() / "su-kien.db")
