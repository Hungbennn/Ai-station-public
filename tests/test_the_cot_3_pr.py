"""Thẻ cột 3 hiện PR do trạm mở và `pr.khong_xac_minh` (spec 2 §5.2, spec 4 §6.5; plan 2d Task 3, G10–G13, G16)."""
from bd_gia import BdGia
from bead_gia import bead
from giao_viec_gia import bug, du_an_gia
from tram.api.bo_dem import BoDemBeads
from tram.api.luong import TrangThaiLuong, mot_nhip
from tram.su_kien.kho import KhoSuKien
from tram.suy.giao_viec import suy_giao
from tram.suy.pr_tram import LY_DO, LY_DO_KHAC, pr_tram

DA, C1, C2 = "hr-codex", "a" * 40, "b" * 40
URL = "https://github.com/hung/hr-codex/pull/7"


def ghi(kho, ten, **d):
    kho.ghi(DA, ten, d, bead_id="hr-2", tac_nhan="tram/giao-viec")


def vc3(kho):
    return kho.moi_nhat(DA, "hr-2", "bead.vao_cot_3")


def test_pr_tram_chi_tinh_su_kien_sau_lan_vao_cot_3_hien_tai(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None                            # trạm chưa mở PR
    ghi(kho, "pr.mo", loai="bead", pr=7, url=URL, commit=C1)
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) == {"so": 7, "url": URL, "trang_thai": "mo", "ly_do": None}
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="khong-phai-merge-commit")
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) == {"so": 7, "url": URL, "trang_thai": "khong_xac_minh",
                                                 "ly_do": LY_DO["khong-phai-merge-commit"]}
    ghi(kho, "cot.tra_ve", gop_y="x")
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C2)                               # vòng mới: PR cũ không dính
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None
    ghi(kho, "pr.mo", loai="bead", pr=8, url=URL[:-1] + "8", commit=C1)          # PR của commit khác
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None


def test_pr_tram_loc_du_lieu_la_va_da_merge(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    ghi(kho, "pr.mo", loai="spec", pr=3, url=URL, commit=C1)                     # PR spec của feature: bỏ
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None
    ghi(kho, "pr.mo", loai="bead", pr="7", url="javascript:alert(1)", commit=C1)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="<b>lạ</b>")
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) == {"so": None, "url": None, "trang_thai": "khong_xac_minh",
                                                 "ly_do": LY_DO_KHAC}
    ghi(kho, "pr.da_merge", pr=7, url=URL, commit=C1, merge_commit=C2, nhanh_chinh="main", ma_thao_tac="pr-1")
    assert pr_tram(kho, DA, "hr-2", vc3(kho))["trang_thai"] == "da_merge"


def test_suy_giao_gan_pr_tram_vao_the_cot_3(tmp_path):
    kho, da = KhoSuKien(tmp_path / "sk.db"), du_an_gia(tmp_path)
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    ghi(kho, "pr.mo", loai="bead", pr=7, url=URL, commit=C1)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="head-khac-commit-ban-giao")
    g = suy_giao(da, [bug("hr-1", labels=["cot:can-chot"]), bug("hr-2", labels=["cot:cho-review"])], kho, None)
    assert list(g) == ["hr-codex/hr-2"]
    assert g["hr-codex/hr-2"]["pr"]["commit"] == C1
    assert g["hr-codex/hr-2"]["pr"]["tram"] == {"so": 7, "url": URL, "trang_thai": "khong_xac_minh",
                                                "ly_do": LY_DO["head-khac-commit-ban-giao"]}


def test_su_kien_pr_lam_moi_bang_qua_sse(tmp_path):
    kho, bo = KhoSuKien(tmp_path / "sk.db"), BoDemBeads(lambda ten: BdGia([bead("hr-2")]))
    tt = TrangThaiLuong(moc=0)
    mot_nhip(kho, bo, [DA], tt)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="khong-phai-merge-commit")
    ra = mot_nhip(kho, bo, [DA], tt)
    assert ra[0].startswith("event: su_kien") and ra[-1].startswith("event: phe_duyet_doi")
