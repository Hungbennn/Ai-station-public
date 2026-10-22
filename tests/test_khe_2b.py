from datetime import timedelta

from kho_phieu_gia import LUC, kho_tam
from tram.phieu.cau_dao import dong_cau_dao, ngat_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe, khe_dang_bat, phien_ban_khe, su_kien_khe

K1 = {"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]}


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [K1], luc=LUC)
    return kho


def test_bat_tat_khe_mang_them_nhung_khong_de_khoa_chinh(tmp_path):
    kho = _kho(tmp_path)
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=False, vi_sao="để dành", tac_nhan="dai-ca/dashboard", luc=LUC,
                    them={"ma_thao_tac": "ma-tat-0001", "khe_id": "B/khac", "vi_sao": "đè"})
    _, loai, du_lieu, _ = su_kien_khe(kho, "B/claude-1", ("khe.tat",))
    assert loai == "khe.tat" and not khe_dang_bat(kho, "B/claude-1")
    assert du_lieu == {"khe_id": "B/claude-1", "vi_sao": "để dành", "ma_thao_tac": "ma-tat-0001"}
    with kho.giao_dich():                                         # CLI 3a vẫn gọi như cũ
        bat_tat_khe(kho, "B/claude-1", bat=True, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    assert su_kien_khe(kho, "B/claude-1", ("khe.bat",))[2] == {"khe_id": "B/claude-1", "vi_sao": ""}


def test_dong_cau_dao_mang_them_va_phien_ban_khe_doi_theo_su_kien(tmp_path):
    kho = _kho(tmp_path)
    v0 = phien_ban_khe(kho, "B/claude-1")
    assert v0.endswith(":0") and phien_ban_khe(kho, "B/claude-9") == "0:0"
    with kho.giao_dich():
        ngat_cau_dao(kho, "B/claude-1", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    v1 = phien_ban_khe(kho, "B/claude-1")
    with kho.giao_dich():
        dong_cau_dao(kho, "B/claude-1", ly_do="dai-ca", luc=LUC, tac_nhan="dai-ca/dashboard",
                     them={"ma_thao_tac": "ma-dao-0001"})
    x = su_kien_khe(kho, "B/claude-1", ("khe.cau_dao_dong",))
    assert x[2] == {"khe_id": "B/claude-1", "ly_do": "dai-ca", "toi_luc": None, "ma_thao_tac": "ma-dao-0001"}
    assert len({v0, v1, phien_ban_khe(kho, "B/claude-1")}) == 3
