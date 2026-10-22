"""TC Task 3 (spec cong-tac-de-nghi-viec, design D-8, D85, D105): nút "agent tự cập nhật việc" theo dự án lưu bằng
sự kiện `tu_cap_nhat.cai_dat` — mặc định nút dự án tắt, ba nút con bật; đọc lại sau khởi động lại; lịch sử ai đổi,
lúc nào, trước → sau; dùng được với kết nối của tram-api (`KhoSuKien`) lẫn tiến trình giao việc (`KhoPhieu`)."""
import pytest

from tram.de_nghi.cai_dat import (LOAI_CAI_DAT, MAC_DINH, CaiDatTuCapNhat, bat_ghi_an_toan, doc_cai_dat,
                                  doi_cai_dat, lich_su_doi)
from tram.phieu.kho import KhoPhieu
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.loi import XungDot

BAT = CaiDatTuCapNhat(bat=True)


def test_du_an_chua_tung_chinh_thi_mac_dinh(tmp_path):
    """Scenario "Dự án chưa từng chỉnh": nút dự án tắt, ba nút con hiện bật; không loại nào được ghi."""
    kho = KhoSuKien(tmp_path / "sk.db")
    assert doc_cai_dat(kho.db, "repo-nhap") == (MAC_DINH, "0")
    assert (MAC_DINH.bat, MAC_DINH.tien_do, MAC_DINH.viec_moi, MAC_DINH.bi_chan) == (False, True, True, True)
    assert not any(MAC_DINH.cho_ghi(l) for l in ("tien_do", "viec_moi", "bi_chan"))


def test_chi_ghi_khi_ca_nut_du_an_lan_nut_con_bat():
    """Scenario "Chỉ tắt việc mới" (phần mô hình)."""
    cd = CaiDatTuCapNhat(bat=True, viec_moi=False)
    assert cd.cho_ghi("tien_do") and cd.cho_ghi("bi_chan") and not cd.cho_ghi("viec_moi")


def test_ghi_roi_doc_lai_sau_khoi_dong_lai_va_lich_su(tmp_path):
    """Scenario "Khởi động lại trạm": hai nút vẫn bật; lịch sử có tác nhân, giờ, trước và sau."""
    kho = KhoSuKien(tmp_path / "sk.db")
    id1 = doi_cai_dat(kho.db, "repo-nhap", BAT, tac_nhan="dai-ca/dashboard", expected="0", ma_thao_tac="ma-tc-0001")
    assert doi_cai_dat(kho.db, "repo-nhap", BAT, tac_nhan="dai-ca/dashboard") is None          # không đổi gì
    kho.close()
    moi = KhoSuKien(tmp_path / "sk.db")
    assert doc_cai_dat(moi.db, "repo-nhap") == (BAT, str(id1)) and doc_cai_dat(moi.db, "khac") == (MAC_DINH, "0")
    sk = moi.gan_day("repo-nhap", LOAI_CAI_DAT, 5)[0]
    assert sk.du_lieu == {"bat": True, "tien_do": True, "viec_moi": True, "bi_chan": True, "ma_thao_tac": "ma-tc-0001"}
    doi_cai_dat(moi.db, "repo-nhap", CaiDatTuCapNhat(bat=True, viec_moi=False), tac_nhan="dai-ca/dashboard")
    ls = lich_su_doi(moi.db, "repo-nhap")
    assert [d["doi"] for d in ls] == [[{"truong": "viec_moi", "truoc": True, "sau": False}],
                                      [{"truong": "bat", "truoc": False, "sau": True}]]
    assert ls[1]["tac_nhan"] == "dai-ca/dashboard" and ls[1]["luc"]
    assert len(lich_su_doi(moi.db, "repo-nhap", gioi_han=1)) == 1


def test_phien_ban_cu_la_xung_dot_khong_ghi(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    doi_cai_dat(kho.db, "repo-nhap", BAT, tac_nhan="dai-ca/dashboard", expected="0")
    with pytest.raises(XungDot, match="tải lại"):
        doi_cai_dat(kho.db, "repo-nhap", MAC_DINH, tac_nhan="dai-ca/dashboard", expected="0")
    assert doc_cai_dat(kho.db, "repo-nhap")[0] == BAT


def test_doc_qua_kho_phieu_cung_file(tmp_path):
    """Vòng tick và `nhan_bao` đọc qua `KhoPhieu.db` — cùng `su-kien.db` với tram-api."""
    kho = KhoSuKien(tmp_path / "su-kien.db")
    doi_cai_dat(kho.db, "repo-nhap", BAT, tac_nhan="dai-ca/dashboard")
    kp = KhoPhieu(tmp_path / "su-kien.db")
    with kp.giao_dich():
        assert doc_cai_dat(kp.db, "repo-nhap")[0] == BAT


@pytest.mark.parametrize("doc, mong", [(lambda t: True, True), (lambda t: False, False),
                                       (lambda t: "true", False), (lambda t: 1 / 0, None)])
def test_bat_ghi_an_toan(doc, mong):
    """INV-005: đọc `bat_ghi` lỗi (yaml hỏng, sai kiểu, thiếu file) → coi như false."""
    if mong is None:
        with pytest.raises(ZeroDivisionError):
            bat_ghi_an_toan(doc, "x")                       # lỗi lập trình không bị nuốt
        return
    assert bat_ghi_an_toan(doc, "x") is mong
    assert bat_ghi_an_toan(lambda t: (_ for _ in ()).throw(OSError("mất file")), "x") is False
    assert bat_ghi_an_toan(lambda t: (_ for _ in ()).throw(ValueError("sai kiểu")), "x") is False
