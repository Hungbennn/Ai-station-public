"""TM-1: giờ yên lặng cho tin tự merge / tự deploy (D98, D99). Tin xấu và tin đổi cài đặt gửi ngay; tin tốt gom
gửi khi hết giờ yên lặng (không mất); "mỗi lần một tin" không bị luật 1 giờ nuốt. Các loại tin cũ giữ hành vi cũ."""
from datetime import datetime, timedelta, timezone

from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.tin import Tin

YEN = "23:00-07:00"
DEM = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)          # 02:00 giờ VN — trong giờ yên lặng
SANG = datetime(2026, 10, 18, 0, 5, tzinfo=timezone.utc)          # 07:05 giờ VN


def _loai(ra):
    return [(g.loai, [(t.du_an, t.bead_id) for t in g.tins]) for g in ra]


def test_tin_xau_va_doi_cai_dat_gui_ngay_trong_gio_yen_lang():
    """Scenario "Hỏng lúc nửa đêm": tin "đã tự lùi" gửi ngay."""
    tins = [Tin("deploy_da_lui", "rn", "hong-1-lan"), Tin("lui_hong", "rn"), Tin("tu_deploy_tu_tat", "rn"),
            Tin("deploy_khong_ro", "rn"), Tin("cai_dat_doi", "rn", "tu-merge-bat"), Tin("cho_review", "rn", "rn-1")]
    assert [g.loai for g in BoChongOn(YEN).nhan(tins, DEM)] == [
        "deploy_da_lui", "lui_hong", "tu_deploy_tu_tat", "deploy_khong_ro", "cai_dat_doi"]
    bo = BoChongOn(YEN)
    for phut in (0, 1, 2):
        assert [g.loai for g in bo.nhan(tins[:5], DEM + timedelta(minutes=phut))] == [
            "deploy_da_lui", "lui_hong", "tu_deploy_tu_tat", "deploy_khong_ro", "cai_dat_doi"]
    assert bo.den_han(DEM + timedelta(minutes=6)) == []


def test_tin_tot_gom_gui_sau_gio_yen_lang_qua_luu_trang_thai():
    """Scenario "Hỏng lúc nửa đêm" vế sau: "deploy xong" lúc 01:00 gom gửi sau giờ yên lặng; tin cũ vẫn bỏ như trước."""
    bo = BoChongOn(YEN)
    assert bo.nhan([Tin("deploy_xong", "rn"), Tin("tu_merge", "rn", "rn-7"), Tin("tu_merge", "rn", "rn-8"),
                    Tin("san_sang_deploy", "rn"), Tin("cho_review", "rn", "rn-1")], DEM) == []
    assert bo.nhan([Tin("tu_merge", "rn", "rn-7")], DEM + timedelta(minutes=30)) == []        # trùng: gom một
    assert bo.den_han(DEM + timedelta(hours=1)) == []                                         # vẫn yên lặng
    bo = BoChongOn(YEN, bo.trang_thai())                                                      # tram-bao-tin chạy lại
    ra = bo.den_han(SANG)
    assert _loai(ra) == [("deploy_xong", [("rn", None)]), ("tu_merge", [("rn", "rn-7"), ("rn", "rn-8")]),
                         ("san_sang_deploy", [("rn", None)])]
    assert bo.den_han(SANG + timedelta(minutes=1)) == [] and bo.trang_thai()["cho_sang"] == []


def test_tin_tot_dang_gom_khi_vao_gio_yen_lang_khong_mat():
    """Tin thứ hai rơi vào cửa sổ 5 phút lúc 22:59, cửa sổ hết hạn lúc 23:04 (đã yên lặng) → hoãn tới sáng."""
    toi = datetime(2026, 10, 17, 15, 57, tzinfo=timezone.utc)                     # 22:57 giờ VN
    bo = BoChongOn(YEN)
    assert len(bo.nhan([Tin("tu_merge", "rn", "rn-1")], toi)) == 1
    assert bo.nhan([Tin("tu_merge", "rn", "rn-2")], toi + timedelta(minutes=2)) == []
    assert bo.den_han(toi + timedelta(minutes=7)) == [] and bo.trang_thai()["cho_sang"] == [["tu_merge", "rn", "rn-2"]]
    assert _loai(bo.den_han(SANG)) == [("tu_merge", [("rn", "rn-2")])]


def test_moi_lan_mot_tin_khong_bi_luat_mot_gio():
    """D99 "mỗi lần đổi một tin", spec tu-deploy "Mỗi lần … deploy … SHALL sinh một tin"."""
    t0 = datetime(2026, 10, 18, 3, 0, tzinfo=timezone.utc)
    bo = BoChongOn(YEN)
    for loai, ma in (("deploy_xong", None),):
        assert len(bo.nhan([Tin(loai, "rn", ma)], t0)) == 1
        assert bo.nhan([Tin(loai, "rn", ma)], t0 + timedelta(minutes=2)) == []            # trong cửa sổ 5 phút: gom
    assert {g.loai for g in bo.den_han(t0 + timedelta(minutes=5))} == {"deploy_xong"}
    assert bo.den_han(t0 + timedelta(minutes=10)) == []
    assert len(bo.nhan([Tin("deploy_xong", "rn")], t0 + timedelta(minutes=20))) == 1        # chưa đủ 1 giờ vẫn gửi
    bo.nhan([Tin("co_do", "rn", "rn-1")], t0)
    bo.den_han(t0 + timedelta(minutes=6))
    assert bo.nhan([Tin("co_do", "rn", "rn-1")], t0 + timedelta(minutes=30)) == []             # loại cũ: luật 1 giờ giữ
