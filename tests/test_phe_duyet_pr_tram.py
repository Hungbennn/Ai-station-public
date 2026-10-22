"""Trang Phê duyệt: mục "Chờ review để đóng" mang `chi_tiet.pr_tram` (D38 — C6 của 2d; plan 2d Task 7, G21)."""
from bead_gia import bead, notes_ban_giao
from tram.su_kien.kho import KhoSuKien
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.pr_tram import LY_DO

C1, URL = "a" * 40, "https://github.com/hung/hr-codex/pull/7"


def ghi(kho, ten, bead_id="hr-1", **d):
    kho.ghi("hr", ten, d, bead_id=bead_id, tac_nhan="tram/giao-viec")


def test_muc_cho_review_mang_pr_tram(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    beads = [bead("hr-1", labels=["cot:cho-review"], notes=notes_ban_giao()),
             bead("hr-2", labels=["co-do", "cot:cho-review"]), bead("hr-3", labels=["cot:ai-lam"])]
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    ghi(kho, "pr.mo", loai="bead", pr=7, url=URL, commit=C1)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="khong-phai-merge-commit")
    ghi(kho, "pr.mo", "hr-2", loai="bead", pr=8, url=URL, commit=C1)            # hr-2 chưa vào cột 3
    muc = gom_phe_duyet(["hr"], {"hr": beads}, kho)
    cr = {m["bead_id"]: m["chi_tiet"] for m in muc if m["loai"] == "cho-review"}
    assert cr["hr-1"]["pr_tram"] == {"so": 7, "url": URL, "trang_thai": "khong_xac_minh",
                                     "ly_do": LY_DO["khong-phai-merge-commit"]}
    assert cr["hr-1"]["pr"] == "https://github.com/o/r/pull/7"                 # khoá cũ của bàn giao giữ nguyên
    assert cr["hr-2"]["pr_tram"] is None
    assert all("pr_tram" not in m["chi_tiet"] for m in muc if m["loai"] != "cho-review")
