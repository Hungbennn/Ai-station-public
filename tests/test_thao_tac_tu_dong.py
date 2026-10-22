"""TM-1: thao tác ghi dashboard của tự merge / tự deploy — lưu cài đặt (kiểm `expected_version`, `bat_ghi`, lệnh),
TẠM DỪNG / Tiếp tục dự án và toàn trạm (không kiểm phiên bản, như estop — D78). Idempotent theo `ma_thao_tac`."""
from dataclasses import replace

import pytest

from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.thao_tac.tu_dong import luu_cai_dat_thao_tac, tam_dung_thao_tac
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import DU_AN_TRAM, LOAI_CAI_DAT, doc_cai_dat, tam_dung_cua

BAT = replace(MAC_DINH, tu_merge=True)


def _kho(tmp_path):
    db = tmp_path / "sk.db"
    return KhoSuKien(db), KhoThaoTac(db)


def _luu(k, kt, cd=BAT, *, ma="ma-luu-00001", ev="0", bat_ghi=True):
    return luu_cai_dat_thao_tac(k, kt, "repo-nhap", cd, bat_ghi=bat_ghi, ma=ma, expected_version=ev)


def test_luu_mot_lan_theo_ma(tmp_path):
    """Scenario "Gửi lại cùng mã thao tác": kết quả lần đầu, lịch sử một dòng."""
    k, kt = _kho(tmp_path)
    a = _luu(k, kt)
    b = _luu(k, kt)
    cd, pb = doc_cai_dat(k.db, "repo-nhap")
    assert cd == BAT and a.ket_qua == b.ket_qua == {"tu_dong.cai_dat": {"phien_ban": pb}}
    assert (a.lap_lai, b.lap_lai) == (False, True)
    ds = k.gan_day("repo-nhap", LOAI_CAI_DAT, 10)
    assert len(ds) == 1 and ds[0].tac_nhan == "dai-ca/dashboard" and ds[0].du_lieu["ma_thao_tac"] == "ma-luu-00001"


def test_cung_ma_khac_noi_dung_va_phien_ban_cu_la_xung_dot(tmp_path):
    k, kt = _kho(tmp_path)
    _luu(k, kt)
    with pytest.raises(XungDot):
        _luu(k, kt, MAC_DINH)                                           # cùng mã, nội dung khác
    with pytest.raises(XungDot, match="đã đổi"):
        _luu(k, kt, replace(BAT, dk_ci=False), ma="ma-luu-00002")       # Scenario "Màn hình cũ": phiên bản "0" đã cũ
    assert doc_cai_dat(k.db, "repo-nhap")[0] == BAT and kt.lay("ma-luu-00002") is None    # 409 không để bản ghi treo


def test_khong_doi_gi_tra_phien_ban_hien_hanh(tmp_path):
    k, kt = _kho(tmp_path)
    pb = _luu(k, kt).ket_qua["tu_dong.cai_dat"]["phien_ban"]
    kq = _luu(k, kt, ma="ma-luu-00003", ev=pb)
    assert kq.ket_qua == {"tu_dong.cai_dat": {"phien_ban": pb}} and len(k.gan_day("repo-nhap", LOAI_CAI_DAT, 9)) == 1


@pytest.mark.parametrize("cd, bat_ghi, loi", [
    (BAT, False, "chỉ quét thử"),                                                          # Scenario "Dự án chỉ quét thử"
    (replace(MAC_DINH, tu_deploy=True, lenh_deploy="d.sh"), True, "Chưa khai đủ 3 lệnh"),
    (replace(MAC_DINH, lenh_kiem_song="curl -H 'Authorization: Bearer " + "q8W" * 12 + "' https://x.vn"), True,
     "Lệnh kiểm còn sống: Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"),                # Scenario "Dán token…"
])
def test_tu_choi_khong_luu_khong_ghi_thao_tac(tmp_path, cd, bat_ghi, loi):
    k, kt = _kho(tmp_path)
    with pytest.raises(KhongHopLe, match=loi):
        _luu(k, kt, cd, bat_ghi=bat_ghi)
    assert k.gan_day("repo-nhap", LOAI_CAI_DAT, 9) == [] and kt.lay("ma-luu-00001") is None    # không lưu, không lịch sử


def test_tam_dung_tiep_tuc_khong_kiem_phien_ban(tmp_path):
    """Scenario "Tạm dừng rồi tiếp tục": tạm dừng không hỏng vì màn hình cũ; công tắc giữ nguyên."""
    k, kt = _kho(tmp_path)
    _luu(k, kt)
    a = tam_dung_thao_tac(k, kt, "repo-nhap", tam_dung=True, ma="ma-td-000001", expected_version="man-hinh-cu")
    b = tam_dung_thao_tac(k, kt, "repo-nhap", tam_dung=True, ma="ma-td-000001", expected_version="khac")
    assert a.ket_qua == {"tu_dong.tam_dung": True} and b.lap_lai and tam_dung_cua(k.db, "repo-nhap").boi == "dai-ca/dashboard"
    assert k.gan_day("repo-nhap", "tu_dong.tam_dung", 9)[0].du_lieu == {"ma_thao_tac": "ma-td-000001"}
    tam_dung_thao_tac(k, kt, "repo-nhap", tam_dung=False, ma="ma-tt-000001", expected_version="x")
    assert tam_dung_cua(k.db, "repo-nhap") is None and doc_cai_dat(k.db, "repo-nhap")[0] == BAT


def test_tam_dung_toan_tram(tmp_path):
    k, kt = _kho(tmp_path)
    tam_dung_thao_tac(k, kt, DU_AN_TRAM, tam_dung=True, ma="ma-tram-0001", expected_version="")
    assert tam_dung_cua(k.db, DU_AN_TRAM) is not None and tam_dung_cua(k.db, "repo-nhap") is None
    kq = tam_dung_thao_tac(k, kt, DU_AN_TRAM, tam_dung=True, ma="ma-tram-0002", expected_version="")
    assert kq.ket_qua == {"tu_dong.tam_dung": False}                       # đã tạm dừng: không ghi thêm
    assert len(k.gan_day(DU_AN_TRAM, "tu_dong.tam_dung", 9)) == 1
