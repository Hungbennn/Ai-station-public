import sqlite3

import pytest

from tram.su_kien.ket_noi import THOI_GIAN_CHO_GIAY, mo_ket_noi
from tram.su_kien.kho import KhoSuKien


def test_ket_noi_wal_va_timeout(tmp_path):
    db = mo_ket_noi(tmp_path / "sk.db")
    assert db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert db.execute("PRAGMA busy_timeout").fetchone()[0] == THOI_GIAN_CHO_GIAY * 1000


def test_doc_dang_mo_khong_chan_ghi(tmp_path):
    p = tmp_path / "sk.db"
    KhoSuKien(p).ghi("hr", "x", {})
    doc = mo_ket_noi(p)
    doc.execute("BEGIN")
    assert doc.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 1
    KhoSuKien(p).ghi("hr", "y", {})          # WAL: giao dịch đọc không khoá người ghi
    doc.execute("COMMIT")
    assert doc.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 2


def test_su_kien_giu_cot_token_qua_mo_hinh_doc(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam"}, bead_id="hr-1",
          token_vao=10, token_ra=5, mo_hinh="m", thoi_gian_ms=7)
    s = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua")
    assert (s.id, s.token_vao, s.token_ra, s.mo_hinh, s.thoi_gian_ms) == (1, 10, 5, "m", 7)
    assert k.gan_day("hr", "cham_cot.ket_qua", 1)[0].token_vao == 10


def test_sau_id_phan_trang(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    for i in range(5):
        k.ghi("hr", "x", {"i": i})
    t1 = k.sau_id(0, 2)
    t2 = k.sau_id(t1[-1].id, 2)
    t3 = k.sau_id(t2[-1].id, 10)
    assert [s.du_lieu["i"] for s in t1 + t2 + t3] == [0, 1, 2, 3, 4]
    assert k.sau_id(5, 10) == []


def test_id_moi_nhat(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    assert k.id_moi_nhat() == 0
    k.ghi("hr", "x", {})
    k.ghi("_tram", "estop.bat", {})
    assert k.id_moi_nhat() == 2


def test_cua_bead_cu_truoc_moi_sau(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "a", {}, bead_id="hr-1")
    k.ghi("hr", "b", {}, bead_id="hr-2")
    k.ghi("hr", "c", {}, bead_id="hr-1")
    k.ghi("web", "d", {}, bead_id="hr-1")
    assert [s.loai for s in k.cua_bead("hr", "hr-1")] == ["a", "c"]
    assert [s.loai for s in k.cua_bead("hr", "hr-1", gioi_han=1)] == ["c"]


def test_yeu_cau_plan_1a_van_dung_chung_ket_noi(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m"}, bead_id="hr-1", tac_nhan="dai-ca/dashboard")
    assert k.yeu_cau.nhan_su_kien_nguon("hr") == 1


def test_close_dong_ket_noi(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.close()
    with pytest.raises(sqlite3.ProgrammingError):
        k.id_moi_nhat()
