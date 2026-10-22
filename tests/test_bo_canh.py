import threading
from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.tram import CauHinhTram
from tram.phieu.canh import bat_dau_canh, mot_vong_canh
from tram.phieu.cau_dao import ngat_cau_dao, trang_thai_cau_dao
from tram.phieu.ghi import gia_han
from tram.phieu.khe import dang_ky_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.su_kien.kho import KhoSuKien

CH = CauHinhTram()


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "1", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
    return kho


def test_mat_ket_noi_sau_90_giay_mot_lan_moi_dot(tmp_path):
    kho = _kho(tmp_path)
    assert mot_vong_canh(kho, bay_gio=LUC, ch=CH)["mat_ket_noi"] == ["B/claude-1"]     # chưa có nhịp nào
    assert mot_vong_canh(kho, bay_gio=LUC, ch=CH)["mat_ket_noi"] == []
    with kho.giao_dich():
        kho.ghi_su_kien("_tram", "khe.ket_noi", {"khe_id": "B/claude-1"}, luc=LUC)
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
    assert mot_vong_canh(kho, bay_gio=LUC + timedelta(seconds=90), ch=CH)["mat_ket_noi"] == []
    assert mot_vong_canh(kho, bay_gio=LUC + timedelta(seconds=91), ch=CH)["mat_ket_noi"] == ["B/claude-1"]


def test_thu_hoi_khi_qua_han_giu_h3(tmp_path):
    kho = _kho(tmp_path)
    p = dat_phieu(kho)
    cuoi = LUC + timedelta(minutes=4)                                   # nhịp tim hợp lệ cuối
    with kho.giao_dich() as db:
        gia_han(db, p.giao_id, han_giu=cuoi + timedelta(minutes=10), nhip=cuoi)
    assert mot_vong_canh(kho, bay_gio=cuoi + timedelta(minutes=10), ch=CH)["thu_hoi"] == []
    ra = mot_vong_canh(kho, bay_gio=cuoi + timedelta(minutes=10, seconds=1), ch=CH)
    assert ra["thu_hoi"] == [p.giao_id] and kho.lay(p.giao_id).ket_thuc == "thu_hoi"
    th = KhoSuKien(tmp_path / "su-kien.db").gan_day("hr-codex", "giao.thu_hoi", 1)[0]
    assert th.du_lieu["ly_do"] == "mat-nhip"


def test_cau_dao_tu_dong_khi_toi_gio(tmp_path):
    kho = _kho(tmp_path)
    with kho.giao_dich():
        ngat_cau_dao(kho, "B/claude-1", ly_do="x", toi_luc=LUC + timedelta(minutes=60), luc=LUC)
    assert mot_vong_canh(kho, bay_gio=LUC + timedelta(minutes=59), ch=CH)["cau_dao_dong"] == []
    assert mot_vong_canh(kho, bay_gio=LUC + timedelta(minutes=60), ch=CH)["cau_dao_dong"] == ["B/claude-1"]
    assert not trang_thai_cau_dao(kho, "B/claude-1", LUC).ngat


def test_vong_lap_song_sot_khi_loi_va_dung_khi_duoc_bao(tmp_path, capsys):
    dung, goi = threading.Event(), []

    def mo_kho():
        goi.append(1)
        if len(goi) == 1:
            raise OSError("đĩa đầy")
        if len(goi) >= 3:
            dung.set()
        return kho_tam(tmp_path)

    t = bat_dau_canh(dung, mo_kho=mo_kho, nap_ch=CauHinhTram, chu_ky=0.01, dong_ho=lambda: LUC)
    t.join(timeout=5)
    assert not t.is_alive() and len(goi) == 3 and "đĩa đầy" in capsys.readouterr().err
