import sqlite3
import pytest
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma, bam, TuChoi
from tram.su_kien.phien_ban import LoiPhienBan


def test_ma_chi_luu_bam_va_khoi_phuc(tmp_path):
    p = tmp_path/'passkey.db'
    with mo_kho(p) as db, giao_dich(db):
        u = nguoi(db, 'chu')
        m = cap_ma(db, u, 100, False)
        assert db.execute('select bam,han from ma').fetchone()[:] == (bam(m), 700)
        m2 = cap_ma(db, u, 101, True)
        assert db.execute('select count(*) from ma').fetchone()[0] == 1
        assert db.execute('select loai from tin').fetchone()[0] == 'khoi-phuc'
        assert m != m2
    assert m.encode() not in p.read_bytes()
    with mo_kho(p) as db:
        assert nguoi(db, 'chu')['id'] == u['id']
        with pytest.raises(TuChoi):
            nguoi(db, 'khac')


def test_migration_va_rollback(tmp_path):
    p = tmp_path/'passkey.db'
    with mo_kho(p) as db:
        assert db.execute('pragma user_version').fetchone()[0] == 1
        with pytest.raises(RuntimeError), giao_dich(db):
            nguoi(db, 'chu')
            raise RuntimeError()
        assert db.execute('select count(*) from nguoi').fetchone()[0] == 0
        db.execute('pragma user_version=2')
    with pytest.raises(LoiPhienBan):
        with mo_kho(p):
            pass
