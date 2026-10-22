"""Nhật ký thao tác của memory service — ~/.tram/nho/nhat-ky.db (spec 1b §6.4).

Giữ kết quả tách (kế hoạch ghi có ID ký ức ổn định) TRƯỚC khi áp dụng, các bước đã xong, và mốc `moc_nho`.
Đánh dấu hoàn tất + tiến mốc nằm trong MỘT giao dịch SQLite."""
import json
import sqlite3
from pathlib import Path

from tram.duong_dan import bay_gio
from tram.nho.mo_hinh import ThaoTacNho
from tram.su_kien.ket_noi import mo_ket_noi

LUOC_DO = """
CREATE TABLE IF NOT EXISTS thao_tac (
  ma TEXT PRIMARY KEY,                 -- '<su_kien_id>:<phien_ban_pipeline>'
  su_kien_id INTEGER NOT NULL,
  trang_thai TEXT NOT NULL,            -- 'dang' | 'xong' | 'bo'
  ke_hoach TEXT NOT NULL,              -- JSON {du_an, bead_id, buoc: [BuocGhi.sang_dict()]}
  buoc_xong TEXT NOT NULL DEFAULT '[]',
  luc TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS moc (ten TEXT PRIMARY KEY, gia_tri INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS cap_thang_cap (   -- 1b-3: cặp KHÔNG thăng cấp nữa dù LanceDB không còn dấu vết
  cap TEXT PRIMARY KEY,                       -- '<id nhỏ>|<id lớn>'
  trang_thai TEXT NOT NULL,                   -- 'tu_choi' | 'bo' | 'xoa_cung'
  luc TEXT NOT NULL
);
"""


class NhatKy:
    def __init__(self, duong_dan: Path):
        duong_dan.parent.mkdir(parents=True, exist_ok=True)
        self._db = mo_ket_noi(duong_dan)
        self._db.executescript(LUOC_DO)

    def moc(self) -> int:
        h = self._db.execute("SELECT gia_tri FROM moc WHERE ten='moc_nho'").fetchone()
        return h[0] if h else 0

    def _dat_moc(self, su_kien_id: int) -> None:
        self._db.execute("INSERT INTO moc (ten, gia_tri) VALUES ('moc_nho', ?) ON CONFLICT(ten) DO UPDATE"
                         " SET gia_tri=MAX(gia_tri, excluded.gia_tri)", (su_kien_id,))

    def dat_moc(self, su_kien_id: int) -> None:
        """Sự kiện không phải nguồn ký ức: chỉ tiến mốc (mốc không bao giờ lùi)."""
        with self._db:
            self._dat_moc(su_kien_id)

    def lay(self, ma: str) -> ThaoTacNho | None:
        h = self._db.execute("SELECT ma, su_kien_id, trang_thai, ke_hoach, buoc_xong FROM thao_tac WHERE ma=?",
                             (ma,)).fetchone()
        return None if h is None else ThaoTacNho(h[0], h[1], h[2], json.loads(h[3]), frozenset(json.loads(h[4])))

    def bat_dau(self, ma: str, su_kien_id: int, ke_hoach: dict) -> ThaoTacNho:
        """Lưu kế hoạch trước khi áp dụng. Đã có (phát lại) → giữ bản cũ, không ghi đè."""
        with self._db:
            self._db.execute("INSERT OR IGNORE INTO thao_tac (ma, su_kien_id, trang_thai, ke_hoach, luc)"
                             " VALUES (?, ?, 'dang', ?, ?)",
                             (ma, su_kien_id, json.dumps(ke_hoach, ensure_ascii=False), bay_gio()))
        return self.lay(ma)

    def danh_dau_buoc(self, ma: str, buoc: str) -> None:
        tt = self.lay(ma)
        with self._db:
            self._db.execute("UPDATE thao_tac SET buoc_xong=? WHERE ma=?",
                             (json.dumps(sorted(tt.buoc_xong | {buoc})), ma))

    def hoan_tat(self, ma: str, su_kien_id: int, trang_thai: str = "xong") -> None:
        """`xong` sau khi mọi ký ức đã áp dụng; `bo` khi bỏ sự kiện (nho.loi_tach). Cùng giao dịch với mốc."""
        with self._db:
            self._db.execute("INSERT INTO thao_tac (ma, su_kien_id, trang_thai, ke_hoach, luc) VALUES (?,?,?,?,?)"
                             " ON CONFLICT(ma) DO UPDATE SET trang_thai=excluded.trang_thai",
                             (ma, su_kien_id, trang_thai, "{}", bay_gio()))
            self._dat_moc(su_kien_id)

    def dang_do(self) -> list[ThaoTacNho]:
        return [self.lay(h[0]) for h in
                self._db.execute("SELECT ma FROM thao_tac WHERE trang_thai='dang' ORDER BY su_kien_id")]

    def ghi_cap(self, cap: str, trang_thai: str) -> None:
        with self._db:
            self._db.execute("INSERT OR IGNORE INTO cap_thang_cap (cap, trang_thai, luc) VALUES (?, ?, ?)",
                             (cap, trang_thai, bay_gio()))

    def cac_cap(self) -> dict[str, str]:
        return dict(self._db.execute("SELECT cap, trang_thai FROM cap_thang_cap"))

    def xoa_noi_dung_ke_hoach(self, id_ky_uc: str) -> int:
        """Xoá cứng: kế hoạch đã xong/bỏ còn chép nội dung ký ức — xoá luôn (thao tác dở thì người gọi từ chối
        trước)."""
        so = 0
        with self._db:
            for ma, van_ban in self._db.execute(
                    "SELECT ma, ke_hoach FROM thao_tac WHERE trang_thai != 'dang'").fetchall():
                kh = json.loads(van_ban)
                doi = False
                for b in kh.get("buoc", []):
                    k = b.get("ky_uc", {})
                    if k.get("id") == id_ky_uc and "noi_dung" in k:
                        b["ky_uc"] = {x: k[x] for x in ("id", "pham_vi") if x in k}
                        b["xoa_cung"] = True
                        doi = True
                if doi:
                    self._db.execute("UPDATE thao_tac SET ke_hoach=? WHERE ma=?", (json.dumps(kh), ma))
                    so += 1
        return so

    def sao_luu(self, dich: Path) -> None:
        """Bản chụp nhất quán (online backup API) — gọi khi đang dừng ghi (§6.4)."""
        with sqlite3.connect(dich) as dst:
            self._db.backup(dst)

    def close(self) -> None:
        self._db.close()
