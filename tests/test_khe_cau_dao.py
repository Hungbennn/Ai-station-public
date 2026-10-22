from datetime import timedelta

import pytest

from kho_phieu_gia import LUC, kho_tam
from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhThoTram
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.cau_dao import (dong_cau_dao, dong_cau_dao_het_gio, ngat_cau_dao, toi_luc_het_han_muc,
                                trang_thai_cau_dao, xet_sau_chay)
from tram.phieu.kho import chuoi_gio
from tram.phieu.khe import (KheLa, bat_tat_khe, cac_khe, con_cho_chay, dang_ky_khe, dang_mat_ket_noi,
                            khe_dang_bat)
from tram.phieu.nhip_tim import doc_nhip, ghi_nhip, han_muc_hieu_luc

K1 = {"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]}
CH, NG = CauHinhThoTram(), CauHinhHanMuc()


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [K1], luc=LUC)
    return kho


def _chay_xong(kho, ket_thuc, luc=LUC):
    with kho.giao_dich():
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/claude-1", "ket_thuc": ket_thuc}, luc=luc, bead_id="b")
        return xet_sau_chay(kho, "B/claude-1", ket_thuc, reset_luc=None, han_muc=None, bay_gio=luc, ch=CH, nguong=NG)


def test_dang_ky_khong_cap_quyen_va_khong_ghi_lai_khi_khong_doi(tmp_path):
    kho = _kho(tmp_path)
    assert not khe_dang_bat(kho, "B/claude-1") and not khe_dang_bat(kho, "B/claude-9")
    with kho.giao_dich():
        assert dang_ky_khe(kho, "B", [K1], luc=LUC) == ["B/claude-1"]
        dang_ky_khe(kho, "B", [{**K1, "vai_uu_tien": ["qc"]}], luc=LUC)
    assert kho.db.execute("SELECT COUNT(*) FROM su_kien WHERE loai = 'khe.dang_ky'").fetchone()[0] == 2
    assert cac_khe(kho)["B/claude-1"]["vai_uu_tien"] == ["qc"]


def test_tat_bat_khe(tmp_path):
    kho = _kho(tmp_path)
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=False, vi_sao="để dành hạn mức", tac_nhan="dai-ca", luc=LUC)
    assert not khe_dang_bat(kho, "B/claude-1")
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=True, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    assert khe_dang_bat(kho, "B/claude-1")
    with pytest.raises(KheLa), kho.giao_dich():
        bat_tat_khe(kho, "B/claude-9", bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)


def test_tran_lan_chay_gio_ngay_cua_so_truot(tmp_path):
    kho = _kho(tmp_path)
    for i in range(6):
        kho.db.execute("INSERT INTO lan_chay VALUES (?, 'B/claude-1', 'g', 1, ?)",
                       (f"r{i}", chuoi_gio(LUC - timedelta(minutes=50 - i))))
    assert not con_cho_chay(kho, "B/claude-1", LUC, CH)
    assert con_cho_chay(kho, "B/claude-1", LUC + timedelta(minutes=11), CH)       # lần đầu đã quá 60 phút
    assert not con_cho_chay(kho, "B/claude-1", LUC, CauHinhThoTram(lan_chay_moi_gio=10, lan_chay_moi_ngay=6))


def test_het_han_muc_ngat_toi_reset_roi_tu_dong(tmp_path):
    kho = _kho(tmp_path)
    hm = HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[CuaSo(
        loai="5h", trang_thai="biet", phan_tram=100, reset_luc="2026-10-13T05:00:00Z", doc_luc="2026-10-13T02:59:00Z")])
    assert chuoi_gio(toi_luc_het_han_muc(hm, LUC, reset_luc=None, phut=60, ngung=90)) == "2026-10-13T05:00:00Z"
    assert toi_luc_het_han_muc(None, LUC, reset_luc=None, phut=60, ngung=90) == LUC + timedelta(minutes=60)
    assert _chay_xong(kho, "het_han_muc")
    tt = trang_thai_cau_dao(kho, "B/claude-1", LUC)
    assert tt.ngat and tt.ly_do == "het-han-muc" and tt.toi_luc == "2026-10-13T04:00:00Z"
    assert not _chay_xong(kho, "het_han_muc")                                      # đã ngắt tới cùng giờ
    with kho.giao_dich():
        assert dong_cau_dao_het_gio(kho, LUC + timedelta(minutes=59)) == []
        assert dong_cau_dao_het_gio(kho, LUC + timedelta(minutes=60)) == ["B/claude-1"]
    assert not trang_thai_cau_dao(kho, "B/claude-1", LUC).ngat


def test_ba_lan_loi_he_lien_tiep_moi_ngat_loi_agent_cat_chuoi(tmp_path):
    kho = _kho(tmp_path)
    assert not _chay_xong(kho, "loi_he") and not _chay_xong(kho, "loi_he")
    assert not _chay_xong(kho, "loi")                                              # lỗi do agent cắt chuỗi
    assert not _chay_xong(kho, "loi_he") and not _chay_xong(kho, "loi_he")
    assert _chay_xong(kho, "loi_he")
    assert trang_thai_cau_dao(kho, "B/claude-1", LUC).ly_do == "loi-lien-tiep"
    with kho.giao_dich():
        dong_cau_dao(kho, "B/claude-1", ly_do="dai-ca", luc=LUC, tac_nhan="dai-ca")
    assert not _chay_xong(kho, "loi_he")                                           # đếm lại sau khi đóng


def test_ngat_lau_hon_thi_gia_han(tmp_path):
    kho = _kho(tmp_path)
    with kho.giao_dich():
        assert ngat_cau_dao(kho, "B/claude-1", ly_do="a", toi_luc=LUC + timedelta(minutes=10), luc=LUC)
        assert ngat_cau_dao(kho, "B/claude-1", ly_do="b", toi_luc=LUC + timedelta(minutes=20), luc=LUC)
    assert trang_thai_cau_dao(kho, "B/claude-1", LUC).ly_do == "b"


def test_nhip_tim_ghi_de_va_han_muc_hieu_luc(tmp_path):
    kho = _kho(tmp_path)
    assert doc_nhip(kho, "B/claude-1") is None
    hm = HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[CuaSo(
        loai="5h", trang_thai="biet", phan_tram=40, reset_luc="2026-10-13T05:00:00Z", doc_luc="2026-10-13T02:59:00Z")])
    with kho.giao_dich():
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id="g-1", luot=2, buoc_tho="chay", han_muc=hm)
    n = doc_nhip(kho, "B/claude-1")
    assert (n.giao_id, n.luot, n.buoc_tho, n.han_muc) == ("g-1", 2, "chay", hm)
    assert kho.db.execute("SELECT COUNT(*) FROM nhip_tim").fetchone()[0] == 1
    c = {x.loai: x for x in han_muc_hieu_luc(kho, "B/claude-1", LUC, NG).cua_so}
    assert c["5h"].phan_tram == 40 and c["tuan"].trang_thai == "chua_biet"
    assert han_muc_hieu_luc(kho, "B/claude-1", LUC + timedelta(hours=3), NG).cua_so[0].trang_thai == "chua_biet"


def test_mat_ket_noi_theo_su_kien(tmp_path):
    kho = _kho(tmp_path)
    assert not dang_mat_ket_noi(kho, "B/claude-1")
    with kho.giao_dich():
        kho.ghi_su_kien("_tram", "khe.mat_ket_noi", {"khe_id": "B/claude-1"}, luc=LUC)
    assert dang_mat_ket_noi(kho, "B/claude-1")
