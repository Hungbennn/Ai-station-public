"""Bảng sự cố 4D-0 (plan 4d 4D-1b), một tiến trình, đồng hồ giả: mỗi cửa sổ trước/sau giữ chỗ, trước/sau `bd create`,
trước/sau ghi sổ. Bất biến: `bd create` gọi nhiều nhất một lần cho một mã; `khong_ro` chỉ đối soát, không tạo lại."""
import pytest
from yeu_cau_gia import BI_MAT, LOGIN, MA, BdTep, DongHo, giu_cho, yc

from tram.yeu_cau.dich_vu import HAN_GIAY, tiep_nhan
from tram.yeu_cau.so_nhan import SoNhan


def gui(so, bd, dh, **sua):
    return tiep_nhan(so, bd, yc(**sua), nguoi_gui=LOGIN, dong_ho=dh)


@pytest.fixture
def so(tmp_path):
    return SoNhan(tmp_path / "sk.db")


def test_chet_giua_giu_cho_va_create(so, tmp_path):
    bd, dh = BdTep(tmp_path), DongHo()
    giu_cho(so, han=dh.t + HAN_GIAY)
    assert gui(so, bd, dh).trang_thai == "dang_xu_ly" and bd.so_lan_tao() == 0
    dh.t += HAN_GIAY + 1
    kq = gui(so, bd, dh)
    assert (kq.trang_thai, kq.bead_id, bd.so_lan_tao()) == ("da_tao", "hr-f1", 1)


def test_chet_sau_khi_goi_create_chua_ro_khong_tao_lai_ke_ca_qua_han(so, tmp_path):
    bd, dh = BdTep(tmp_path), DongHo()
    giu_cho(so, han=dh.t + HAN_GIAY)
    so.bat_dau_tao(MA, chu="chet", han=dh.t + HAN_GIAY)
    assert gui(so, bd, dh).trang_thai == "dang_xu_ly"
    for _ in range(3):
        dh.t += 10 * HAN_GIAY
        kq = gui(so, bd, dh)
        assert (kq.trang_thai, kq.ly_do) == ("khong_ro", "chua_thay")
    assert bd.so_lan_tao() == 0 and so.lay(MA).lan_doi_soat == 3


def test_beads_da_ghi_nhung_so_chua_ghi_thi_doi_soat_ra_feature(so, tmp_path):
    bd, dh = BdTep(tmp_path), DongHo()
    giu_cho(so, han=dh.t + HAN_GIAY)
    so.bat_dau_tao(MA, chu="chet", han=dh.t + HAN_GIAY)
    bid = bd.them_dau()                                   # create đã commit, tiến trình chết trước khi ghi sổ
    dh.t += HAN_GIAY + 1
    assert (gui(so, bd, dh).trang_thai, so.lay(MA).bead_id) == ("da_co", bid)
    assert gui(so, bd, dh).bead_id == bid and bd.so_lan_tao() == 0


def test_timeout_roi_commit_tre_chi_doi_soat_khong_tao_lan_hai(so, tmp_path):
    bd, dh = BdTep(tmp_path, su_co=("truoc_ghi", "loi")), DongHo()
    kq, bn = gui(so, bd, dh), so.lay(MA)
    assert (kq.trang_thai, kq.ly_do, bn.trang_thai, bn.ly_do) == ("khong_ro", "chua_thay", "khong_ro", "bd_loi")
    for _ in range(3):
        dh.t += 10 * HAN_GIAY
        assert gui(so, bd, dh).trang_thai == "khong_ro"
    bid = bd.them_dau()                                   # transaction treo của lần đầu commit trễ
    assert (gui(so, bd, dh).trang_thai, so.lay(MA).bead_id) == ("da_co", bid)
    assert bd.so_lan_tao() == 1 and len(bd.tat_ca()) == 1


def test_bd_bao_loi_sau_khi_da_ghi_thi_doi_soat_ngay(so, tmp_path):
    bd, dh = BdTep(tmp_path, su_co=("sau_ghi", "loi")), DongHo()
    kq = gui(so, bd, dh)
    assert (kq.trang_thai, kq.bead_id, bd.so_lan_tao(), so.lay(MA).trang_thai) == ("da_co", "hr-f1", 1, "da_tao")


def test_loi_la_cua_bd_la_khong_ro_va_khong_lo_chi_tiet(so, tmp_path):
    bd, dh = BdTep(tmp_path, su_co=("truoc_ghi", "la")), DongHo()
    kq = gui(so, bd, dh)
    assert (kq.trang_thai, kq.ly_do, so.lay(MA).ly_do) == ("khong_ro", "chua_thay", "bd_khong_ro")
    assert BI_MAT not in repr(kq) and BI_MAT not in repr(so.lay(MA))
    dh.t += 10 * HAN_GIAY
    assert gui(so, bd, dh).trang_thai == "khong_ro" and bd.so_lan_tao() == 1


@pytest.mark.parametrize("cach", ["loi", "la"])               # LoiBd, hoặc lỗi lạ (vd giải mã đầu ra bd)
def test_doc_bd_loi_truoc_khi_tao_thi_chua_tao_va_tra_cho(so, tmp_path, cach):
    bd, dh = BdTep(tmp_path, su_co=("doc", cach)), DongHo()
    kq = gui(so, bd, dh)
    assert (kq.trang_thai, kq.ly_do, bd.so_lan_tao()) == ("chua_tao", "doc_bd_loi", 0)
    assert (so.lay(MA).trang_thai, so.lay(MA).han) == ("nhan", 0)
    assert gui(so, bd, dh).trang_thai == "da_tao" and bd.so_lan_tao() == 1


def test_doc_bd_loi_luc_doi_soat_khong_ro_van_khong_tao(so, tmp_path):
    bd, dh = BdTep(tmp_path), DongHo()
    giu_cho(so, han=dh.t + HAN_GIAY)
    so.bat_dau_tao(MA, chu="chet", han=dh.t + HAN_GIAY)
    bd.su_co = ("doc", "loi")
    dh.t += HAN_GIAY + 1
    assert (gui(so, bd, dh).ly_do, gui(so, bd, dh).ly_do) == ("doc_bd_loi", "chua_thay")
    assert bd.so_lan_tao() == 0


def test_bead_mang_dau_co_san_thi_khong_tao(so, tmp_path):
    bd, dh = BdTep(tmp_path), DongHo()
    bid = bd.them_dau()                                   # sổ mất/khôi phục bản cũ, bead đã có
    assert (gui(so, bd, dh).trang_thai, bd.so_lan_tao(), so.lay(MA).bead_id) == ("da_co", 0, bid)


def test_nhieu_feature_cung_dau_khong_chon_bua(so, tmp_path):
    bd, dh = BdTep(tmp_path), DongHo()
    bd.them_dau()
    bd.them_dau()
    kq = gui(so, bd, dh)
    assert (kq.trang_thai, kq.ly_do, kq.bead_id, bd.so_lan_tao()) == ("khong_ro", "nhieu_feature", None, 0)
    assert (so.lay(MA).trang_thai, gui(so, bd, dh).ly_do, bd.so_lan_tao()) == ("khong_ro", "nhieu_feature", 0)


def test_mat_cho_khi_dang_doc_bd_thi_khong_tao(so, tmp_path):
    dh = DongHo()

    class BdCham(BdTep):
        def tat_ca(self):                                 # đọc lâu quá hạn; lần gửi khác giành chỗ đúng lúc đó
            dh.t += HAN_GIAY + 1
            so.gianh(MA, chu="khac", han=dh.t + HAN_GIAY, luc=dh.t)
            return super().tat_ca()
    bd = BdCham(tmp_path)
    assert gui(so, bd, dh).trang_thai == "dang_xu_ly" and bd.so_lan_tao() == 0 and so.lay(MA).chu == "khac"
