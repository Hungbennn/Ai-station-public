"""Trạm tự mở PR và tự xác minh merge (spec 4 §6.4 mục 4, §6.5, §7.3; Q7) — lát 4c, GitHub giả + Git cục bộ."""
from pathlib import Path
from dataclasses import replace

import pytest

from bd_gia import BdGia
from bead_gia import bead, notes_ban_giao
from gh_gia import REPO, GhGia
from git_gia import git
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, kho_tam
from su_kien_gia import DA as TEN, cong_bo, ds, sk
from tram.ban_giao.doc import tom_tat_ban_giao
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.pr import mo_pr_bead, mo_pr_spec
from tram.giao_viec.pr_merge import kiem_merge
from tram.giao_viec.tieu_chi import digest_tieu_chi, tach_tieu_chi

DA = DuAn(TEN, Path("/r"), None, {})


class M:
    def __init__(self, tmp_path, **kw_gh):
        self.k, self.kho = dung_kho(tmp_path), kho_tam(tmp_path)
        self.g = BdGia([bead("hr-1", status="in_progress", labels=["cot:cho-review"], notes=notes_ban_giao())])
        self.gh = GhGia(lambda nhanh: git(self.k.origin, "rev-parse", nhanh), **kw_gh)
        self.c = self.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=self.k.main)
        fetch(self.k.kho)
        cong_bo(self.kho, 2, self.c)
        sk(self.kho, "bead.vao_cot_3", {"bead_id": "hr-1", "commit_code": self.c, "commit_ban_giao": self.c,
                                        "digest_tieu_chi": digest_tieu_chi(tach_tieu_chi(self.g.beads["hr-1"].acceptance_criteria)),
                                        "co_do": True, "pr": None})

    def mo(self):
        return mo_pr_bead(self.gh, REPO, self.kho, self.k.kho, DA, self.g, self.g.beads["hr-1"], ds(self.kho), LUC)

    def kiem(self):
        return kiem_merge(self.gh, REPO, self.kho, self.k.kho, DA, self.g, self.g.beads["hr-1"], ds(self.kho), LUC)

    def merge_vao_main(self, head, *, squash=False):
        git(self.k.dev, "checkout", "-q", "-B", "main", git(self.k.origin, "rev-parse", "main"))
        if squash:
            git(self.k.dev, "checkout", "-q", head, "--", "src/tom_tat.py")
            git(self.k.dev, "commit", "-q", "-m", "squash")
        else:
            git(self.k.dev, "merge", "-q", "--no-ff", "-m", "Merge PR", head)
        m = git(self.k.dev, "rev-parse", "HEAD")
        git(self.k.dev, "push", "-q", "origin", "HEAD:refs/heads/main")
        fetch(self.k.kho)
        return m


def loai(m, l):
    return [s for s in ds(m.kho) if s.loai == l]


def test_mo_pr_dien_pr_va_khong_lap(tmp_path):
    m = M(tmp_path)
    assert m.mo() == "pr_mo"
    [(_, repo, nhanh, base, tieu_de, than)] = [g for g in m.gh.goi if g[0] == "tao_pr"]
    assert (repo, nhanh, base, tieu_de) == (REPO, "tram/hr-1", "main", "hr-1: Việc") and m.c in than and "CÓ" in than
    [e] = loai(m, "pr.mo")
    assert (e.du_lieu["pr"], e.du_lieu["commit"], e.du_lieu["loai"]) == (1, m.c, "bead")
    assert tom_tat_ban_giao(m.g.beads["hr-1"].notes)["pr"] == f"https://github.com/{REPO}/pull/1"
    so_goi = len(m.g.goi)
    assert m.mo() is None and len(m.gh.prs) == 1 and len(m.g.goi) == so_goi


def test_tao_mat_phan_hoi_van_doi_soat_mot_pr(tmp_path):
    m = M(tmp_path, mat_phan_hoi_khi_tao=True)
    assert m.mo() == "pr_mo" and len(m.gh.prs) == 1 and len(loai(m, "pr.mo")) == 1
    m2 = M(tmp_path / "merged")
    m2.gh.tao_pr(REPO, "tram/hr-1", "main", "đã tạo trước crash", "")
    m2.gh.dat(1, trang_thai="MERGED", merge_commit=m2.merge_vao_main(m2.c))
    assert m2.mo() == "pr_mo" and len(m2.gh.prs) == 1
    assert m2.kiem() == "da_merge"


def test_head_lech_hoac_ref_cong_bo_doi_thi_khong_ghi(tmp_path):
    m = M(tmp_path)
    m.k.day("tram/hr-1", {"src/khac.py": "y\n"}, tu=m.c)              # remote đi trước commit đã kiểm
    fetch(m.k.kho)
    assert m.mo() == "pr_cho" and loai(m, "pr.mo") == [] and not m.gh.prs
    m2 = M(tmp_path / "b")
    cong_bo(m2.kho, 3, "e" * 40)
    assert m2.mo() is None and m2.gh.goi == []
    m3 = M(tmp_path / "c")
    m3.mo()
    m3.gh.dat(1, trang_thai="MERGED", merge_commit=m3.merge_vao_main(m3.c))
    cong_bo(m3.kho, 3, "e" * 40)
    assert m3.kiem() is None and m3.g.beads["hr-1"].status != "closed"
    m4 = M(tmp_path / "d")
    m4.mo()
    m4.gh.dat(1, trang_thai="MERGED", merge_commit=m4.merge_vao_main(m4.c))
    m4.g.beads["hr-1"] = replace(m4.g.beads["hr-1"], acceptance_criteria='["mới"]')
    assert m4.kiem() is None and m4.g.beads["hr-1"].status != "closed"


def test_pr_mo_san_duoc_dung_lai(tmp_path):
    m = M(tmp_path)
    m.gh.tao_pr(REPO, "tram/hr-1", "main", "cũ", "")
    m.gh.goi.clear()
    assert m.mo() == "pr_mo" and [g[0] for g in m.gh.goi] == ["ds_pr"] and loai(m, "pr.mo")[0].du_lieu["pr"] == 1


def test_merge_that_thi_dong_bead_mot_lan(tmp_path):
    m = M(tmp_path)
    m.mo()
    assert m.kiem() is None                                              # PR còn mở
    m.gh.dat(1, trang_thai="MERGED", merge_commit=m.merge_vao_main(m.c))
    assert m.kiem() == "da_merge"
    b = m.g.beads["hr-1"]
    assert b.status == "closed" and "Trạm xác minh PR #1" in b.close_reason and len(loai(m, "pr.da_merge")) == 1
    assert m.kiem() is None and m.g.so_lan("dong") == 1


def test_squash_khong_xac_minh_va_khong_hoi_lai(tmp_path):
    m = M(tmp_path)
    m.mo()
    m.gh.dat(1, trang_thai="MERGED", merge_commit=m.merge_vao_main(m.c, squash=True))
    assert m.kiem() == "pr_khong_xac_minh" and m.g.beads["hr-1"].status == "in_progress"
    assert loai(m, "pr.khong_xac_minh")[0].du_lieu["ly_do"] == "khong-phai-merge-commit"
    so = len(m.gh.goi)
    assert m.kiem() is None and len(m.gh.goi) == so


def test_merge_commit_chua_fetch_thi_cho(tmp_path):
    m = M(tmp_path)
    m.mo()
    m.gh.dat(1, trang_thai="MERGED", merge_commit="f" * 40)
    assert m.kiem() == "pr_cho_fetch" and loai(m, "pr.khong_xac_minh") == []


@pytest.mark.parametrize("kw,ly_do", [({"base": "develop"}, "sai-nhanh-chinh"), ({"ngoai_repo": True}, "sai-nhanh"),
                                      ({"so": 9}, "pr-khac")])
def test_pr_sai_thong_tin_khong_xac_minh(tmp_path, kw, ly_do):
    m = M(tmp_path)
    m.mo()
    m.gh.dat(1, trang_thai="MERGED", merge_commit=m.merge_vao_main(m.c), **kw)
    assert m.kiem() == "pr_khong_xac_minh" and loai(m, "pr.khong_xac_minh")[0].du_lieu["ly_do"] == ly_do


def test_head_moi_du_la_merge_van_can_kiem_lai(tmp_path):
    m = M(tmp_path)
    m.mo()
    moi_main = m.k.day("main", {"README.md": "main đi tiếp\n"}, tu=m.k.main)
    git(m.k.dev, "checkout", "-q", "-B", "tram/hr-1", m.c)
    git(m.k.dev, "merge", "-q", "--no-ff", "-m", "Update branch", moi_main)
    h = git(m.k.dev, "rev-parse", "HEAD")
    m.gh.dat(1, trang_thai="MERGED", head=h, merge_commit=m.merge_vao_main(h))
    assert m.kiem() == "pr_khong_xac_minh"  # graph merge không chứng minh tree không sửa mã
    m2 = M(tmp_path / "b")
    m2.mo()
    h2 = m2.k.day("tram/hr-1", {"src/len.py": "lén\n"}, tu=m2.c)
    m2.gh.dat(1, trang_thai="MERGED", head=h2, merge_commit=m2.merge_vao_main(h2))
    assert m2.kiem() == "pr_khong_xac_minh"
    assert loai(m2, "pr.khong_xac_minh")[0].du_lieu["ly_do"] == "head-khac-commit-ban-giao"


def test_mo_pr_spec_da_duyet(tmp_path):
    m = M(tmp_path)
    m.g.beads["hr-f"] = bead("hr-f", issue_type="feature", title="Hoa hồng tạm tính", labels=["theo-plan"])
    s = m.k.day("tram/spec-hr-f", {"docs/specs/x.md": "spec\n"}, tu=m.k.main)
    fetch(m.k.kho)
    cong_bo(m.kho, 1, s, bead_id="hr-f")
    sk(m.kho, "spec.duyet", {"feature": "hr-f", "commit": s, "digest_bead": "sha256:b", "bead_moi": [],
                             "ma_thao_tac": "dy-1"}, bead_id="hr-f")
    chay = lambda: mo_pr_spec(m.gh, REPO, m.kho, m.k.kho, DA, m.g.beads["hr-f"], ds(m.kho, "hr-f"), LUC)
    assert chay() == "pr_mo" and m.gh.prs[1].nhanh == "tram/spec-hr-f" and chay() is None
    assert ds(m.kho, "hr-f")[-1].du_lieu["loai"] == "spec"
