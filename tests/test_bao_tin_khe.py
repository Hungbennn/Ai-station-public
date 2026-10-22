from datetime import datetime, timezone

from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin, soan_tin
from tram.su_kien.kho import KhoSuKien


def test_cau_dao_ngat_thanh_tin_theo_ly_do(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("_tram", "khe.cau_dao_ngat", {"khe_id": "B/claude-1", "ly_do": "het-han-muc", "toi_luc": "x"})
    k.ghi("_tram", "khe.cau_dao_ngat", {"khe_id": "B/claude-2", "ly_do": "loi-lien-tiep", "toi_luc": "x"})
    k.ghi("_tram", "khe.cau_dao_dong", {"khe_id": "B/claude-2", "ly_do": "het-gio", "toi_luc": None})
    k.ghi("_tram", "khe.tat", {"khe_id": "B/claude-1", "vi_sao": ""})
    assert [t for s in k.sau_id(0, 10) for t in tin_tu_su_kien(s, k)] == [
        Tin("khe_het_han_muc", "_tram", "B/claude-1"), Tin("khe_cau_dao", "_tram", "B/claude-2")]


def test_soan_tin_khe_chi_ma_khe_va_link():
    tins = (Tin("khe_het_han_muc", "_tram", "B/claude-1"), Tin("khe_het_han_muc", "_tram", "B/claude-2"))
    assert soan_tin("khe_het_han_muc", tins, "https://b.ts.net") == \
        "[tram] khe hết hạn mức (B/claude-1, B/claude-2) → https://b.ts.net"
    assert soan_tin("khe_cau_dao", (Tin("khe_cau_dao", "_tram", "B/x y;z"),), None) == "[tram] cầu dao khe ngắt"
    assert soan_tin("estop_bat", (Tin("estop_bat", "_tram"),), None) == "[tram] estop BẬT"


def test_chong_on_khong_lap_cung_khe_trong_mot_gio():
    bo, luc = BoChongOn(), datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
    t = Tin("khe_cau_dao", "_tram", "B/claude-1")
    assert len(bo.nhan([t], luc)) == 1 and bo.nhan([t], luc.replace(minute=30)) == []
