import os
import sqlite3

import pytest

from tram.su_kien import mo_an_toan as m


@pytest.mark.parametrize("duoi", ["-wal", "-shm"])
def test_ket_noi_khac_dong_xoa_sidecar_sau_open(tmp_path, monkeypatch, duoi):
    p = tmp_path / "kho.db"
    db = sqlite3.connect(p)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE mau (id INTEGER)")
    db.commit()
    that, thay = m._mo, []

    def mo(ten, dfd, tao):
        fd = that(ten, dfd, tao)
        if ten == p.name + duoi:
            assert fd is not None
            db.close()
            thay.append(os.fstat(fd).st_nlink)
        return fd

    monkeypatch.setattr(m, "_mo", mo)
    try:
        moi = m.mo_da_kiem(p)
        try:
            assert moi.execute("SELECT count(*) FROM mau").fetchone() == (0,)
        finally:
            moi.close()
        assert thay == [0]
    finally:
        db.close()
