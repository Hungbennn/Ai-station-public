"""TM-2 mốc 2.2, 2.4–2.6 (spec `tu-merge`; `dieu-khien-tu-dong` "Estop dừng cả tự merge", "Kiểm lại công tắc ngay
trước lúc merge"): vòng tick thật trên GitHub giả + Git cục bộ — cột 3 → PR → tự merge → xác minh → đóng bead; chờ
Đại ca kèm lý do (không ghi lặp); đọc lại cài đặt ngay trước lệnh — gồm tập file cấm từ ba lệnh (D89, Codex Q2);
đối soát khi kết quả không rõ; 3 lần lỗi."""
from dataclasses import replace

import pytest

from gh_gia import REPO, GhGia
from giao_viec_gia import TC, bug, dung
from git_gia import git
from su_kien_gia import cong_bo, ds, ket_thuc, kiem, nhan, qc, sk
from test_xet_xong import F, bg
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin
from tram.cau_hinh.du_an import HangRao
from tram.chu import estop
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.su_kien import SK
from tram.giao_viec.tu_merge_rao import cham_rao, doc_tep
from tram.giao_viec.tick import mot_vong_tick
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.tu_dong.luu import DU_AN_TRAM, doi_cai_dat, ghi_tam_dung

GIU = {"status": "in_progress", "assignee": "tram/giao-viec"}
TIEN = {"tien": HangRao(tu_khoa=("hoá đơn",), duong_dan=("*Modules/Fin/*",))}


def lam_merge(k):
    """Merge commit thường vào `main` của remote cục bộ `k` — như GitHub làm khi nhận `gh pr merge --merge`."""
    def lam(p):
        git(k.dev, "checkout", "-q", "-B", "main", git(k.origin, "rev-parse", "main"))
        git(k.dev, "merge", "-q", "--no-ff", "-m", f"Merge PR #{p.so}", p.head)
        git(k.dev, "push", "-q", "origin", "HEAD:refs/heads/main")
        return git(k.dev, "rev-parse", "HEAD")
    return lam


def doi(t, **kw):
    doi_cai_dat(t.kho.db, "hr-codex", lambda c: replace(c, **kw), tac_nhan="dai-ca/dashboard")


def dung_tu_merge(tmp_path, monkeypatch, *, bat=True, bat_ghi=True, hang_rao=None, tep=None, gh_kw=None, them=(),
                  cho_phep=(), **b_kw):
    """Bead `hr-1` sẵn sàng vào cột 3 (kiểm lại + QC khác khe đạt); `du-an/hr-codex.yaml` giả có `bat_ghi`; `them`:
    bead khác trong Beads giả; `cho_phep`: ngoại lệ đường cấm của dự án (`duong_dan_cam_cho_phep`)."""
    (goc := tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (goc / "hr-codex.yaml").write_text(f"ten: hr-codex\nbat_ghi: {'true' if bat_ghi else 'false'}\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    monkeypatch.setattr("tram.giao_viec.tu_merge_gui.cong_mo", lambda: True)
    t = dung(tmp_path, bug(**{**GIU, **b_kw}), *them)
    da = replace(t.da, hang_rao=TIEN if hang_rao is None else hang_rao,
                 giao=replace(t.da.giao, duong_dan_cam_cho_phep=cho_phep))
    t.bo.cac_du_an = lambda: [da]
    gh = GhGia(lambda nhanh: git(t.k.origin, "rev-parse", nhanh), lam_merge=lam_merge(t.k), **(gh_kw or {}))
    t.bo.p4c = PhuThuoc4c(gh=gh, github_repo=lambda kg: REPO)
    c = t.k.day("tram/hr-1", tep or {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    q = t.k.day("tram/hr-1", {F: "qc"}, tu=c)
    nhan(t.kho, "g-1", 1)
    cong_bo(t.kho, 1, c)
    ket_thuc(t.kho, "g-1", 1, commit=c)
    sk(t.kho, "bao.xong", {"giao_id": "g-1", "commit": c, "ban_giao": bg(c)})
    kiem(t.kho, "g-1", c, digest=digest_tieu_chi([TC]))
    nhan(t.kho, "g-2", 2, buoc="qc", khe_id="B/claude-2")                   # QC ở khe khác khe code (INV-006)
    cong_bo(t.kho, 2, q)
    qc(t.kho, "g-2", c, q)
    if bat:
        doi(t, tu_merge=True)
    return t, gh, q


def cot_3_co_pr(t, gh, ci="xanh"):
    r = mot_vong_tick(t.bo)
    assert (r["cot_3"], r["pr_mo"]) == (1, 1)
    gh.dat(1, ci=ci)


def tm(t, loai=None):
    return [s for s in ds(t.kho) if s.loai.startswith("tu_merge.") and (loai is None or s.loai == loai)]


def merge_goi(gh):
    return [g for g in gh.goi if g[0] == "merge_pr"]


def test_tu_merge_roi_xac_minh_dong_bead(tmp_path, monkeypatch):
    """Scenario "Merge xong, xác minh đạt" + "Tin tự merge"; mốc 2.4 luồng xác minh cũ vẫn chạy."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and gh.prs[1].trang_thai == "MERGED"
    assert merge_goi(gh) == [("merge_pr", REPO, 1, q)]
    bd, xong = tm(t)
    assert (bd.loai, bd.du_lieu["commit"], bd.du_lieu["pr"], bd.du_lieu["loai"], bd.du_lieu["lan"]) == (
        "tu_merge.bat_dau", q, 1, "code", 1)
    assert bd.du_lieu["ma_thao_tac"].startswith("tm-") and xong.du_lieu == {"ma_thao_tac": bd.du_lieu["ma_thao_tac"],
                                                                            "loai": "code"}
    assert mot_vong_tick(t.bo)["da_merge"] == 1 and t.g.beads["hr-1"].status == "closed"
    assert len(merge_goi(gh)) == 1 and len(tm(t)) == 2
    sk_xong = t.kho.db.execute("SELECT id, loai, tac_nhan, du_an, bead_id FROM su_kien WHERE loai = 'tu_merge.xong'"
                               ).fetchone()
    assert sk_xong[2] == "tram/tu-merge"
    ban = type("SK", (), {"loai": "tu_merge.xong", "du_an": "hr-codex", "bead_id": "hr-1", "du_lieu": xong.du_lieu,
                          "tac_nhan": sk_xong[2]})
    assert tin_tu_su_kien(ban, None) == [Tin("tu_merge", "hr-codex", "hr-1")]


def test_cong_tac_tat_khong_doc_github_khong_ghi_gi(tmp_path, monkeypatch):
    """Scenario "Dự án mới thêm vào trạm": công tắc tắt → như trước TM-2, chờ Đại ca merge tay."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, bat=False)
    cot_3_co_pr(t, gh)
    gh.goi.clear()
    assert "tu_merge" not in mot_vong_tick(t.bo)
    assert [g[0] for g in gh.goi] == ["xem_pr"] and tm(t) == [] and gh.prs[1].trang_thai == "OPEN"


def test_ci_cho_khong_ghi_lap_moi_vong(tmp_path, monkeypatch):
    """Mốc 2.5 + Scenario "CI đang chạy" (xét lại vòng sau, không lỗi), "CI đỏ"."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh, ci="dang_chay")
    for _ in range(3):
        r = mot_vong_tick(t.bo)
        assert "tu_merge" not in r and "loi_gh" not in r and "loi" not in r
    assert [s.du_lieu for s in tm(t)] == [{"ly_do": ["ci_dang_chay"], "commit": q}]
    gh.dat(1, ci="do")
    mot_vong_tick(t.bo)
    mot_vong_tick(t.bo)
    assert [s.du_lieu["ly_do"] for s in tm(t)] == [["ci_dang_chay"], ["ci_do"]] and merge_goi(gh) == []
    assert {r[0] for r in t.kho.db.execute("SELECT tac_nhan FROM su_kien WHERE loai LIKE 'tu_merge.%'")} == {
        "tram/tu-merge"}
    gh.dat(1, ci="xanh")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1


@pytest.mark.parametrize("bam, ly_do", [
    (lambda t: ghi_tam_dung(t.kho.db, "hr-codex", tam_dung=True, tac_nhan="dai-ca/dashboard"), ["tam_dung_du_an"]),
    (lambda t: ghi_tam_dung(t.kho.db, DU_AN_TRAM, tam_dung=True, tac_nhan="dai-ca/dashboard"), ["tam_dung_tram"]),
    (lambda t: doi(t, tu_merge=False), ["tu_merge_tat"]),
    (lambda t: doi(t, dk_hang_rao=False), []),                                   # đổi không chặn → vẫn merge
    (lambda t: estop.bat("thử"), ["estop"]),
    (lambda t: (t.k.kho.parent / "repo-tram" / "du-an" / "hr-codex.yaml").write_text(
        "ten: hr-codex\nbat_ghi: false\n"), ["bat_ghi"]),
])
def test_doc_lai_ngay_truoc_lenh_merge(tmp_path, monkeypatch, bam, ly_do):
    """Scenario "Đại ca bấm tạm dừng giữa vòng tick", "Estop bật", "Dự án chỉ quét thử": thay đổi xảy ra SAU khi
    trạm bắt đầu xét (trong lúc chờ `gh pr view`) vẫn chặn lệnh merge."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    lan = []
    gh.khi_xem = lambda so: lan or (lan.append(1), bam(t))
    try:
        mot_vong_tick(t.bo)
    finally:
        estop.tat()
    if not ly_do:
        assert len(merge_goi(gh)) == 1
        return
    assert merge_goi(gh) == [] and gh.prs[1].trang_thai == "OPEN"
    assert [s.du_lieu["ly_do"] for s in tm(t, "tu_merge.cho")] == [ly_do]


@pytest.mark.parametrize("lenh", ["sh scripts/deploy.sh", "/r/scripts/deploy.sh", "sh ./src/../scripts/deploy.sh",
                                  "deploy --file=scripts/deploy.sh", "make -C scripts"])
def test_doi_lenh_trong_luc_doc_pr_thi_cho_file_lenh(tmp_path, monkeypatch, lenh):
    """Codex Q2 + C2 (D89 tại cửa merge): PR sửa `scripts/deploy.sh`; QC, kiểm lại đã đạt khi ba lệnh còn trống. Trong
    lúc trạm chờ `gh pr view`, Đại ca khai lệnh dùng đúng file đó (tương đối, tuyệt đối theo gốc dự án, sau `=`, cả
    thư mục) → không merge, chờ `file_lenh` — dấu QC cũ không đủ; dự án miễn đúng file đó ở `duong_dan_cam_cho_phep`
    cũng không miễn được tập bắt buộc này. Lệnh đổi sang file PR không sửa → merge."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, tep={"scripts/deploy.sh": "echo 2\n"},
                             cho_phep=("scripts/deploy.sh",))
    cot_3_co_pr(t, gh)
    gh.khi_xem = lambda so: doi(t, lenh_deploy=lenh)
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == [] and [s.du_lieu["ly_do"] for s in tm(t, "tu_merge.cho")] == [["file_lenh"]]
    gh.khi_xem = lambda so: doi(t, lenh_deploy="sh kiem.sh")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and merge_goi(gh) == [("merge_pr", REPO, 1, q)]


def test_doi_lenh_trong_luc_doc_cay_git_thi_cho(tmp_path, monkeypatch):
    from tram.giao_viec import tu_merge_rao

    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, tep={"scripts/deploy.sh": "echo 2\n"})
    cot_3_co_pr(t, gh)
    doi(t, lenh_deploy="sh kiem.sh")
    doc = tu_merge_rao._cay

    def doi_khi_doc(*args):
        doi(t, lenh_deploy="sh scripts/deploy.sh")
        return doc(*args)
    monkeypatch.setattr(tu_merge_rao, "_cay", doi_khi_doc)
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == []
    assert tm(t, "tu_merge.cho")[-1].du_lieu["ly_do"] == ["file_lenh_loi"]


def test_lenh_tuyet_doi_trong_worktree_deploy_van_cam_merge(tmp_path, monkeypatch):
    """Review vòng 2: cùng file ở gốc deploy cũng thuộc repo, kể cả lệnh đổi sau QC."""
    from tram.duong_dan import tram_home

    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, tep={"scripts/deploy.sh": "echo 2\n"},
                             cho_phep=("scripts/deploy.sh",))
    cot_3_co_pr(t, gh)
    p = tram_home() / "kho-deploy" / "hr-codex" / "scripts" / "deploy.sh"
    gh.khi_xem = lambda so: doi(t, lenh_deploy=f'sh "{p}"')
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == []
    assert tm(t, "tu_merge.cho")[-1].du_lieu["ly_do"] == ["file_lenh"]


def test_tam_dung_roi_tiep_tuc(tmp_path, monkeypatch):
    """Scenario "Tạm dừng rồi tiếp tục" (phần tự merge): công tắc vẫn như cũ sau Tiếp tục."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    ghi_tam_dung(t.kho.db, "hr-codex", tam_dung=True, tac_nhan="dai-ca/dashboard")
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == []
    ghi_tam_dung(t.kho.db, "hr-codex", tam_dung=False, tac_nhan="dai-ca/dashboard")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1


def test_tram_tat_ngay_sau_lenh_merge_thi_doi_soat(tmp_path, monkeypatch):
    """Scenario "Trạm tắt ngay sau lệnh merge": vòng sau đọc PR — đã merge → đi tiếp xác minh, không gửi lại."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, gh_kw={"mat_phan_hoi_khi_merge": True})
    cot_3_co_pr(t, gh)
    assert mot_vong_tick(t.bo)["loi_gh"] == 1 and [s.loai for s in tm(t)] == ["tu_merge.bat_dau"]
    gh.mat_merge = False
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and [s.loai for s in tm(t)] == ["tu_merge.bat_dau", "tu_merge.xong"]
    assert mot_vong_tick(t.bo)["da_merge"] == 1 and len(merge_goi(gh)) == 1


def test_con_mo_thi_gui_lai_cung_commit_ba_lan_roi_loi(tmp_path, monkeypatch):
    """Mốc 2.4: lỗi `gh` → vòng sau đọc PR, còn mở + vẫn đủ điều kiện → gửi lại ĐÚNG commit; 3 lần → `tu_merge.loi`,
    ngừng thử, báo "trạm lỗi"; PR vẫn mở cho Đại ca merge tay."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, gh_kw={"loi_merge": True})
    cot_3_co_pr(t, gh)
    assert [mot_vong_tick(t.bo).get("loi_gh") for _ in range(3)] == [1, 1, 1]
    assert not tm(t, "tu_merge.loi")
    assert mot_vong_tick(t.bo)["tu_merge_loi"] == 1             # đọc lại OPEN trước khi kết luận lỗi
    assert merge_goi(gh) == [("merge_pr", REPO, 1, q)] * 3
    assert [s.du_lieu.get("lan") for s in tm(t, "tu_merge.bat_dau")] == [1, 2, 3]
    [loi] = tm(t, "tu_merge.loi")
    assert loi.du_lieu["ma_loi"] == "gh-loi-3-lan" and gh.prs[1].trang_thai == "OPEN"
    mot_vong_tick(t.bo)
    assert len(merge_goi(gh)) == 3 and len(tm(t, "tu_merge.loi")) == 1
    gh.dat(1, trang_thai="MERGED", merge_commit=lam_merge(t.k)(gh.prs[1]))          # Đại ca merge tay
    assert mot_vong_tick(t.bo)["da_merge"] == 1


def test_lan_ba_mat_phan_hoi_van_doi_soat_thanh_cong(tmp_path, monkeypatch):
    """Lần thứ ba cũng có thể đã merge dù CLI báo lỗi: không kết luận lỗi trước khi đọc lại PR."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, gh_kw={"loi_merge": True})
    cot_3_co_pr(t, gh)
    assert mot_vong_tick(t.bo)["loi_gh"] == 1
    assert mot_vong_tick(t.bo)["loi_gh"] == 1
    gh.loi_merge, gh.mat_merge = False, True
    assert mot_vong_tick(t.bo)["loi_gh"] == 1
    assert gh.prs[1].trang_thai == "MERGED" and not tm(t, "tu_merge.loi")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1
    assert len(tm(t, "tu_merge.xong")) == 1 and len(merge_goi(gh)) == 3
    assert mot_vong_tick(t.bo)["da_merge"] == 1


def test_dau_pr_doi_hay_pr_dong(tmp_path, monkeypatch):
    """Scenario "Đầu PR đổi sau khi kiểm"; PR đã gửi lệnh mà bị đóng → `tu_merge.loi`."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    gh.dat(1, head="d" * 40)
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == [] and tm(t, "tu_merge.cho")[-1].du_lieu["ly_do"] == ["dau_pr_khac"]
    t2, gh2, _ = dung_tu_merge(tmp_path / "b", monkeypatch, gh_kw={"mat_phan_hoi_khi_merge": True})
    cot_3_co_pr(t2, gh2)
    gh2.lam_merge = None
    mot_vong_tick(t2.bo)
    gh2.dat(1, trang_thai="CLOSED")
    assert mot_vong_tick(t2.bo)["tu_merge_loi"] == 1
    assert tm(t2, "tu_merge.loi")[0].du_lieu["ma_loi"] == "pr-da-dong"


@pytest.mark.parametrize("canh, kw, nut, ly_do", [
    ("Diff chạm đường dẫn tiền", {"tep": {"erp/app/Modules/Fin/So.php": "x\n"}}, {}, ["hang_rao_tien"]),
    ("Tắt nút hàng rào thì merge", {"tep": {"erp/app/Modules/Fin/So.php": "x\n"}}, {"dk_hang_rao": False}, []),
    ("Việc chỉ nhắc từ khoá", {"description": "Sửa hoá đơn hiển thị sai"}, {}, []),
    ("Tắt nút hàng rào vẫn chặn migration",
     {"tep": {"db/migrations/001.sql": "alter\n"}, "hang_rao": {"schema": HangRao(duong_dan=("db/migrations/*",))}},
     {"dk_hang_rao": False}, ["schema_duong_dan"]),
    ("Việc nói tới xoá dữ liệu",
     {"description": "Xoá dữ liệu khách cũ", "hang_rao": {"schema": HangRao(tu_khoa=("xoá dữ liệu",))}},
     {"dk_hang_rao": False}, ["schema_tu_khoa"]),
    ("Đại ca đã tự gán cột", {"labels": ["cot:ai-lam", "cot-khoa"]}, {}, ["cot"]),
    ("Tắt nút cột", {"labels": ["cot:ai-lam", "cot-khoa"]}, {"dk_cot": False}, []),
    ("Repo chưa có CI, nút CI bật", {}, {"ci": "rong"}, ["ci_rong"]),
    ("Cờ CI cũ không miễn khoá", {}, {"ci": "rong", "dk_ci": False}, ["ci_rong"]),
])
def test_dieu_kien_tren_du_lieu_that(tmp_path, monkeypatch, canh, kw, nut, ly_do):
    """Mốc 2.6: hàng rào chỉ theo đường dẫn diff (D91); `schema` theo đường dẫn + từ khoá, không theo nút (D76, D92,
    D112); cột theo `cot-khoa` (D90); CI rỗng = chưa xanh (D93)."""
    ci = nut.pop("ci", "xanh")
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, **kw)
    if nut:
        doi(t, **nut)
    cot_3_co_pr(t, gh, ci=ci)
    mot_vong_tick(t.bo)
    assert [s.du_lieu["ly_do"] for s in tm(t, "tu_merge.cho")] == ([ly_do] if ly_do else [])
    assert len(merge_goi(gh)) == (0 if ly_do else 1)


def test_khong_doc_duoc_diff_thi_luon_cho(tmp_path, monkeypatch):
    """Commit không có trong kho kiểm → không biết diff chạm gì → chờ Đại ca, không theo nút (như D76)."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, bat=False)
    da, b, v = t.bo.cac_du_an()[0], t.g.beads["hr-1"], SK(1, "bead.vao_cot_3", {"commit_ban_giao": "f" * 40}, "")
    assert doc_tep(t.k.kho, da, "f" * 40) is None and cham_rao(da, b, v, None) == (("diff_loi",), ())
    fetch(t.k.kho)
    assert cham_rao(da, b, replace(v, du_lieu={"commit_ban_giao": q}), doc_tep(t.k.kho, da, q)) == ((), ())
