"""TM-1: cài đặt tự động và TẠM DỪNG lưu bằng sự kiện trong kho sự kiện (D88, design D-4) — không bảng mới; đọc–so–ghi
trong một giao dịch `BEGIN IMMEDIATE` để ghi của trạm (tiến trình khác) không đè ghi của Đại ca. Hàm nhận kết nối của
`KhoSuKien` (tram-api) lẫn `KhoPhieu` (tiến trình giao việc của TM-2, TM-3)."""
import sqlite3
from dataclasses import replace

import pytest

from tram.phieu.kho import KhoPhieu
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.loi import XungDot
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import (DU_AN_TRAM, LOAI_CAI_DAT, doc_cai_dat, doc_trang_thai, doi_cai_dat, ghi_tam_dung,
                              giao_dich, lich_su_doi, tam_dung_cua)

BAT = replace(MAC_DINH, tu_merge=True)


def _db(tmp_path):
    return KhoSuKien(tmp_path / "sk.db").db


def test_chua_chinh_thi_mac_dinh_phien_ban_0(tmp_path):
    assert doc_cai_dat(_db(tmp_path), "repo-nhap") == (MAC_DINH, "0")


def test_ghi_roi_doc_lai_sau_khi_khoi_dong_lai(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    id_ = doi_cai_dat(k.db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard", expected="0",
                      them={"ma_thao_tac": "ma-cd-0001"})
    k.close()
    k2 = KhoSuKien(tmp_path / "sk.db")                          # trạm khởi động lại: kho mới, cùng file
    assert doc_cai_dat(k2.db, "repo-nhap") == (BAT, str(id_))
    s = k2.gan_day("repo-nhap", LOAI_CAI_DAT, 1)[0]
    assert s.tac_nhan == "dai-ca/dashboard" and s.bead_id is None and s.id == id_
    assert s.du_lieu == {"cai_dat": BAT.phang(), "doi": ["tu_merge"], "ma_thao_tac": "ma-cd-0001"}
    assert doc_cai_dat(k2.db, "hr-codex") == (MAC_DINH, "0")   # dự án khác không đổi


def test_phien_ban_cu_thi_xung_dot_va_khong_ghi(tmp_path):
    db = _db(tmp_path)
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard", expected="0")
    with pytest.raises(XungDot, match="đã đổi"):
        doi_cai_dat(db, "repo-nhap", lambda c: replace(c, lenh_deploy="a.sh"), tac_nhan="dai-ca/dashboard",
                    expected="0")
    assert db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 1 and not db.in_transaction


def test_khong_doi_gi_thi_khong_ghi(tmp_path):
    db = _db(tmp_path)
    assert doi_cai_dat(db, "repo-nhap", lambda c: c, tac_nhan="dai-ca/dashboard", expected="0") is None
    assert db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 0


def test_ghi_cua_tram_ap_tren_ban_moi_nhat_qua_kho_phieu(tmp_path):
    """TM-3 tự tắt tự deploy (tiến trình giao việc, `KhoPhieu.db`, expected=None) không làm mất thay đổi Đại ca vừa
    ghi qua `KhoSuKien.db` — kể cả khi gọi bên trong `KhoPhieu.giao_dich()` của người gọi."""
    k, kp = KhoSuKien(tmp_path / "sk.db"), KhoPhieu(tmp_path / "sk.db")
    doi_cai_dat(k.db, "repo-nhap", lambda _: replace(BAT, tu_deploy=True), tac_nhan="dai-ca/dashboard", expected="0")
    doi_cai_dat(k.db, "repo-nhap", lambda c: replace(c, tu_merge=False), tac_nhan="dai-ca/dashboard",
                expected=doc_cai_dat(k.db, "repo-nhap")[1])
    with kp.giao_dich():
        doi_cai_dat(kp.db, "repo-nhap", lambda c: replace(c, tu_deploy=False), tac_nhan="tram/tu-deploy",
                    them={"ly_do": "hong-3-lan"})
        assert ghi_tam_dung(kp.db, "repo-nhap", tam_dung=True, tac_nhan="tram/tu-deploy", them={"ly_do": "lui-hong"})
    cd, _ = doc_cai_dat(k.db, "repo-nhap")
    assert (cd.tu_merge, cd.tu_deploy) == (False, False) and tam_dung_cua(k.db, "repo-nhap").ly_do == "lui-hong"
    assert k.gan_day("repo-nhap", LOAI_CAI_DAT, 1)[0].du_lieu["ly_do"] == "hong-3-lan"


def test_giao_dich_loi_thi_khong_ghi_gi(tmp_path):
    db = _db(tmp_path)

    def hong(_):
        raise RuntimeError("giữa giao dịch")
    with pytest.raises(RuntimeError):
        doi_cai_dat(db, "repo-nhap", hong, tac_nhan="dai-ca/dashboard")
    assert not db.in_transaction and db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 0
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard")      # kết nối vẫn dùng được


def test_giao_dich_giu_khoa_ghi_voi_tien_trinh_khac(tmp_path):
    db = _db(tmp_path)
    khac = sqlite3.connect(tmp_path / "sk.db", timeout=0.1)
    with giao_dich(db):
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            khac.execute("BEGIN IMMEDIATE")
    khac.execute("BEGIN IMMEDIATE")
    khac.rollback()


def test_lich_su_doi_hai_dong_moi_nhat_truoc(tmp_path):
    """Scenario "Xem lịch sử đổi": bật rồi tắt → hai dòng, ai đổi, giờ, trước/sau."""
    db = _db(tmp_path)
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard")
    doi_cai_dat(db, "repo-nhap", lambda _: MAC_DINH, tac_nhan="dai-ca/dashboard")
    ls = lich_su_doi(db, "repo-nhap")
    assert [d["doi"] for d in ls] == [[{"truong": "tu_merge", "truoc": True, "sau": False}],
                                      [{"truong": "tu_merge", "truoc": False, "sau": True}]]
    assert {d["tac_nhan"] for d in ls} == {"dai-ca/dashboard"} and all(d["luc"] for d in ls)
    assert lich_su_doi(db, "repo-nhap", gioi_han=1) == ls[:1]                # dòng cũ nhất bị cắt vẫn so đúng bản trước


def test_tam_dung_du_an_va_toan_tram_doc_lap(tmp_path):
    db = _db(tmp_path)
    assert tam_dung_cua(db, "repo-nhap") is None
    assert ghi_tam_dung(db, "repo-nhap", tam_dung=True, tac_nhan="dai-ca/dashboard", them={"ma_thao_tac": "m1-aaaa"})
    assert not ghi_tam_dung(db, "repo-nhap", tam_dung=True, tac_nhan="dai-ca/dashboard")      # đã tạm dừng: không ghi
    td = tam_dung_cua(db, "repo-nhap")
    assert td.boi == "dai-ca/dashboard" and td.luc and td.ly_do == ""
    assert tam_dung_cua(db, DU_AN_TRAM) is None and tam_dung_cua(db, "hr-codex") is None
    ghi_tam_dung(db, DU_AN_TRAM, tam_dung=True, tac_nhan="tram/tu-deploy", them={"ly_do": "lui-hong"})
    assert tam_dung_cua(db, DU_AN_TRAM).ly_do == "lui-hong"
    assert ghi_tam_dung(db, "repo-nhap", tam_dung=False, tac_nhan="dai-ca/dashboard")
    assert tam_dung_cua(db, "repo-nhap") is None and not ghi_tam_dung(db, "hr-codex", tam_dung=False, tac_nhan="x")
    assert [h[0] for h in db.execute("SELECT loai FROM su_kien ORDER BY id")] == [
        "tu_dong.tam_dung", "tu_dong.tam_dung", "tu_dong.tiep_tuc"]


def test_doc_trang_thai_gom_mot_lan(tmp_path):
    db = _db(tmp_path)
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard")
    ghi_tam_dung(db, DU_AN_TRAM, tam_dung=True, tac_nhan="dai-ca/dashboard")
    tt = doc_trang_thai(db, "repo-nhap")
    assert tt.cai_dat == BAT and tt.phien_ban == doc_cai_dat(db, "repo-nhap")[1]
    assert tt.tam_dung_du_an is None and tt.tam_dung_tram.boi == "dai-ca/dashboard"
