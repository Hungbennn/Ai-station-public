"""TM-1: tin Telegram của tự merge / tự deploy (design D-8, D99; spec "Báo Telegram mỗi lần cài đặt đổi", "Báo
Telegram mỗi lần tự merge", "… mỗi lần deploy và lùi"). Hợp đồng sự kiện → tin cho TM-2/TM-3: hai lát đó chỉ GHI sự
kiện, không sửa `tram/bao_tin/`. Tin chỉ có dự án, mã bead, nhãn loại, chi tiết từ bảng mã — không lệnh, SHA, URL."""
from dataclasses import replace

import pytest

from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.nguon_tu_dong import tin_tu_dong
from tram.bao_tin.tin import LOAI_TIN, NHAN_LOAI, Tin, soan_tin
from tram.su_kien.kho import KhoSuKien
from tram.su_kien.mo_hinh import SuKien
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.tu_dong import luu_cai_dat_thao_tac, tam_dung_thao_tac
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import doi_cai_dat

MOI = ("tu_merge", "san_sang_deploy", "deploy_xong", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro",
       "lui_hong", "cai_dat_doi")
URL = "https://may-b.tail.ts.net"
LENH = "/Users/Shared/tram-deploy/repo-nhap/deploy.sh"


def _sk(loai, du_lieu=None, *, du_an="repo-nhap", bead_id=None, tac_nhan="dai-ca/dashboard"):
    return SuKien("2026-10-18T02:00:00Z", du_an, bead_id, loai, tac_nhan, du_lieu or {}, 1)


def test_dang_ky_du_loai_tin_moi():
    assert set(MOI) <= set(LOAI_TIN) and set(MOI) <= set(NHAN_LOAI)


@pytest.mark.parametrize("sk, tin", [
    (_sk("tu_dong.cai_dat", {"cai_dat": {"tu_deploy": True}, "doi": ["tu_deploy"]}),
     [Tin("cai_dat_doi", "repo-nhap", "tu-deploy-bat")]),
    (_sk("tu_dong.cai_dat", {"cai_dat": {"dk_ci": False, "lenh_deploy": LENH}, "doi": ["dk_ci", "lenh_deploy", "la"]}),
     [Tin("cai_dat_doi", "repo-nhap", "dk-ci-tat"), Tin("cai_dat_doi", "repo-nhap", "lenh-deploy-doi")]),
    (_sk("tu_dong.cai_dat", {"cai_dat": {"tu_deploy": False}, "doi": ["tu_deploy"], "ly_do": "hong-3-lan"},
         tac_nhan="tram/tu-deploy"), [Tin("tu_deploy_tu_tat", "repo-nhap")]),
    (_sk("tu_dong.cai_dat", {"cai_dat": {"tu_deploy": False}, "doi": ["tu_deploy"], "ly_do": "lui-hong"},
         tac_nhan="tram/tu-deploy"), [Tin("cai_dat_doi", "repo-nhap", "tram-tu-deploy-tat")]),
    (_sk("tu_dong.tam_dung"), [Tin("cai_dat_doi", "repo-nhap", "tam-dung")]),
    (_sk("tu_dong.tam_dung", {"ly_do": "lui-hong"}, tac_nhan="tram/tu-deploy"),
     [Tin("cai_dat_doi", "repo-nhap", "tram-tam-dung")]),
    (_sk("tu_dong.tiep_tuc", du_an="_tram"), [Tin("cai_dat_doi", "_tram", "tiep-tuc-toan-tram")]),
    (_sk("tu_merge.xong", {"loai": "code"}, bead_id="rn-7", tac_nhan="tram/tu-merge"), [Tin("tu_merge", "repo-nhap", "rn-7")]),
    (_sk("tu_merge.loi", {"ma_loi": "gh-3-lan"}, bead_id="rn-7"), [Tin("tram_loi", "repo-nhap", "rn-7")]),
    (_sk("tu_merge.cho", {"ly_do": ["ci"]}, bead_id="rn-7"), []),
    (_sk("deploy.san_sang", {"commit": "a" * 40, "so_merge": 3}), [Tin("san_sang_deploy", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "dat", "dem_hong": 0}), [Tin("deploy_xong", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "da_lui", "dem_hong": 2}), [Tin("deploy_da_lui", "repo-nhap", "hong-2-lan")]),
    (_sk("deploy.xong", {"ket_qua": "lui_hong", "dem_hong": 1}), [Tin("lui_hong", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "khong_ro"}), [Tin("deploy_khong_ro", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "la"}), []),
    (_sk("deploy.lenh", {"buoc": "deploy", "ma_thoat": 1}), []),
])
def test_su_kien_sang_tin(sk, tin):
    assert tin_tu_dong(sk) == tin == tin_tu_su_kien(sk, None)


@pytest.mark.parametrize("loai, tins, vb", [
    ("cai_dat_doi", [Tin("cai_dat_doi", "repo-nhap", "tu-deploy-bat")],
     "[tram] repo-nhap · 1 cài đặt tự động vừa đổi (tự deploy bật) → " + URL),
    ("cai_dat_doi", [Tin("cai_dat_doi", "repo-nhap", "tram-tu-deploy-tat")],
     "[tram] repo-nhap · 1 cài đặt tự động vừa đổi (trạm: tự deploy tắt) → " + URL),
    ("cai_dat_doi", [Tin("cai_dat_doi", "_tram", "tam-dung-toan-tram")],
     "[tram] cài đặt tự động vừa đổi (TẠM DỪNG toàn trạm) → " + URL),
    ("tu_merge", [Tin("tu_merge", "repo-nhap", "rn-7")], "[tram] repo-nhap · 1 tự merge (rn-7) → " + URL),
    ("deploy_da_lui", [Tin("deploy_da_lui", "repo-nhap", "hong-2-lan")],
     "[tram] repo-nhap · 1 deploy hỏng, đã tự lùi (hỏng liên tiếp 2 lần) → " + URL),
    ("tu_deploy_tu_tat", [Tin("tu_deploy_tu_tat", "repo-nhap")],
     "[tram] repo-nhap · 1 trạm đã tự tắt tự deploy sau 3 lần hỏng → " + URL),
    ("lui_hong", [Tin("lui_hong", "repo-nhap")], "[tram] repo-nhap · 1 LÙI HỎNG — cần Đại ca → " + URL),
])
def test_soan_tin_loi_thuong(loai, tins, vb):
    assert soan_tin(loai, tins, URL) == vb


def test_cho_review_khong_bi_dich_chi_tiet():
    assert soan_tin("cho_review", [Tin("cho_review", "hr", "tam-dung")], None) == "[tram] hr · 1 việc chờ review (tam-dung)"


def test_dau_cuoi_dashboard_den_tin_khong_chua_lenh(tmp_path, monkeypatch):
    """Scenario "Bật tự deploy" + "Trạm tự tắt": thao tác dashboard / trạm → sự kiện → tin; không chép lệnh."""
    monkeypatch.setattr("tram.thao_tac.tu_dong.can_duong", lambda *a: None)
    k, kt = KhoSuKien(tmp_path / "sk.db"), KhoThaoTac(tmp_path / "sk.db")
    du = replace(MAC_DINH, lenh_deploy=LENH, lenh_kiem_song="k.sh", lenh_lui="l.sh")
    luu_cai_dat_thao_tac(k, kt, "repo-nhap", du, bat_ghi=True, ma="ma-tin-00001", expected_version="0")
    pb = k.gan_day("repo-nhap", "tu_dong.cai_dat", 1)[0].id
    luu_cai_dat_thao_tac(k, kt, "repo-nhap", replace(du, tu_deploy=True), bat_ghi=True, ma="ma-tin-00002",
                         expected_version=str(pb))
    doi_cai_dat(k.db, "repo-nhap", lambda c: replace(c, tu_deploy=False), tac_nhan="tram/tu-deploy",
                them={"ly_do": "hong-3-lan"})
    tam_dung_thao_tac(k, kt, "_tram", tam_dung=True, ma="ma-tin-00003", expected_version="")
    tins = [t for s in k.sau_id(0, 20) for t in tin_tu_su_kien(s, k)]
    assert tins == [Tin("cai_dat_doi", "repo-nhap", "lenh-deploy-doi"), Tin("cai_dat_doi", "repo-nhap", "lenh-kiem-song-doi"),
                    Tin("cai_dat_doi", "repo-nhap", "lenh-lui-doi"), Tin("cai_dat_doi", "repo-nhap", "tu-deploy-bat"),
                    Tin("tu_deploy_tu_tat", "repo-nhap"), Tin("cai_dat_doi", "_tram", "tam-dung-toan-tram")]
    vb = soan_tin("cai_dat_doi", tins[:4], URL)
    assert vb == ("[tram] repo-nhap · 4 cài đặt tự động vừa đổi (lệnh deploy đổi, lệnh kiểm còn sống đổi, lệnh lùi đổi, "
                  "tự deploy bật) → " + URL)
    assert "tram-deploy" not in vb and "k.sh" not in vb
