"""TM-2 mốc 2.7 (spec `tu-merge` "Tự gộp PR spec đã được Đại ca duyệt", D95, design D-11): bước GitHub của feature
`theo-plan` — mở PR spec rồi tự gộp khi dự án bật; sau đó điều kiện 8 của spec 4 §5.1 thấy commit đã vào nhánh chính.
GitHub giả + Git cục bộ."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from bd_gia import BdGia
from bead_gia import bead
from gh_gia import REPO, GhGia
from git_gia import git
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, kho_tam
from su_kien_gia import cong_bo, ds, sk
from test_tu_merge import lam_merge
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.tick_github import buoc_github
from tram.giao_viec.tu_merge import tu_merge_spec
from tram.tu_dong.luu import doi_cai_dat

DA = DuAn("hr-codex", Path("/r"), None, {})
F = bead("hr-f", issue_type="feature", title="Hoa hồng tạm tính", labels=["theo-plan"])


def dung_spec(tmp_path, monkeypatch, *, bat=True):
    (goc := tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (goc / "hr-codex.yaml").write_text("ten: hr-codex\nbat_ghi: true\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    monkeypatch.setattr("tram.giao_viec.tu_merge_gui.cong_mo", lambda: True)
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    s = k.day("tram/spec-hr-f", {"docs/specs/x.md": "spec\n"}, tu=k.main)
    fetch(k.kho)
    cong_bo(kho, 1, s, bead_id="hr-f")
    sk(kho, "spec.duyet", {"feature": "hr-f", "commit": s, "digest_bead": "sha256:b", "bead_moi": [],
                           "ma_thao_tac": "dy-1"}, bead_id="hr-f")
    gh = GhGia(lambda nhanh: git(k.origin, "rev-parse", nhanh), lam_merge=lam_merge(k))
    bo = SimpleNamespace(p4c=PhuThuoc4c(gh=gh, github_repo=lambda kg: REPO))
    if bat:
        doi_cai_dat(kho.db, "hr-codex", lambda c: replace(c, tu_merge=True), tac_nhan="dai-ca/dashboard")
    bd = BdGia([F])
    chay = lambda: buoc_github(bo, kho, DA, bd, [F], k.kho, LUC)        # noqa: E731
    chay.bd = bd
    return k, kho, gh, s, chay


def tm(kho, loai):
    return [e for e in ds(kho, "hr-f") if e.loai == loai]


def test_duyet_spec_xong_thi_pr_spec_tu_vao_nhanh_chinh(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    assert chay() == {"pr_mo": 1}
    assert chay() == {"tu_merge": 1} and gh.prs[1].trang_thai == "MERGED"
    assert [g for g in gh.goi if g[0] == "merge_pr"] == [("merge_pr", REPO, 1, s)]
    assert [e.du_lieu["loai"] for e in tm(kho, "tu_merge.xong")] == ["spec"]
    fetch(k.kho)
    assert feature_da_merge(kho, DA, [F], k.kho) == {"hr-f"}                 # điều kiện 8: việc con được giao
    assert chay() == {} and len([g for g in gh.goi if g[0] == "merge_pr"]) == 1


def test_nhanh_spec_doi_sau_khi_duyet_thi_cho(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    chay()
    gh.dat(1, head="e" * 40)
    assert chay() == {} and gh.prs[1].trang_thai == "OPEN"
    assert [e.du_lieu["ly_do"] for e in tm(kho, "tu_merge.cho")] == [["dau_pr_khac"]]


def test_cong_tac_tat_thi_pr_spec_cho_dai_ca(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch, bat=False)
    assert chay() == {"pr_mo": 1} and chay() == {}
    assert gh.prs[1].trang_thai == "OPEN" and not [e for e in ds(kho, "hr-f") if e.loai.startswith("tu_merge.")]


def test_dai_ca_gop_tay_truoc_thi_khong_doc_lai(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch, bat=False)
    chay()
    gh.dat(1, trang_thai="MERGED", merge_commit=lam_merge(k)(gh.prs[1]))
    fetch(k.kho)
    doi_cai_dat(kho.db, "hr-codex", lambda c: replace(c, tu_merge=True), tac_nhan="dai-ca/dashboard")
    gh.goi.clear()
    assert chay() == {} and gh.goi == [] and not tm(kho, "tu_merge.xong")


def test_feature_chua_duyet_spec_khong_lam_gi(tmp_path, monkeypatch):
    """Scenario "Feature chưa duyệt spec": không có `spec.duyet` → không đọc GitHub, không merge gì."""
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    cho = bead("hr-g", issue_type="feature", labels=["cho-duyet-spec", "theo-plan"])
    assert tu_merge_spec(gh, REPO, kho, k.kho, DA, chay.bd, cho, [], LUC) is None and gh.goi == []


def test_pr_spec_sua_file_lenh_thi_cho(tmp_path, monkeypatch):
    """Codex Q2 (D89 tại cửa merge, cả PR spec): lệnh kiểm còn sống dùng file mà nhánh spec tạo → chờ `file_lenh`,
    không merge dù Đại ca đã duyệt spec; tập này không theo nút."""
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    chay()
    doi_cai_dat(kho.db, "hr-codex", lambda c: replace(c, lenh_kiem_song="sh docs/specs/x.md"),
                tac_nhan="dai-ca/dashboard")
    assert chay() == {} and gh.prs[1].trang_thai == "OPEN"
    assert [e.du_lieu["ly_do"] for e in tm(kho, "tu_merge.cho")] == [["file_lenh"]]
