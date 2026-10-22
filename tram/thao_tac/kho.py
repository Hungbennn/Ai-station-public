"""Bảng `thao_tac` trong ~/.tram/su-kien.db: tiến độ từng thao tác ghi của dashboard (spec 2 §12.2, §12.3)."""
import json
from dataclasses import dataclass
from pathlib import Path

from tram.duong_dan import bay_gio, tram_home
from tram.su_kien.ket_noi import mo_kho_su_kien

LUOC_DO = """
CREATE TABLE IF NOT EXISTS thao_tac (
  ma_thao_tac TEXT PRIMARY KEY,
  loai TEXT NOT NULL,
  du_an TEXT NOT NULL,
  bead_id TEXT,
  digest_noi_dung TEXT NOT NULL,
  expected_version TEXT NOT NULL,
  buoc_da_xong TEXT NOT NULL DEFAULT '{}',
  ket_qua TEXT,
  luc TEXT NOT NULL
);
"""
_COT = ("ma_thao_tac, loai, du_an, bead_id, digest_noi_dung, expected_version,"
        " buoc_da_xong, ket_qua, luc")


@dataclass(frozen=True)
class BanGhiThaoTac:
    ma_thao_tac: str
    loai: str
    du_an: str
    bead_id: str | None
    digest_noi_dung: str
    expected_version: str
    buoc_da_xong: dict
    ket_qua: dict | None
    luc: str


class KhoThaoTac:
    def __init__(self, duong_dan: Path):
        self._db = mo_kho_su_kien(duong_dan)
        self._db.executescript(LUOC_DO)

    def lay(self, ma: str) -> BanGhiThaoTac | None:
        h = self._db.execute(f"SELECT {_COT} FROM thao_tac WHERE ma_thao_tac=?", (ma,)).fetchone()
        if h is None:
            return None
        return BanGhiThaoTac(*h[:6], json.loads(h[6]), None if h[7] is None else json.loads(h[7]), h[8])

    def tao(self, ma: str, *, loai: str, du_an: str, bead_id: str | None, digest: str,
            expected_version: str) -> None:
        with self._db:
            self._db.execute(
                "INSERT INTO thao_tac (ma_thao_tac, loai, du_an, bead_id, digest_noi_dung,"
                " expected_version, luc) VALUES (?,?,?,?,?,?,?)",
                (ma, loai, du_an, bead_id, digest, expected_version, bay_gio()))

    def xong_buoc(self, ma: str, buoc: str, gia_tri) -> None:
        with self._db:
            h = self._db.execute("SELECT buoc_da_xong FROM thao_tac WHERE ma_thao_tac=?", (ma,)).fetchone()
            da = json.loads(h[0])
            da[buoc] = gia_tri
            self._db.execute("UPDATE thao_tac SET buoc_da_xong=? WHERE ma_thao_tac=?",
                             (json.dumps(da, ensure_ascii=False), ma))

    def ket_thuc(self, ma: str, ket_qua: dict) -> None:
        with self._db:
            self._db.execute("UPDATE thao_tac SET ket_qua=? WHERE ma_thao_tac=?",
                             (json.dumps(ket_qua, ensure_ascii=False), ma))

    def close(self) -> None:
        self._db.close()


def mo_kho_thao_tac() -> KhoThaoTac:
    return KhoThaoTac(tram_home() / "su-kien.db")
