import json
from datetime import datetime, timedelta, timezone

from tram.bao_tin.chong_on import BoChongOn, trong_gio_yen_lang
from tram.bao_tin.tin import Tin, soan_tin

T0 = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)      # 10:00 giờ Việt Nam


def p(phut):
    return T0 + timedelta(minutes=phut)


def test_tin_dau_gui_ngay_cung_loai_gom_mot_tin():
    ra = BoChongOn().nhan([Tin("cho_review", "hr", "hr-1"), Tin("cho_review", "hr", "hr-2"),
                           Tin("co_do", "hr", "hr-1"), Tin("cho_review", "hr", "hr-1")], T0)
    assert [(g.loai, [t.bead_id for t in g.tins]) for g in ra] == [("cho_review", ["hr-1", "hr-2"]),
                                                                   ("co_do", ["hr-1"])]


def test_trong_cua_so_5_phut_thi_gom_den_han():
    bo = BoChongOn()
    bo.nhan([Tin("cho_review", "hr", "hr-1")], T0)
    assert bo.nhan([Tin("cho_review", "hr", "hr-2")], p(1)) == []
    assert bo.nhan([Tin("cho_review", "hr", "hr-3")], p(2)) == []
    assert bo.den_han(p(4)) == []
    ra = bo.den_han(p(5))
    assert len(ra) == 1 and [t.bead_id for t in ra[0].tins] == ["hr-2", "hr-3"]
    assert bo.den_han(p(10)) == []                  # hàng rỗng → đóng cửa sổ
    assert len(bo.nhan([Tin("cho_review", "hr", "hr-4")], p(11))) == 1


def test_khong_gui_lai_cung_loai_bead_trong_1_gio():
    bo = BoChongOn()
    bo.nhan([Tin("co_do", "hr", "hr-1")], T0)
    bo.den_han(p(6))
    assert bo.nhan([Tin("co_do", "hr", "hr-1")], p(30)) == []
    bo.den_han(p(36))
    assert len(bo.nhan([Tin("co_do", "hr", "hr-1")], p(61))) == 1


def test_gio_yen_lang_chi_gui_tram_loi():
    dem = datetime(2026, 10, 12, 17, 30, tzinfo=timezone.utc)   # 00:30 giờ VN
    ra = BoChongOn("23:00-07:00").nhan([Tin("cho_review", "hr", "hr-1"), Tin("tram_loi", "hr")], dem)
    assert [g.loai for g in ra] == ["tram_loi"]
    assert trong_gio_yen_lang("23:00-07:00", dem) and not trong_gio_yen_lang("23:00-07:00", T0)
    assert trong_gio_yen_lang("12:00-14:00", datetime(2026, 10, 13, 6, 0, tzinfo=timezone.utc))   # 13:00 VN
    assert not trong_gio_yen_lang(None, dem)


def test_gio_yen_lang_dau_bang_cuoi_la_khong_yen_lang():
    for gio in range(0, 24, 3):
        luc = T0 + timedelta(hours=gio)
        assert not trong_gio_yen_lang("22:00-22:00", luc) and not trong_gio_yen_lang("00:00-00:00", luc)
    assert trong_gio_yen_lang("22:00-22:01", datetime(2026, 10, 13, 15, 0, 30, tzinfo=timezone.utc))


def test_gui_loi_tra_lai_thi_vong_sau_gui_lai_khong_chan_1_gio():
    bo = BoChongOn()
    (tg,) = bo.nhan([Tin("co_do", "hr", "hr-1"), Tin("co_do", "hr", "hr-2")], T0)
    bo.tra_lai(tg)                                   # Telegram lỗi: xếp lại, xoá dấu "đã gửi"
    ra = bo.den_han(T0 + timedelta(seconds=15))      # vòng sau (15 s) gửi lại cả hai, không chờ 5 phút
    assert [(g.loai, [t.bead_id for t in g.tins]) for g in ra] == [("co_do", ["hr-1", "hr-2"])]
    assert bo.nhan([Tin("co_do", "hr", "hr-1")], p(30)) == []   # lần gửi được mới tính luật 1 giờ


def test_trang_thai_luu_va_nap_lai():
    bo = BoChongOn()
    bo.nhan([Tin("cho_review", "hr", "hr-1")], T0)
    bo.nhan([Tin("cho_review", "hr", "hr-2")], p(1))
    bo2 = BoChongOn(None, json.loads(json.dumps(bo.trang_thai())))
    assert [t.bead_id for t in bo2.den_han(p(5))[0].tins] == ["hr-2"]


def test_soan_tin_khong_co_noi_dung_nghiep_vu():
    s = soan_tin("cho_review", (Tin("cho_review", "hr", "hr-1"), Tin("cho_review", "hr", "hr-2"),
                                Tin("cho_review", "web", "web-1")), "https://may-b.tail.ts.net/")
    assert s == ("[tram] hr · 2 việc chờ review (hr-1, hr-2) · web · 1 việc chờ review (web-1)"
                 " → https://may-b.tail.ts.net/")
    assert soan_tin("estop_bat", (Tin("estop_bat", "_tram"),), None) == "[tram] estop BẬT"
    assert soan_tin("tram_loi", (Tin("tram_loi", "hr", "id lạ;x"),), None) == "[tram] hr · 1 trạm lỗi"
