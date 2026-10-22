"""Adapter `gh` (lát 4c): đọc/mở PR, kiểm dạng JSON; TM-2 (design D-3): merge đúng MỘT dạng chặt, đọc CI ở `view`.
`gh` thật KHÔNG chạy."""
import json
import re
from pathlib import Path

import pytest

from git_gia import git, tao_repo
from tram.giao_viec.gh import LENH_DUOC_PHEP, GhCli, LoiGh, repo_github_cua

R, H = "dai-ca/hr-codex", "a" * 40


def pr(so=7, **kw):
    d = {"number": so, "url": f"https://github.com/{R}/pull/{so}", "state": "OPEN", "headRefName": "tram/hr-1",
         "headRefOid": H, "baseRefName": "main", "isCrossRepository": False, "mergedAt": None, "mergeCommit": None}
    return {**d, **kw}


class Chay:
    def __init__(self, *ra):
        self.ra, self.goi = list(ra), []

    def __call__(self, argv, dau_vao):
        self.goi.append((argv, dau_vao))
        return self.ra.pop(0)


def test_ds_pr_doc_dung_truong_va_lenh():
    c = Chay((0, json.dumps([pr(), pr(8, state="MERGED", mergeCommit={"oid": "b" * 40})]), ""))
    ds = GhCli(c).ds_pr(R, "tram/hr-1")
    assert [(p.so, p.trang_thai, p.merge_commit) for p in ds] == [(7, "OPEN", None), (8, "MERGED", "b" * 40)]
    argv = c.goi[0][0]
    assert argv[:3] == ["gh", "pr", "list"] and argv[argv.index("--head") + 1] == "tram/hr-1"
    assert argv[argv.index("--repo") + 1] == R and argv[argv.index("--state") + 1] == "all"


@pytest.mark.parametrize("sai", [{"url": "https://evil.example/pull/7"}, {"state": "DRAFT"}, {"headRefOid": "abc"},
                                 {"number": "7"}, {"mergeCommit": {"oid": "x"}}, {"isCrossRepository": "no"}])
def test_pr_sai_dang_bi_tu_choi(sai):
    with pytest.raises(LoiGh):
        GhCli(Chay((0, json.dumps([pr(**sai)]), ""))).ds_pr(R, "tram/hr-1")


def test_loi_va_khong_phai_json():
    with pytest.raises(LoiGh, match="lỗi 1"):
        GhCli(Chay((1, "", "HTTP 401"))).xem_pr(R, 7)
    with pytest.raises(LoiGh):
        GhCli(Chay((0, "not json", ""))).xem_pr(R, 7)
    with pytest.raises(LoiGh):
        GhCli(Chay()).ds_pr("evil repo; rm", "tram/hr-1")


def test_xem_pr_giu_merged_at_de_duyet_tay_squash():
    luc = "2026-10-21T01:00:00Z"
    p = GhCli(Chay((0, json.dumps(pr(state="MERGED", mergedAt=luc)), ""))).xem_pr(R, 7)
    assert getattr(p, "merged_at", None) == luc


def test_tao_pr_qua_stdin_khong_shell():
    c = Chay((0, f"https://github.com/{R}/pull/9\n", ""))
    GhCli(c).tao_pr(R, "tram/hr-1", "main", "-hr-1: tiêu đề bắt đầu bằng gạch", "thân @ai $(rm -rf /)")
    argv, dau_vao = c.goi[0]
    assert argv[:3] == ["gh", "pr", "create"] and "--title=-hr-1: tiêu đề bắt đầu bằng gạch" in argv
    assert argv[argv.index("--body-file") + 1] == "-" and dau_vao == "thân @ai $(rm -rf /)"


def test_merge_chi_mot_dang_chat():
    """Mốc 2.3: chỉ `gh pr merge <so> --repo <r> --merge --match-head-commit <sha>`; cờ khác không bao giờ chạy."""
    assert LENH_DUOC_PHEP == {"list", "view", "create", "merge"}
    c = Chay((0, "", ""))
    GhCli(c).merge_pr(R, 7, H)
    assert c.goi == [(["gh", "pr", "merge", "7", "--repo", R, "--merge", "--match-head-commit", H], None)]
    for co in ("--admin", "--squash", "--rebase", "--auto", "--delete-branch"):
        with pytest.raises(LoiGh, match="không được phép"):
            GhCli(Chay())._gh("merge", "7", "--repo", R, "--merge", "--match-head-commit", H, co)
        with pytest.raises(LoiGh, match="không được phép"):
            GhCli(Chay())._gh("merge", "7", "--repo", R, co, "--match-head-commit", H)
    for sai in (("7", "--repo", R, "--merge"), ("07", "--repo", R, "--merge", "--match-head-commit", H),
                ("7", "--repo", "a b", "--merge", "--match-head-commit", H), ("7", "--repo", R, "--merge",
                                                                              "--match-head-commit", "abc")):
        with pytest.raises(LoiGh, match="không được phép"):
            GhCli(Chay())._gh("merge", *sai)
    for so, commit in ((0, H), ("7", H), (7, "B" * 40)):
        with pytest.raises(LoiGh, match="tham số"):
            GhCli(Chay()).merge_pr(R, so, commit)
    with pytest.raises(LoiGh, match="lỗi 1"):
        GhCli(Chay((1, "", "Pull request is not mergeable"))).merge_pr(R, 7, H)
    goc = Path(__file__).resolve().parents[1] / "tram"
    for f in goc.rglob("*.py"):
        assert not re.search(r"--(admin|squash|rebase|auto|delete-branch)\b", f.read_text()), f


def test_xem_pr_doc_ci_tren_dau_pr():
    xanh = [{"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS"}]
    c = Chay((0, json.dumps(pr(statusCheckRollup=xanh)), ""), (0, json.dumps([pr()]), ""))
    assert GhCli(c).xem_pr(R, 7).ci is None
    argv = c.goi[0][0]
    assert argv[:4] == ["gh", "pr", "view", "7"] and "statusCheckRollup" not in argv[argv.index("--json") + 1]
    assert GhCli(c).ds_pr(R, "tram/hr-1")[0].ci is None                     # `list` không đọc CI
    assert GhCli(Chay((0, json.dumps(pr(statusCheckRollup="lạ")), ""))).xem_pr(R, 7).ci is None


@pytest.mark.parametrize("url,ky_vong", [
    ("https://github.com/dai-ca/hr-codex.git", "dai-ca/hr-codex"),
    ("git@github.com:dai-ca/hr-codex.git", "dai-ca/hr-codex"),
    ("ssh://git@github.com/dai-ca/hr-codex", "dai-ca/hr-codex"), ("https://gitlab.com/dai-ca/hr-codex.git", None),
    ("/tmp/origin.git", None), ("https://github.com.evil.io/a/b", None)])
def test_repo_github_tu_remote(tmp_path, url, ky_vong):
    k = tao_repo(tmp_path / "k")
    git(k, "remote", "add", "origin", url)
    assert repo_github_cua(k) == ky_vong
