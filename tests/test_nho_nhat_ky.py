import sqlite3

from tram.nho.nhat_ky import NhatKy


def test_moc_bat_dau_0_va_khong_lui(tmp_path):
    nk = NhatKy(tmp_path / "nho" / "nhat-ky.db")
    assert nk.moc() == 0
    nk.dat_moc(7)
    nk.dat_moc(3)
    assert nk.moc() == 7


def test_bat_dau_giu_ke_hoach_va_phat_lai_khong_ghi_de(tmp_path):
    nk = NhatKy(tmp_path / "nk.db")
    tt = nk.bat_dau("12:1", 12, {"du_an": "hr", "bead_id": "hr-1", "buoc": [{"a": 1}]})
    assert tt.trang_thai == "dang" and tt.ke_hoach["buoc"] == [{"a": 1}] and tt.buoc_xong == frozenset()
    nk.bat_dau("12:1", 12, {"du_an": "hr", "bead_id": "hr-1", "buoc": [{"a": 2}]})
    assert nk.lay("12:1").ke_hoach["buoc"] == [{"a": 1}]
    assert nk.moc() == 0 and [t.ma for t in nk.dang_do()] == ["12:1"]


def test_danh_dau_buoc_va_hoan_tat_tien_moc_cung_giao_dich(tmp_path):
    nk = NhatKy(tmp_path / "nk.db")
    nk.bat_dau("12:1", 12, {"buoc": []})
    nk.danh_dau_buoc("12:1", "0")
    nk.danh_dau_buoc("12:1", "0")
    nk.danh_dau_buoc("12:1", "1")
    assert nk.lay("12:1").buoc_xong == {"0", "1"}
    nk.hoan_tat("12:1", 12)
    assert nk.lay("12:1").trang_thai == "xong" and nk.moc() == 12 and nk.dang_do() == []


def test_bo_su_kien_tien_moc(tmp_path):
    nk = NhatKy(tmp_path / "nk.db")
    nk.hoan_tat("20:1", 20, "bo")
    assert nk.lay("20:1").trang_thai == "bo" and nk.moc() == 20


def test_mo_lai_doc_duoc_va_sao_luu(tmp_path):
    p = tmp_path / "nk.db"
    nk = NhatKy(p)
    nk.bat_dau("5:1", 5, {"buoc": [1]})
    nk.hoan_tat("4:1", 4)
    nk.close()
    nk = NhatKy(p)
    assert nk.moc() == 4 and [t.ma for t in nk.dang_do()] == ["5:1"]
    nk.sao_luu(tmp_path / "ban.db")
    assert sqlite3.connect(tmp_path / "ban.db").execute("SELECT gia_tri FROM moc").fetchone() == (4,)
