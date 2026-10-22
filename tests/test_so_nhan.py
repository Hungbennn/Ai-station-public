"""Sổ tiếp nhận yêu cầu tạo feature (plan 4d 4D-1a): khoá theo mã, mọi lần đổi trạng thái là so-sánh-rồi-đổi, đúng
giữa nhiều kết nối/luồng trên cùng file SQLite. Không `bd`, không mạng."""
import threading

import pytest

from tram.yeu_cau.so_nhan import SoNhan, mo_so_nhan

MA = "yc-" + "a" * 32


def nhan(so, chu="c1", han=100.0, digest="d1"):
    return so.nhan(MA, du_an="hr-codex", digest=digest, nguoi_gui="dai-ca@example.com", chu=chu, han=han)


def test_nhan_mot_lan_va_luu_nguoi_gui(tmp_path):
    so = SoNhan(tmp_path / "sk.db")
    assert nhan(so) is True and nhan(so, chu="c2", digest="khac") is False
    bn = so.lay(MA)
    assert (bn.trang_thai, bn.chu, bn.digest, bn.nguoi_gui, bn.han) == ("nhan", "c1", "d1", "dai-ca@example.com", 100.0)
    assert so.lay("yc-" + "b" * 32) is None


def test_chi_chu_hien_tai_bat_dau_tao_va_chi_mot_lan(tmp_path):
    so = SoNhan(tmp_path / "sk.db")
    nhan(so)
    assert so.bat_dau_tao(MA, chu="la", han=200.0) is False
    assert so.bat_dau_tao(MA, chu="c1", han=200.0) is True
    assert so.bat_dau_tao(MA, chu="c1", han=300.0) is False and so.lay(MA).han == 200.0


def test_gianh_chi_khi_nhan_qua_han_va_chu_cu_mat_quyen(tmp_path):
    so = SoNhan(tmp_path / "sk.db")
    nhan(so, han=100.0)
    assert so.gianh(MA, chu="c2", han=500.0, luc=99.0) is False
    assert so.gianh(MA, chu="c2", han=500.0, luc=101.0) is True
    assert so.bat_dau_tao(MA, chu="c1", han=600.0) is False and so.bat_dau_tao(MA, chu="c2", han=600.0) is True
    assert so.gianh(MA, chu="c3", han=900.0, luc=10_000.0) is False          # đã gọi bd: không ai giành được nữa


def test_nha_cho_gianh_ngay(tmp_path):
    so = SoNhan(tmp_path / "sk.db")
    nhan(so, han=100.0)
    assert so.nha(MA, chu="la") is False and so.nha(MA, chu="c1") is True
    assert so.gianh(MA, chu="c2", han=500.0, luc=1.0) is True


def test_khong_ro_chi_chu_dua_vao_va_khong_quay_lai_nhan(tmp_path):
    so = SoNhan(tmp_path / "sk.db")
    nhan(so)
    so.bat_dau_tao(MA, chu="c1", han=200.0)
    assert so.het_han(MA, luc=150.0) is False and so.chu_bao_loi(MA, chu="la", ly_do="x") is False
    assert so.doi_soat(MA) is False and so.het_han(MA, luc=201.0) is True
    bn = so.lay(MA)
    assert (bn.trang_thai, bn.ly_do, bn.chu, bn.han) == ("khong_ro", "het_han", None, None)
    assert so.gianh(MA, chu="c9", han=1e12, luc=1e12) is False and so.bat_dau_tao(MA, chu="c9", han=1.0) is False
    assert so.doi_soat(MA) and so.doi_soat(MA)
    assert (so.lay(MA).lan_doi_soat, so.lay(MA).ly_do) == (2, "het_han")                # giữ lý do gốc
    ma2 = "yc-" + "c" * 32                                  # thấy nhiều feature trước khi tạo: `nhan` → `khong_ro`
    so.nhan(ma2, du_an="hr-codex", digest="d", nguoi_gui="x", chu="c1", han=1.0)
    assert so.chu_bao_loi(ma2, chu="la", ly_do="nhieu_feature") is False
    assert so.chu_bao_loi(ma2, chu="c1", ly_do="nhieu_feature") and so.lay(ma2).trang_thai == "khong_ro"


def test_da_tao_tu_moi_trang_thai_chua_xong_va_giu_nguyen_sau_do(tmp_path):
    so = SoNhan(tmp_path / "sk.db")
    nhan(so)
    so.bat_dau_tao(MA, chu="c1", han=200.0)
    so.chu_bao_loi(MA, chu="c1", ly_do="bd_loi")
    assert so.da_tao(MA, "hr-f1") is True and so.da_tao(MA, "hr-f2") is False
    bn = so.lay(MA)
    assert (bn.trang_thai, bn.bead_id, bn.ly_do) == ("da_tao", "hr-f1", None)
    assert so.doi_soat(MA) is False and so.het_han(MA, luc=1e12) is False


def test_nhieu_ket_noi_nhieu_luong_chi_mot_nguoi_giu_cho(tmp_path):
    db, kq, cho = tmp_path / "sk.db", [], threading.Barrier(8)
    SoNhan(db).close()

    def chay(i):
        so = SoNhan(db)
        cho.wait()
        kq.append(nhan(so, chu=f"c{i}"))
        kq.append(so.bat_dau_tao(MA, chu=f"c{i}", han=1.0))
        so.close()
    luong = [threading.Thread(target=chay, args=(i,)) for i in range(8)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert kq.count(True) == 2 and SoNhan(db).lay(MA).trang_thai == "dang_tao"


def test_trang_thai_la_bi_chan_o_luoc_do(tmp_path):
    import sqlite3
    so = SoNhan(tmp_path / "sk.db")
    nhan(so)
    with pytest.raises(sqlite3.IntegrityError):
        so._doi("trang_thai='xong'", "1=1", "luc", MA)
    with pytest.raises(sqlite3.IntegrityError):                # NOT NULL: không bị nhầm là "đã có hàng"
        so.nhan("yc-" + "d" * 32, du_an="hr-codex", digest="d", nguoi_gui=None, chu="c", han=1.0)


def test_mo_so_nhan_dung_su_kien_db_trong_tram_home(tram_home_tam):
    so = mo_so_nhan()
    nhan(so)
    so.close()
    assert SoNhan(tram_home_tam / "su-kien.db").lay(MA).trang_thai == "nhan"
