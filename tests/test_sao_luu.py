import sqlite3

import pytest

from tram.su_kien.kho import KhoSuKien
from tram.su_kien.sao_luu import sao_luu


def test_sao_luu_co_du_lieu_dang_nam_trong_wal(tmp_path):
    p = tmp_path / "sk.db"
    k = KhoSuKien(p)
    for i in range(3):
        k.ghi("hr", "x", {"i": i})
    dich = sao_luu(p, tmp_path / "sl", luc="2026-10-13T03:15:00Z")
    assert dich.name == "su-kien-20261013T031500Z.db"
    db = sqlite3.connect(dich)
    assert db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 3
    db.close()


def test_giu_n_ban_moi_nhat(tmp_path):
    p = tmp_path / "sk.db"
    KhoSuKien(p).ghi("hr", "x", {})
    for gio in ("01", "02", "03"):
        sao_luu(p, tmp_path / "sl", giu=2, luc=f"2026-10-13T{gio}:00:00Z")
    assert sorted(x.name for x in (tmp_path / "sl").glob("su-kien-*.db")) == [
        "su-kien-20261013T020000Z.db", "su-kien-20261013T030000Z.db"]


def test_khong_co_nguon(tmp_path):
    with pytest.raises(FileNotFoundError):
        sao_luu(tmp_path / "khong.db", tmp_path / "sl")


def test_giu_phai_duong(tmp_path):
    p = tmp_path / "sk.db"
    KhoSuKien(p).ghi("hr", "x", {})
    with pytest.raises(ValueError):
        sao_luu(p, tmp_path / "sl", giu=0)
