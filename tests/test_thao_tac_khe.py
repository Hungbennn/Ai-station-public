from datetime import timedelta

import pytest

from kho_phieu_gia import LUC, kho_tam
from tram.phieu.cau_dao import ngat_cau_dao, trang_thai_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe, khe_dang_bat, phien_ban_khe
from tram.thao_tac.chay import YeuCau, digest
from tram.thao_tac.khe import bat_khe_thao_tac, dong_cau_dao_thao_tac, tat_khe_thao_tac
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongThay, XungDot

KHE = "B/claude-1"


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "1", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
    return kho, KhoThaoTac(tmp_path / "su-kien.db")


def _su_kien(kho, loai):
    return kho.db.execute("SELECT du_lieu, tac_nhan FROM su_kien WHERE loai = ?", (loai,)).fetchall()


def test_tat_khe_mot_lan_theo_ma_khong_kiem_version(tmp_path):
    kho, kt = _kho(tmp_path)
    a = tat_khe_thao_tac(kho, kt, KHE, vi_sao=" để dành ", ma="ma-tat-0001", expected_version="cu", luc=LUC)
    b = tat_khe_thao_tac(kho, kt, KHE, vi_sao="để dành", ma="ma-tat-0001", expected_version="khac", luc=LUC)
    assert (a.lap_lai, b.lap_lai, khe_dang_bat(kho, KHE)) == (False, True, False)
    assert _su_kien(kho, "khe.tat") == [('{"khe_id": "B/claude-1", "ma_thao_tac": "ma-tat-0001", "vi_sao": "để dành"}',
                                         "dai-ca/dashboard")]
    with pytest.raises(XungDot):
        tat_khe_thao_tac(kho, kt, KHE, vi_sao="khác", ma="ma-tat-0001", expected_version="", luc=LUC)
    with pytest.raises(KhongThay):
        tat_khe_thao_tac(kho, kt, "B/claude-9", vi_sao="", ma="ma-tat-0002", expected_version="", luc=LUC)


def test_bat_khe_kiem_version(tmp_path):
    kho, kt = _kho(tmp_path)
    tat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-tat-0001", expected_version="", luc=LUC)
    with pytest.raises(XungDot):
        bat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-bat-0001", expected_version="0:0", luc=LUC)
    bat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-bat-0002", expected_version=phien_ban_khe(kho, KHE), luc=LUC)
    assert khe_dang_bat(kho, KHE)
    # Crash sau tạo thao tác, trước ghi sự kiện; CLI tắt khe trong khoảng đó.
    cu = phien_ban_khe(kho, KHE)
    yc = YeuCau("ma-bat-0003", "khe.bat", "_tram", KHE, {"vi_sao": ""}, cu)
    kt.tao(yc.ma, loai=yc.loai, du_an=yc.du_an, bead_id=KHE, digest=digest(yc), expected_version=cu)
    with kho.giao_dich():
        bat_tat_khe(kho, KHE, bat=False, vi_sao="giữ hạn mức", tac_nhan="dai-ca/cli", luc=LUC)
    for version in (cu, phien_ban_khe(kho, KHE)):
        with pytest.raises(XungDot):
            bat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma=yc.ma, expected_version=version, luc=LUC)
    assert not khe_dang_bat(kho, KHE)


def test_dong_cau_dao_chi_khi_dang_ngat(tmp_path):
    kho, kt = _kho(tmp_path)
    with pytest.raises(XungDot, match="đang đóng"):
        dong_cau_dao_thao_tac(kho, kt, KHE, ma="ma-dao-0001", expected_version=phien_ban_khe(kho, KHE), luc=LUC)
    with kho.giao_dich():
        ngat_cau_dao(kho, KHE, ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    kq = dong_cau_dao_thao_tac(kho, kt, KHE, ma="ma-dao-0002", expected_version=phien_ban_khe(kho, KHE), luc=LUC)
    assert kq.ket_qua == {"khe.cau_dao_dong": True} and not trang_thai_cau_dao(kho, KHE, LUC).ngat
    assert '"ly_do": "dai-ca"' in _su_kien(kho, "khe.cau_dao_dong")[0][0]


def test_crash_sau_khi_ghi_su_kien_khong_ghi_lan_hai(tmp_path):
    kho, kt = _kho(tmp_path)
    yc = YeuCau("ma-tat-0009", "khe.tat", "_tram", KHE, {"vi_sao": ""}, "")
    kt.tao(yc.ma, loai=yc.loai, du_an=yc.du_an, bead_id=yc.bead_id, digest=digest(yc), expected_version="")
    with kho.giao_dich():
        bat_tat_khe(kho, KHE, bat=False, vi_sao="", tac_nhan="dai-ca/dashboard", luc=LUC,
                    them={"ma_thao_tac": "ma-tat-0009"})
    kq = tat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-tat-0009", expected_version="", luc=LUC)
    assert kq.lap_lai is False and len(_su_kien(kho, "khe.tat")) == 1
