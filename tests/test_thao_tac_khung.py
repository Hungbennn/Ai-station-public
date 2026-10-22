import sqlite3
import threading
import time

import pytest

from bead_gia import bead
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chay import YeuCau, chay_thao_tac, cung_version
from tram.thao_tac.chung import ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

MA = "ma-thu-0001"


def yc(ma=MA, noi_dung=None, bead_id="hr-1"):
    return YeuCau(ma, "thu", "hr", bead_id, noi_dung or {"a": 1}, "2026-10-13T01:00:00Z")


def test_kho_tao_lay_danh_dau_ket_thuc(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")
    k.tao(MA, loai="thu", du_an="hr", bead_id="hr-1", digest="d", expected_version="v")
    k.xong_buoc(MA, "a", 1)
    k.xong_buoc(MA, "b", {"x": "ă"})
    bg = k.lay(MA)
    assert bg.buoc_da_xong == {"a": 1, "b": {"x": "ă"}} and bg.ket_qua is None
    assert (bg.loai, bg.du_an, bg.bead_id, bg.expected_version) == ("thu", "hr", "hr-1", "v")
    k.ket_thuc(MA, {"xong": True})
    assert k.lay(MA).ket_qua == {"xong": True}
    assert k.lay("ma-khac-0001") is None
    k.close()
    with pytest.raises(sqlite3.ProgrammingError):
        k.lay(MA)


def test_kho_trung_ma_nem_integrity(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")
    k.tao(MA, loai="thu", du_an="hr", bead_id=None, digest="d", expected_version="v")
    with pytest.raises(sqlite3.IntegrityError):
        k.tao(MA, loai="thu", du_an="hr", bead_id=None, digest="d", expected_version="v")


def test_chay_dung_thu_tu_va_lan_hai_tra_ket_qua_cu(tmp_path):
    k, goi = KhoThaoTac(tmp_path / "sk.db"), []
    buoc = [("a", lambda d: goi.append("a") or 1), ("b", lambda d: goi.append("b") or d["a"] + 1)]
    kq = chay_thao_tac(k, yc(), kiem_moi=lambda: None, cac_buoc=buoc)
    assert kq.ket_qua == {"a": 1, "b": 2} and kq.lap_lai is False and goi == ["a", "b"]
    kq2 = chay_thao_tac(k, yc(), kiem_moi=lambda: pytest.fail("không được kiểm lại"), cac_buoc=buoc)
    assert kq2.lap_lai is True and kq2.ket_qua == {"a": 1, "b": 2} and goi == ["a", "b"]


def test_cung_ma_khac_noi_dung_la_xung_dot(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")
    chay_thao_tac(k, yc(), kiem_moi=lambda: None, cac_buoc=[("a", lambda d: 1)])
    with pytest.raises(XungDot):
        chay_thao_tac(k, yc(noi_dung={"a": 2}), kiem_moi=lambda: None, cac_buoc=[("a", lambda d: 1)])


def test_kiem_moi_that_bai_thi_khong_ghi_gi(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")

    def kiem():
        raise XungDot("bead đã đổi")

    with pytest.raises(XungDot):
        chay_thao_tac(k, yc(), kiem_moi=kiem, cac_buoc=[("a", lambda d: 1)])
    assert k.lay(MA) is None


def test_buoc_loi_thi_lan_sau_lam_tiep_khong_lam_lai(tmp_path):
    k, goi, lan = KhoThaoTac(tmp_path / "sk.db"), [], {"n": 0}

    def b(d):
        lan["n"] += 1
        if lan["n"] == 1:
            raise RuntimeError("crash")
        goi.append("b")
        return d["a"] + 1

    buoc = [("a", lambda d: goi.append("a") or 1), ("b", b)]
    with pytest.raises(RuntimeError):
        chay_thao_tac(k, yc(), kiem_moi=lambda: None, cac_buoc=buoc)
    assert k.lay(MA).buoc_da_xong == {"a": 1} and k.lay(MA).ket_qua is None
    kq = chay_thao_tac(k, yc(), kiem_moi=lambda: pytest.fail("không kiểm lại khi làm tiếp"), cac_buoc=buoc)
    assert goi == ["a", "b"] and kq.ket_qua == {"a": 1, "b": 2} and kq.lap_lai is False


def test_ma_khong_hop_le(tmp_path):
    with pytest.raises(KhongHopLe):
        chay_thao_tac(KhoThaoTac(tmp_path / "sk.db"), yc(ma="ngắn"), kiem_moi=lambda: None, cac_buoc=[])


def test_hai_luong_cung_ma_chi_chay_mot_lan(tmp_path):
    db, dem, kq = tmp_path / "sk.db", [], []

    def b(d):
        time.sleep(0.05)
        dem.append(1)
        return 1

    def chay():
        kq.append(chay_thao_tac(KhoThaoTac(db), yc(), kiem_moi=lambda: None, cac_buoc=[("b", b)]))

    luong = [threading.Thread(target=chay) for _ in range(2)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert len(dem) == 1 and sorted(x.lap_lai for x in kq) == [False, True]


def test_cung_version():
    assert cung_version("2026-10-13T01:00:00Z", "2026-10-13T01:00:00+00:00")
    assert not cung_version("2026-10-13T01:00:00Z", "2026-10-13T01:00:01Z")
    assert cung_version("bat", "bat") and not cung_version("bat", "tat")


def test_kiem_version_bead():
    kiem_version(bead(updated_at="2026-10-13T01:00:00Z"), "2026-10-13T01:00:00Z")
    with pytest.raises(XungDot):
        kiem_version(bead(updated_at="2026-10-13T01:00:05Z"), "2026-10-13T01:00:00Z")


def test_ghi_su_kien_mot_lan_theo_ma(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    assert ghi_su_kien_mot_lan(k, "hr", "hr-1", "cot.tra_ve", {"gop_y": "x"}, ma=MA) is True
    assert ghi_su_kien_mot_lan(k, "hr", "hr-1", "cot.tra_ve", {"gop_y": "x"}, ma=MA) is False
    assert ghi_su_kien_mot_lan(k, "_tram", None, "estop.bat", {}, ma=MA) is True
    assert ghi_su_kien_mot_lan(k, "_tram", None, "estop.bat", {}, ma=MA) is False
    s = k.moi_nhat("hr", "hr-1", "cot.tra_ve")
    assert s.du_lieu == {"gop_y": "x", "ma_thao_tac": MA} and s.tac_nhan == "dai-ca/dashboard"
    assert len(k.gan_day("hr", "cot.tra_ve", 10)) == 1
