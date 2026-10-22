"""Yêu cầu chấm lại bền (spec 0+1a §5.6) và ảnh decision giữa hai lượt quét.

Bảng vận hành, không phải nhật ký: mỗi yêu cầu khoá theo ID sự kiện nguồn; chỉ đánh dấu xong, không xoá.
Nguồn: `cham_cot.thu_lai` (dashboard), `cham_cot.ket_qua` có `huy` (kết quả bị bỏ), `cham_cot.can_cham_lai`
(decision đổi — 1a ghi trong cùng giao dịch với yêu cầu).
"""
import json
import sqlite3

from tram.duong_dan import bay_gio

LUOC_DO = """
CREATE TABLE IF NOT EXISTS yeu_cau_cham_lai (
  du_an TEXT NOT NULL,
  bead_id TEXT NOT NULL,
  nguon_id INTEGER NOT NULL,   -- id sự kiện nguồn trong su_kien
  nguon TEXT NOT NULL,         -- 'thu_lai' | 'huy' | 'decision'
  xong_luc TEXT,
  PRIMARY KEY (du_an, bead_id, nguon_id)
);
CREATE TABLE IF NOT EXISTS anh_decision (du_an TEXT PRIMARY KEY, du_lieu TEXT NOT NULL);
"""
LOAI_THU_LAI = "cham_cot.thu_lai"
LOAI_CAN_CHAM_LAI = "cham_cot.can_cham_lai"


class YeuCauChamLai:
    def __init__(self, db: sqlite3.Connection):
        self._db = db
        db.executescript(LUOC_DO)

    def nhan_su_kien_nguon(self, du_an: str) -> int:
        """Biến `cham_cot.thu_lai` và `cham_cot.ket_qua{huy}` chưa nhận thành yêu cầu. Chạy lại không nhân đôi."""
        with self._db:
            cur = self._db.execute(
                "INSERT OR IGNORE INTO yeu_cau_cham_lai (du_an, bead_id, nguon_id, nguon)"
                " SELECT du_an, bead_id, id, CASE loai WHEN ? THEN 'thu_lai' ELSE 'huy' END FROM su_kien"
                " WHERE du_an=? AND bead_id IS NOT NULL AND (loai=? OR"
                " (loai='cham_cot.ket_qua' AND json_extract(du_lieu, '$.huy') IS NOT NULL))",
                (LOAI_THU_LAI, du_an, LOAI_THU_LAI))
        return cur.rowcount

    def dang_co_phieu(self, du_an: str, bead_id: str) -> bool:
        """#10: bead đang có phiếu hiệu lực của phần 3 — đọc bảng `phieu` cùng định nghĩa `KhoPhieu.phieu_hieu_luc`
        (`trang_thai = 'hieu_luc'`). Chưa có bảng (phần 3 chưa từng mở kho phiếu) → False."""
        try:
            return self._db.execute("SELECT 1 FROM phieu WHERE du_an=? AND bead_id=? AND trang_thai='hieu_luc'"
                                    " LIMIT 1", (du_an, bead_id)).fetchone() is not None
        except sqlite3.OperationalError as e:
            if "no such table" not in str(e):
                raise
            return False

    def dang_cho(self, du_an: str) -> dict[str, list[int]]:
        cho: dict[str, list[int]] = {}
        for bead_id, nguon_id in self._db.execute(
                "SELECT bead_id, nguon_id FROM yeu_cau_cham_lai WHERE du_an=? AND xong_luc IS NULL"
                " ORDER BY nguon_id", (du_an,)):
            cho.setdefault(bead_id, []).append(nguon_id)
        return cho

    def danh_dau_xong(self, du_an: str, bead_id: str, nguon_ids: list[int]) -> None:
        luc = bay_gio()
        with self._db:
            self._db.executemany(
                "UPDATE yeu_cau_cham_lai SET xong_luc=?"
                " WHERE du_an=? AND bead_id=? AND nguon_id=? AND xong_luc IS NULL",
                [(luc, du_an, bead_id, n) for n in nguon_ids])

    def dong_het(self, du_an: str, bead_id: str) -> None:
        """Nhận nốt sự kiện nguồn rồi đánh dấu xong mọi yêu cầu của bead (dùng khi chạm trần huỷ)."""
        self.nhan_su_kien_nguon(du_an)
        self.danh_dau_xong(du_an, bead_id, self.dang_cho(du_an).get(bead_id, []))

    def dem_huy_lien_tiep(self, du_an: str, bead_id: str) -> int:
        """Số `cham_cot.ket_qua{huy}` liền nhau mới nhất, dừng ở kết quả không bị huỷ."""
        dem = 0
        for (du_lieu,) in self._db.execute(
                "SELECT du_lieu FROM su_kien WHERE du_an=? AND bead_id=? AND loai='cham_cot.ket_qua'"
                " ORDER BY id DESC", (du_an, bead_id)):
            if not json.loads(du_lieu).get("huy"):
                break
            dem += 1
        return dem

    def doc_anh_decision(self, du_an: str) -> dict[str, list] | None:
        """None = dự án chưa từng lưu ảnh (lượt đầu); {} = đã lưu, không có decision."""
        h = self._db.execute("SELECT du_lieu FROM anh_decision WHERE du_an=?", (du_an,)).fetchone()
        return json.loads(h[0]) if h else None

    def luu_anh_decision(self, du_an: str, anh: dict[str, list],
                         yeu_cau: list[tuple[str, dict]]) -> list[int]:
        """Một giao dịch: mỗi (bead_id, du_lieu) → sự kiện `cham_cot.can_cham_lai {nguon: "decision", …}`
        + yêu cầu; rồi lưu ảnh. Crash giữa chừng thì ảnh cũ còn nguyên, lượt sau phát hiện lại."""
        luc, ids = bay_gio(), []
        with self._db:
            for bead_id, du_lieu in yeu_cau:
                cur = self._db.execute(
                    "INSERT INTO su_kien (luc, du_an, bead_id, loai, tac_nhan, du_lieu) VALUES (?,?,?,?,?,?)",
                    (luc, du_an, bead_id, LOAI_CAN_CHAM_LAI, "tram/cham-cot",
                     json.dumps({**du_lieu, "nguon": "decision"}, ensure_ascii=False, sort_keys=True)))
                ids.append(cur.lastrowid)
                self._db.execute(
                    "INSERT INTO yeu_cau_cham_lai (du_an, bead_id, nguon_id, nguon) VALUES (?,?,?,'decision')",
                    (du_an, bead_id, cur.lastrowid))
            self._db.execute(
                "INSERT INTO anh_decision (du_an, du_lieu) VALUES (?, ?)"
                " ON CONFLICT(du_an) DO UPDATE SET du_lieu=excluded.du_lieu",
                (du_an, json.dumps(anh, ensure_ascii=False, sort_keys=True)))
        return ids
