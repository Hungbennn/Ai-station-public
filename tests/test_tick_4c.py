"""Vòng tick với lát 4c (spec 4 §6.4, §6.5): cột 3 → PR → Đại ca merge trên GitHub → trạm xác minh → đóng bead →
`bead.dong`; cờ đỏ gitnexus; estop không chạm GitHub; lỗi `gh` được đếm. GitHub/gitnexus giả, Git cục bộ."""
from dataclasses import replace

from gh_gia import REPO, GhGia
from giao_viec_gia import TC, bug, dung
from gitnexus_gia import GnGia
from git_gia import git
from su_kien_gia import cong_bo, ds, ket_thuc, kiem, nhan, qc, sk
from test_xet_xong import F, bg
from tram.cau_hinh.du_an import HangRao
from tram.chu import estop
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.tick import mot_vong_tick
from tram.giao_viec.tieu_chi import digest_tieu_chi

GIU = {"status": "in_progress", "assignee": "tram/giao-viec"}


def san_sang_cot_3(tmp_path, gh_kw=None, gn=None):
    t = dung(tmp_path, bug(**GIU))
    da = replace(t.da, gitnexus_repo="hr-interview-copilot", hang_rao={"tien": HangRao(duong_dan=("*Modules/Fin/*",))})
    t.bo.cac_du_an = lambda: [da]
    gh = GhGia(lambda nhanh: git(t.k.origin, "rev-parse", nhanh), **(gh_kw or {}))
    t.bo.p4c = PhuThuoc4c(gh=gh, github_repo=lambda kg: REPO, gitnexus=gn)
    c = t.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    q = t.k.day("tram/hr-1", {F: "qc"}, tu=c)
    nhan(t.kho, "g-1", 1)
    cong_bo(t.kho, 1, c)
    ket_thuc(t.kho, "g-1", 1, commit=c)
    sk(t.kho, "bao.xong", {"giao_id": "g-1", "commit": c, "ban_giao": bg(c)})
    kiem(t.kho, "g-1", c, digest=digest_tieu_chi([TC]))
    cong_bo(t.kho, 2, q)
    qc(t.kho, "g-2", c, q)
    return t, gh, q


def merge_tren_github(t, gh, head):
    git(t.k.dev, "checkout", "-q", "-B", "main", git(t.k.origin, "rev-parse", "main"))
    git(t.k.dev, "merge", "-q", "--no-ff", "-m", "Merge PR #1", head)
    git(t.k.dev, "push", "-q", "origin", "HEAD:refs/heads/main")
    gh.dat(1, trang_thai="MERGED", merge_commit=git(t.k.dev, "rev-parse", "HEAD"))


def test_cot_3_pr_merge_dong_bead(tmp_path):
    t, gh, q = san_sang_cot_3(tmp_path, gn=GnGia({"erp/app/Modules/Fin/So.php"}))
    r = mot_vong_tick(t.bo)
    assert (r["cot_3"], r["pr_mo"]) == (1, 1) and "co-do" in t.g.beads["hr-1"].labels
    assert gh.prs[1].head == q and t.g.beads["hr-1"].notes.count(f"https://github.com/{REPO}/pull/1") >= 1
    assert "da_merge" not in mot_vong_tick(t.bo)                       # Đại ca chưa merge
    merge_tren_github(t, gh, q)
    assert mot_vong_tick(t.bo)["da_merge"] == 1 and t.g.beads["hr-1"].status == "closed"
    assert mot_vong_tick(t.bo)["bead_dong"] == 1 and "bead_dong" not in mot_vong_tick(t.bo)   # bước 3 ở vòng sau
    assert [s.loai for s in ds(t.kho) if s.loai in ("pr.mo", "pr.da_merge", "bead.dong")] == [
        "pr.mo", "pr.da_merge", "bead.dong"]


def test_estop_khong_cham_github(tmp_path):
    t, gh, _ = san_sang_cot_3(tmp_path)
    estop.bat("thử")
    try:
        mot_vong_tick(t.bo)
        assert gh.goi == []
    finally:
        estop.tat()


def test_gh_loi_duoc_dem_cot_3_van_vao(tmp_path):
    t, gh, _ = san_sang_cot_3(tmp_path, gh_kw={"loi": True})
    r = mot_vong_tick(t.bo)
    assert (r["cot_3"], r["loi_gh"]) == (1, 1) and t.g.beads["hr-1"].labels == ("cot:cho-review",)


def test_chua_noi_gh_hoac_remote_khong_phai_github(tmp_path):
    t, gh, _ = san_sang_cot_3(tmp_path)
    t.bo.p4c = PhuThuoc4c(gh=gh, github_repo=lambda kg: None)
    assert "pr_mo" not in mot_vong_tick(t.bo) and gh.goi == []
    t.bo.p4c = PhuThuoc4c()
    assert "pr_mo" not in mot_vong_tick(t.bo)
