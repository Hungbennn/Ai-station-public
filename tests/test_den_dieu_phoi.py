"""Đèn Điều phối suy từ nhịp hook máy A (spec 2 §5.5; plan 2e Task 1, G7–G9; review đợt 4 F11)."""
from contextlib import closing
from datetime import datetime, timedelta, timezone

from api_gia import tao_app_gia
from asgi_gia import goi
from tram.su_kien.kho import KhoSuKien, SuKien
from tram.suy.dieu_phoi import DU_AN_HE, LOAI, TAC_NHAN, can_ghi, den_dieu_phoi
from tram.suy.kho_nhip import doc_nhip

T = datetime(2026, 10, 15, 7, 0, tzinfo=timezone.utc)


def nhip(phut: float, su_kien: str = "Stop", phien: str = "a" * 16) -> SuKien:
    luc = (T + timedelta(minutes=phut)).isoformat().replace("+00:00", "Z")
    return SuKien(luc, DU_AN_HE, None, LOAI, TAC_NHAN, {"su_kien": su_kien, "phien": phien})


def luc(phut: float) -> datetime:
    return T + timedelta(minutes=phut)


def test_den_theo_phien_va_han_song_15_phut():
    assert den_dieu_phoi([], luc(0)) == {"sang": None, "nhip_cuoi": None}
    mot = [nhip(0)]
    assert den_dieu_phoi(mot, luc(10)) == {"sang": True, "nhip_cuoi": "2026-10-15T07:00:00Z"}
    assert den_dieu_phoi(mot, luc(15))["sang"] is True                                # đúng 15 phút: còn sáng
    assert den_dieu_phoi(mot, luc(15.5)) == {"sang": False, "nhip_cuoi": "2026-10-15T07:00:00Z"}
    hai = [nhip(5, "SessionEnd"), nhip(0, "UserPromptSubmit", "b" * 16)]                # mới → cũ
    assert den_dieu_phoi(hai, luc(6)) == {"sang": True, "nhip_cuoi": "2026-10-15T07:05:00Z"}   # phiên b còn
    assert den_dieu_phoi(hai, luc(16))["sang"] is False
    assert den_dieu_phoi([nhip(1, "SessionEnd"), nhip(0)], luc(2))["sang"] is False     # phiên duy nhất đã đóng
    assert den_dieu_phoi([nhip(2), nhip(1, "SessionEnd")], luc(3))["sang"] is True      # mở lại (resume)


def test_can_ghi_gop_60_giay_tru_khi_doi_trang_thai():
    assert can_ghi([], "a" * 16, "SessionStart", luc(0))
    ds = [nhip(0)]
    assert not can_ghi(ds, "a" * 16, "UserPromptSubmit", luc(0.5))
    assert can_ghi(ds, "a" * 16, "UserPromptSubmit", luc(1))
    assert can_ghi(ds, "b" * 16, "Stop", luc(0.1))                                      # phiên khác
    assert can_ghi(ds, "a" * 16, "SessionEnd", luc(0.1))                                # đang chạy → kết thúc
    het = [nhip(0, "SessionEnd")]
    assert not can_ghi(het, "a" * 16, "SessionEnd", luc(0.1))
    assert can_ghi(het, "a" * 16, "SessionStart", luc(0.1))                             # kết thúc → mở lại


def test_api_van_phong_tra_sang_that_cho_phong_dieu_phoi(tmp_path):
    app, pt = tao_app_gia(tmp_path, {})
    assert {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"] == {
        "ma": "dieu-phoi", "loai": "dieu_phoi", "ten": "Điều phối", "sang": None, "nhip_cuoi": None}
    kho = KhoSuKien(tmp_path / "sk.db")
    luc_ghi = kho.ghi(DU_AN_HE, LOAI, {"su_kien": "Stop", "phien": "c" * 16}, tac_nhan=TAC_NHAN)
    kho.close()
    dp = {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]
    assert (dp["sang"], dp["nhip_cuoi"]) == (True, luc_ghi)
    pt.dong_ho = lambda: datetime.now(timezone.utc) + timedelta(minutes=20)              # quá hạn → xám
    dp = {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]
    assert (dp["sang"], dp["nhip_cuoi"]) == (False, luc_ghi)                             # vẫn biết nhịp cuối


def test_hon_200_nhip_khong_lam_tat_phien_con_song(tmp_path):
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        kho.ghi(DU_AN_HE, LOAI, {"su_kien": "Stop", "phien": "a" * 16}, tac_nhan=TAC_NHAN)
        for i in range(201):
            kho.ghi(DU_AN_HE, LOAI, {"su_kien": "SessionEnd", "phien": f"{i:016x}"}, tac_nhan=TAC_NHAN)
        luc = datetime.now(timezone.utc)
        assert den_dieu_phoi(doc_nhip(kho, luc), luc)["sang"] is True
        sau = luc + timedelta(minutes=16)
        assert den_dieu_phoi(doc_nhip(kho, sau), sau)["sang"] is False                   # hết hạn ≠ chưa từng có
