"""Adapter `gh` (GitHub CLI) cho lát 4c (spec 4 §6.4 mục 4, §6.5; kiến trúc Q7): đọc PR, mở PR, và (TM-2, D-3)
merge đúng MỘT dạng chặt khi dự án bật tự merge (`gh_tu_merge.dang_merge`). Không đóng hay sửa PR. Lệnh chạy
bằng danh sách đối số, không qua shell, không hỏi tương tác. Hình dạng JSON của `gh pr list/view/merge` theo tài
liệu gh 2.x — CHỜ S7 kiểm trên repo nháp (tài khoản trạm đã `gh auth login`); test dùng bản giả `chay`."""
import json
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.giao_viec.gh_tu_merge import REPO_RE, SHA_RE, dang_merge, la_dang_merge
from tram.giao_viec.git_kiem import GIT

TRUONG = "number,url,state,headRefName,headRefOid,baseRefName,isCrossRepository,mergedAt,mergeCommit"
TRUONG_XEM = TRUONG                    # CI trên đầu PR (D-2) — chỉ `view`
LENH_DUOC_PHEP = frozenset({"list", "view", "create", "merge"})   # `merge`: chỉ dạng `la_dang_merge` (test khoá)
REMOTE_RE = re.compile(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
                       r"([A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}?)(?:\.git)?/?")
Chay = Callable[[list[str], str | None], tuple[int, str, str]]


class LoiGh(RuntimeError):
    """`gh` lỗi, quá hạn, hoặc trả dữ liệu sai dạng — người gọi thử lại ở vòng tick sau."""


@dataclass(frozen=True)
class PrInfo:
    so: int
    url: str
    trang_thai: str          # OPEN | CLOSED | MERGED
    nhanh: str               # headRefName
    head: str                # headRefOid
    base: str
    ngoai_repo: bool
    merge_commit: str | None
    ci: str | None = None    # xanh | do | dang_chay | rong (kết luận cổng GitHub); None: lệnh không đọc CI
    merged_at: str | None = None     # mergedAt — bằng chứng Duyệt tay sau squash/rebase


def chay_gh(argv: list[str], dau_vao: str | None) -> tuple[int, str, str]:
    env = {**os.environ, "GH_PROMPT_DISABLED": "1", "GH_NO_UPDATE_NOTIFIER": "1", "NO_COLOR": "1",
           "GH_SPINNER_DISABLED": "1"}
    try:
        kq = subprocess.run(argv, input=dau_vao, capture_output=True, text=True, timeout=60, env=env)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise LoiGh(f"không chạy được gh: {type(e).__name__}") from None
    return kq.returncode, kq.stdout, kq.stderr


def repo_github_cua(kho_git: Path) -> str | None:
    """`owner/repo` từ remote `origin` của kho kiểm (github.com — #2); remote khác → None (không mở PR)."""
    kq = subprocess.run([*GIT, "-C", str(kho_git), "remote", "get-url", "origin"], capture_output=True, text=True)
    m = REMOTE_RE.fullmatch(kq.stdout.strip()) if kq.returncode == 0 else None
    return m.group(1) if m else None


def _pr(d: object, repo: str) -> PrInfo:
    try:
        so, mc = d["number"], d["mergeCommit"]
        pr = PrInfo(so, d["url"], d["state"], d["headRefName"], d["headRefOid"], d["baseRefName"],
                    d["isCrossRepository"], mc["oid"] if mc else None,
                    None, d.get("mergedAt"))
    except (TypeError, KeyError) as e:
        raise LoiGh(f"gh trả PR sai dạng: {type(e).__name__}") from None
    if (type(so) is not int or so <= 0 or pr.url != f"https://github.com/{repo}/pull/{so}"
            or pr.trang_thai not in ("OPEN", "CLOSED", "MERGED") or not SHA_RE.fullmatch(str(pr.head))
            or type(pr.ngoai_repo) is not bool or not isinstance(pr.nhanh, str) or not isinstance(pr.base, str)
            or (pr.merged_at is not None and (not isinstance(pr.merged_at, str) or not pr.merged_at))
            or (pr.merge_commit is not None and not SHA_RE.fullmatch(str(pr.merge_commit)))):
        raise LoiGh("gh trả PR sai dạng")
    return pr


class GhCli:
    def __init__(self, chay: Chay = chay_gh):
        self._chay = chay

    def _gh(self, lenh: str, *args: str, dau_vao: str | None = None) -> str:
        if lenh not in LENH_DUOC_PHEP or (lenh == "merge" and not la_dang_merge(args)):
            raise LoiGh(f"gh pr {lenh}: không được phép")
        ma, ra, loi = self._chay(["gh", "pr", lenh, *args], dau_vao)
        if ma != 0:
            raise LoiGh(f"gh pr {lenh} lỗi {ma}")
        return ra

    def ds_pr(self, repo: str, nhanh: str) -> list[PrInfo]:
        """Mọi PR (mọi trạng thái) có head là `nhanh` trong `repo`."""
        if not REPO_RE.fullmatch(repo):
            raise LoiGh("tên repo không hợp lệ")
        ra = self._gh("list", "--repo", repo, "--head", nhanh, "--state", "all", "--limit", "20", "--json", TRUONG)
        try:
            ds = json.loads(ra)
        except ValueError:
            raise LoiGh("gh pr list không trả JSON") from None
        if not isinstance(ds, list):
            raise LoiGh("gh pr list không trả mảng")
        return [_pr(d, repo) for d in ds]

    def xem_pr(self, repo: str, so: int) -> PrInfo:
        try:
            return _pr(json.loads(self._gh("view", str(so), "--repo", repo, "--json", TRUONG_XEM)), repo)
        except ValueError:
            raise LoiGh("gh pr view không trả JSON") from None

    def tao_pr(self, repo: str, nhanh: str, base: str, tieu_de: str, than: str) -> None:
        """Kết quả không rõ (lỗi sau khi GitHub đã nhận) → người gọi đối soát bằng `ds_pr`, không tạo lại mù."""
        self._gh("create", "--repo", repo, "--head", nhanh, "--base", base, f"--title={tieu_de}",
                 "--body-file", "-", dau_vao=than)

    def cong_merge(self, repo: str, pr: PrInfo) -> str:
        from tram.giao_viec.gh_bao_ve import cong_merge
        return cong_merge(self._chay, repo, pr)

    def merge_pr(self, repo: str, so: int, commit: str) -> None:
        """Lỗi hay không rõ → `LoiGh`; người gọi ĐỌC LẠI PR trước khi gửi lại (spec `tu-merge`, design D-7)."""
        if (args := dang_merge(repo, so, commit)) is None:
            raise LoiGh("gh pr merge: tham số không hợp lệ")
        self._gh("merge", *args)
