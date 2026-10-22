"""Tin Telegram "PR đã merge" / "PR không xác minh được" từ `pr.da_merge`, `pr.khong_xac_minh` của 4c (spec 2 §6,
§4 mục 5; D15; plan 2d Task 4, G15–G17)."""
from datetime import datetime, timedelta, timezone

from bd_gia import BdGia
from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import LOAI_TIN, NHAN_LOAI, Tin, soan_tin
from tram.bao_tin.vong import NguCanhBaoTin, mot_vong
from tram.su_kien.kho import KhoSuKien, SuKien

T0 = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)             # 10:00 giờ VN
SHA, MERGE, URL = "a" * 40, "b" * 40, "https://github.com/hung/hr-codex/pull/7"
DA_MERGE = {"bead_id": "hr-1", "pr": 7, "url": URL, "commit": SHA, "merge_commit": MERGE, "nhanh_chinh": "main",
            "ma_thao_tac": "pr-0123456789abcdef0123"}
KHONG_XM = {"bead_id": "hr-2", "pr": 8, "commit": SHA, "ly_do": "khong-phai-merge-commit",
            "ma_thao_tac": "pr-0123456789abcdef0124"}


def sk(loai, du_lieu=None, bead="hr-1"):
    return SuKien("2026-10-13T03:00:00Z", "hr-codex", bead, loai, "tram/giao-viec", du_lieu or {})


def test_hai_su_kien_pr_thanh_tin_pr_mo_thi_khong():
    assert {"pr_da_merge", "pr_khong_xac_minh"} <= set(LOAI_TIN) and {"pr_da_merge", "pr_khong_xac_minh"} <= set(
        NHAN_LOAI)
    assert tin_tu_su_kien(sk("pr.da_merge", DA_MERGE), None) == [Tin("pr_da_merge", "hr-codex", "hr-1")]
    assert tin_tu_su_kien(sk("pr.khong_xac_minh", KHONG_XM, "hr-2"), None) == [
        Tin("pr_khong_xac_minh", "hr-codex", "hr-2")]
    assert tin_tu_su_kien(sk("pr.mo", {"pr": 7, "url": URL, "commit": SHA}), None) == []


def test_mot_vong_gui_tin_khong_lo_pr_url_sha_ly_do(tmp_path):
    da_gui = []
    nc = NguCanhBaoTin(kho=KhoSuKien(tmp_path / "sk.db"), tao_bd=lambda ten: BdGia([]), gui=da_gui.append,
                       thu_muc=tmp_path / "bao-tin", dashboard_url="https://may-b.tail.ts.net/", bay_gio=lambda: T0)
    assert mot_vong(nc) == 0                                         # lần đầu: chỉ đặt mốc
    nc.kho.ghi("hr-codex", "pr.da_merge", DA_MERGE, bead_id="hr-1", tac_nhan="tram/giao-viec")
    nc.kho.ghi("hr-codex", "pr.khong_xac_minh", KHONG_XM, bead_id="hr-2", tac_nhan="tram/giao-viec")
    assert mot_vong(nc) == 2
    assert sorted(da_gui) == sorted([
        "[tram] hr-codex · 1 PR đã merge, trạm xác minh đúng commit đã kiểm (hr-1) → https://may-b.tail.ts.net/",
        "[tram] hr-codex · 1 PR đã merge nhưng trạm không xác minh được, cần Đại ca Duyệt tay (hr-2)"
        " → https://may-b.tail.ts.net/"])
    assert not any(x in t for t in da_gui for x in ("github", "#7", "#8", SHA[:7], MERGE[:7], "khong-phai", "main"))
    nc.kho.ghi("hr-codex", "pr.da_merge", DA_MERGE, bead_id="hr-1", tac_nhan="tram/giao-viec")
    assert mot_vong(nc) == 0                                         # cùng (loại, bead) trong 1 giờ: không gửi lại


def test_chong_on_gom_5_phut_va_gio_yen_lang():
    bo = BoChongOn("23:00-07:00")
    a, b = Tin("pr_da_merge", "hr-codex", "hr-1"), Tin("pr_da_merge", "hr-codex", "hr-2")
    assert [g.tins for g in bo.nhan([a], T0)] == [(a,)]
    assert bo.nhan([b], T0 + timedelta(minutes=1)) == []                       # trong cửa sổ: chờ gom
    assert [g.tins for g in bo.den_han(T0 + timedelta(minutes=5))] == [(b,)]
    dem = datetime(2026, 10, 13, 16, 30, tzinfo=timezone.utc)                 # 23:30 giờ VN
    k = Tin("pr_khong_xac_minh", "hr-codex", "hr-3")
    assert BoChongOn("23:00-07:00").nhan([a, k], dem) == []
    assert "hr-1" in soan_tin("pr_da_merge", [a], None) and "→" not in soan_tin("pr_da_merge", [a], None)
