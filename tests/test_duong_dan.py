from datetime import timezone

from tram.duong_dan import bay_gio, doc_luc, goc_repo, tram_home


def test_tram_home_theo_bien_moi_truong(tram_home_tam):
    assert tram_home() == tram_home_tam
    assert tram_home_tam.is_dir()


def test_goc_repo_la_thu_muc_du_an():
    assert (goc_repo() / "pyproject.toml").exists()


def test_doc_luc_chap_nhan_z_va_phan_giay():
    a = doc_luc("2026-10-12T14:10:32Z")
    b = doc_luc("2026-10-12T14:10:32.500Z")
    assert a.tzinfo == timezone.utc
    assert b > a


def test_bay_gio_dang_z():
    s = bay_gio()
    assert s.endswith("Z") and "T" in s
    doc_luc(s)
