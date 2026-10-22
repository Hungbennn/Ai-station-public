"""Bản chép kiểm là repo git MỘT commit (D40 chọn (b), lát 3c): sau `tar -x`, `tram-kiem` tự `git init`, `git add -A
-f`, `git commit` trong bản chép — đủ cho công cụ chỉ cần "là repo git" (husky, `git ls-files`, `git diff`). Cây của
commit = cây commit gốc (`-f`: cả file đã theo dõi mà `.gitignore` bỏ); KHÔNG lịch sử, remote, alternates của kho thật.

Không cấu hình nào ngoài trạm kiểm soát được chạm vào: `env -i` (bỏ `GIT_CONFIG_COUNT/PARAMETERS`, `GIT_TEMPLATE_DIR`,
`GIT_DIR`…), `GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_ATTR_NOSYSTEM`, `core.attributesFile=/dev/null`,
`--template=` (không template, không `.git/hooks`), `core.hooksPath=/dev/null` + `--no-verify`. `.gitattributes` của
cây chỉ GỌI TÊN driver (`filter=lfs`); lệnh `clean`/`process` chỉ đến từ cấu hình — không còn nguồn nào, nên `git add`
không chạy filter. `.git` trong commit: `git archive` của trạm từ chối (đường dẫn không hợp lệ) → `LoiBanChep`."""
import secrets
from tram.kiem.toolchain import GIT, PATH_KIEM

MOI_TRUONG = ("/usr/bin/env", "-i", f"PATH={PATH_KIEM}", "HOME=/var/empty", "LC_ALL=C",
              "GIT_CONFIG_NOSYSTEM=1", "GIT_CONFIG_GLOBAL=/dev/null", "GIT_ATTR_NOSYSTEM=1")
CAU_HINH = ("core.hooksPath=/dev/null", "core.attributesFile=/dev/null", "core.fsmonitor=false", "gc.auto=0",
            "maintenance.auto=false", "commit.gpgSign=false", "init.defaultBranch=kiem", "user.name=tram-kiem",
            "user.email=tram-kiem@localhost", "core.ignorecase=false")


def _git(wt) -> list[str]:
    git = [*MOI_TRUONG, f"{GIT}/bin/git"]
    for c in CAU_HINH:
        git += ["-c", c]
    return [*git, "-C", str(wt)]


def lenh_repo(wt) -> dict[str, list[str]]:
    """Ba lệnh (chạy theo thứ tự, DƯỚI `tram-kiem` qua `boc`) dựng repo một commit trong `wt`."""
    git = _git(wt)
    return {"init": [*git, "init", "-q", "--template="], "add": [*git, "add", "-A", "-f"],
            "commit": [*git, "commit", "-q", "--allow-empty", "--no-verify", "-m", "kiem"]}


def lenh_cay(wt) -> list[str]:
    """In cây của HEAD bản chép (dưới `tram-kiem`) để trạm so với cây commit gốc (R7)."""
    return [*_git(wt), "rev-parse", "--verify", "HEAD^{tree}"]


def ten_ban_chep(giao_id: str) -> str:
    """Tên MỚI mỗi lần (không dùng lại thư mục của lần trước)."""
    if not giao_id or "/" in giao_id or giao_id.startswith((".", "-")):
        raise ValueError(f"giao_id không dùng làm tên thư mục được: {giao_id!r}")
    return f"{giao_id}-{secrets.token_hex(4)}"
