from dataclasses import replace
import subprocess

import pytest

from duyet_merge_gia import URL, V, ghi_sk, tao
from git_gia import git
from tram.giao_viec.git_kiem import la_to_tien, sha_cua
from tram.beads.bd import LoiBd
from tram.thao_tac.duyet_merge import NguonDuyet
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.thao_tac.phe_duyet import duyet

MA = "ma-duyet-merge-01"


def bam(t):
    return duyet(t.n, "hr-2", ma=MA, expected_version=V)


def tu_choi(t, ly_do):
    moc = t.n.kho.id_moi_nhat()
    with pytest.raises(KhongHopLe, match=ly_do):
        bam(t)
    assert t.n.bd.beads["hr-2"].status == "open" and t.n.bd.goi == []
    assert t.n.kho_tt.lay(MA) is None and t.n.kho.id_moi_nhat() == moc


def test_chua_vao_khong_pr_khong_dong(tmp_path):
    t = tao(tmp_path)
    tu_choi(t, "Commit chưa vào main và trạm chưa mở PR — ghép nhánh tram/hr-2 vào main rồi bấm Duyệt")


def test_fetch_truoc_khi_kiem_va_ly_do_commit(tmp_path):
    t = tao(tmp_path, da_vao=True, nhanh_chinh="develop", pr=URL)
    assert sha_cua(t.kg, "origin/develop") == t.dau
    assert bam(t).ket_qua == {"dong": {"pr": URL}}
    assert t.n.bd.beads["hr-2"].close_reason == f"Đại ca duyệt — commit {t.commit[:7]} đã vào develop"
    assert t.goi == [] and sha_cua(t.kg, "origin/develop") == t.commit
    assert bam(t).lap_lai and t.n.bd.so_lan("dong") == 1


@pytest.mark.parametrize("state", ["OPEN", "CLOSED", "MERGED"])
def test_pr_chua_merge_ke_ca_state_merged_nhung_merged_at_null(tmp_path, state):
    t = tao(tmp_path, pr=URL)
    t.pr["state"] = state
    tu_choi(t, f"PR {URL} chưa merge — merge trên GitHub \\(Create a merge commit\\) rồi bấm Duyệt")


@pytest.mark.parametrize("nguon", ["notes", "pr.mo"])
def test_squash_commit_khong_la_to_tien_nhung_pr_merged_dong(tmp_path, nguon):
    t = tao(tmp_path, pr=URL if nguon == "notes" else None)
    if nguon == "pr.mo":
        ghi_sk(t, "pr.mo", loai="bead", commit=t.commit, url=URL, pr=7)
    t.pr.update(state="MERGED", mergedAt="2026-10-21T01:00:00Z", mergeCommit={"oid": t.dau})
    bam(t)
    assert not la_to_tien(t.kg, t.commit, "origin/main")
    assert t.n.bd.beads["hr-2"].status == "closed"
    assert t.n.bd.beads["hr-2"].close_reason.startswith(f"Đại ca xác nhận đã merge PR {URL}")


def test_pr_merged_sai_base_tu_choi(tmp_path):
    t = tao(tmp_path, pr=URL)
    t.pr.update(state="MERGED", mergedAt=V, baseRefName="khac")
    tu_choi(t, "nhánh chính")


@pytest.mark.parametrize("loi", [subprocess.CalledProcessError(1, "git"), subprocess.TimeoutExpired("git", 1)])
def test_fetch_loi_tu_choi_ke_ca_pr_da_merge(tmp_path, monkeypatch, loi):
    t = tao(tmp_path, da_vao=True, pr=URL)
    t.pr.update(state="MERGED", mergedAt=V)
    def hong(*a, **kw):
        raise loi
    monkeypatch.setattr("tram.thao_tac.duyet_merge.fetch", hong)
    tu_choi(t, "fetch")


@pytest.mark.parametrize("thieu", ["nguon", "kho", "remote", "nhanh", "commit"])
def test_thieu_bang_chung_tu_choi(tmp_path, thieu):
    t = tao(tmp_path, da_vao=True)
    if thieu in ("nguon", "kho"):
        t.n = replace(t.n, nguon_duyet=None if thieu == "nguon" else lambda _: NguonDuyet(None))
    elif thieu == "remote":
        git(t.kg, "remote", "remove", "origin")
    elif thieu == "nhanh":
        t.n = replace(t.n, nguon_duyet=lambda _: NguonDuyet(t.kg, "khong-co"))
    else:
        ghi_sk(t, "bead.vao_cot_3")
    tu_choi(t, "kho kiểm|fetch|nhánh chính|commit bàn giao")


def test_chi_dung_vao_cot_3_moi_nhat_sau_tra_ve(tmp_path):
    t = tao(tmp_path, da_vao=True)
    ghi_sk(t, "cot.tra_ve")
    tu_choi(t, "bead.vao_cot_3")
    ghi_sk(t, "bead.vao_cot_3", commit_ban_giao="b" * 40)
    tu_choi(t, "Commit chưa vào main")


@pytest.mark.parametrize("loi", ["gh", "khong-gh", "url"])
def test_khong_xac_minh_duoc_pr_khong_dong(tmp_path, loi):
    t = tao(tmp_path, pr="https://example.com/pull/7" if loi == "url" else URL)
    t.loi_gh = loi == "gh"
    if loi == "khong-gh":
        t.n = replace(t.n, nguon_duyet=lambda _: NguonDuyet(t.kg))
    tu_choi(t, "gh|PR")


def test_khong_tai_dung_pr_mo_cua_vong_cu(tmp_path):
    t = tao(tmp_path)
    ghi_sk(t, "pr.mo", loai="bead", commit=t.commit, url=URL, pr=7)
    ghi_sk(t, "cot.tra_ve")
    ghi_sk(t, "bead.vao_cot_3", commit_ban_giao="b" * 40)
    tu_choi(t, "trạm chưa mở PR")


@pytest.mark.parametrize("notes", ["", "<!-- ban-giao --> { sai json"])
def test_thieu_loi_ban_giao_van_can_bang_chung_commit(tmp_path, notes):
    t = tao(tmp_path, da_vao=True, notes=notes)
    bam(t)
    assert t.n.bd.beads["hr-2"].close_reason == f"Đại ca duyệt — commit {t.commit[:7]} đã vào main"


def test_retry_sau_close_khong_fetch_lai_va_khong_dong_hai_lan(tmp_path):
    t = tao(tmp_path, ra_loi_sau={"dong": 1})
    ghi_sk(t, "pr.mo", loai="bead", commit=t.commit, url=URL, pr=7)
    t.pr.update(state="MERGED", mergedAt=V)
    with pytest.raises(LoiBd):
        bam(t)
    t.n = replace(t.n, nguon_duyet=None)
    assert bam(t).ket_qua == {"dong": {"pr": URL}}
    assert bam(t).lap_lai and t.n.bd.so_lan("dong") == 1


def test_retry_truoc_close_van_kiem_bang_chung(tmp_path):
    t = tao(tmp_path, da_vao=True, ra_loi_truoc={"dong": 1})
    with pytest.raises(LoiBd):
        bam(t)
    git(t.remote, "update-ref", "refs/heads/main", t.dau)
    with pytest.raises(KhongHopLe, match="Commit chưa vào main"):
        bam(t)
    assert t.n.bd.beads["hr-2"].status == "open" and t.n.bd.goi == []


def test_chi_lay_vao_cot_3_moi_nhat_khong_lay_commit_cu_da_vao(tmp_path):
    t = tao(tmp_path, da_vao=True)
    ghi_sk(t, "bead.vao_cot_3", commit_ban_giao="b" * 40)
    tu_choi(t, "Commit chưa vào main")


@pytest.mark.parametrize("luc_doi", ["fetch", "gh"])
@pytest.mark.parametrize("loai", ["cot.tra_ve", "bead.vao_cot_3"])
def test_bang_chung_doi_trong_luc_xac_minh_khong_dong(tmp_path, monkeypatch, luc_doi, loai):
    from tram.thao_tac.duyet_merge import fetch
    t = tao(tmp_path, da_vao=luc_doi == "fetch", pr=URL)
    if luc_doi == "fetch":
        def doi(*a, **kw):
            fetch(*a, **kw)
            ghi_sk(t, loai, commit_ban_giao="b" * 40)
        monkeypatch.setattr("tram.thao_tac.duyet_merge.fetch", doi)
    else:
        t.pr.update(state="MERGED", mergedAt=V)
        gh = t.n.nguon_duyet("hr").gh
        xem = gh.xem_pr
        def doi(*a):
            ghi_sk(t, loai, commit_ban_giao="b" * 40)
            return xem(*a)
        monkeypatch.setattr(gh, "xem_pr", doi)
        t.n = replace(t.n, nguon_duyet=lambda _: NguonDuyet(t.kg, "main", gh))
    with pytest.raises(KhongHopLe, match="đã đổi"):
        bam(t)
    assert t.n.bd.goi == [] and t.n.kho_tt.lay(MA) is None


@pytest.mark.parametrize("doi_version", [False, True])
def test_bead_doi_trong_luc_fetch_khong_dong(tmp_path, monkeypatch, doi_version):
    from tram.thao_tac.duyet_merge import fetch
    t = tao(tmp_path, da_vao=True)
    def doi(*a, **kw):
        fetch(*a, **kw)
        b = t.n.bd.beads["hr-2"]
        t.n.bd.beads["hr-2"] = replace(b, **({"updated_at": "2026-10-21T01:00:00Z"}
                                             if doi_version else {"labels": ("cot:ai-lam",)}))
    monkeypatch.setattr("tram.thao_tac.duyet_merge.fetch", doi)
    with pytest.raises((KhongHopLe, XungDot)):
        bam(t)
    assert t.n.bd.goi == [] and t.n.kho_tt.lay(MA) is None
