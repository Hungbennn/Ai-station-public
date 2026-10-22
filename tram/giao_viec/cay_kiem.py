"""Cây của commit cho bản chép kiểm (D22, lát 3c) — mọi phép xét làm trên ĐỐI TƯỢNG GIT của kho kiểm (bất biến theo
SHA), không trên đĩa mà `tram-kiem` sửa được. `info/attributes` của kho kiểm vô hiệu `export-ignore`/`export-subst`
trong `.gitattributes` của commit (ưu tiên cao nhất theo gitattributes) — commit không giấu được file khỏi bản chép.
R7: lệnh git của trạm bỏ biến `GIT_*`, cấu hình global/system, attributes ngoài và `refs/replace`; `git archive` ghim
autocrlf/eol/ignorecase/protectHFS; kho kiểm có `filter.*` riêng thì từ chối — bản chép theo `.gitattributes` của
commit, cùng phép mà `git add` của bản chép (`repo_ban_chep.py`) đảo lại; cây lệch thì `ban_chep` từ chối."""
import io
import os
import subprocess
import tarfile
import time
from collections.abc import Callable
from pathlib import Path

from tram.kiem.vong_doi import Nhom, khoi_chay, kill_cuc_bo

GIT = ("git", "-c", "core.hooksPath=/dev/null")
THUOC_TINH = "* -export-ignore -export-subst\n"
ARCHIVE = ("-c", "core.autocrlf=false", "-c", "core.eol=lf", "-c", "core.attributesFile=/dev/null", "-c",
           "core.ignorecase=false", "-c", "core.protectHFS=true", "-c", "core.protectNTFS=true")


def _env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return env | {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_ATTR_NOSYSTEM": "1",
                  "GIT_NO_REPLACE_OBJECTS": "1"}


def _git(kho: Path, *args: str, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, timeout=120, env=_env(), **kw)


def loi_dich_trong_cay(kho: Path, commit: str, dich: str) -> str | None:
    """Đích môi trường kiểm xét trên cây của commit: mọi thư mục cha là thư mục thật, đích (nếu có) là file thường —
    không symlink, thư mục hay submodule."""
    phan = dich.split("/")
    for i in range(1, len(phan) + 1):
        con, cuoi = "/".join(phan[:i]), i == len(phan)
        r = _git(kho, "ls-tree", "-z", commit, "--", con)
        if r.returncode != 0:
            return f"không đọc được cây của commit {commit[:12]}"
        dong = [x for x in r.stdout.split(b"\0") if x]
        if not dong:
            return None if cuoi else f"Thư mục đích không có trong commit: {con}"
        mode = dong[0].split(b" ", 1)[0]
        if not cuoi and mode != b"040000":
            return f"Đích {dich} đi qua {con} — không phải thư mục thật trong commit"
        if cuoi and mode not in (b"100644", b"100755"):
            return f"Đích {dich} trong commit là symlink/thư mục/submodule"
    return None


def chuan_bi_thuoc_tinh(kho: Path) -> None:
    p = Path(_git(kho, "rev-parse", "--git-path", "info/attributes", check=True, text=True).stdout.strip())
    p = p if p.is_absolute() else kho / p
    if not p.is_file() or p.read_text(encoding="utf-8") != THUOC_TINH:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(THUOC_TINH, encoding="utf-8")


def nguon_archive(kho: Path, commit: str, *, chu: list, khoi: Callable = khoi_chay) -> Nhom:
    """`git archive` của commit qua primitive P1 (H1, V2-6a): nhóm/phiên riêng, kill cục bộ (tiến trình của TRẠM),
    stdout là ống. Người gọi SỞ HỮU qua `chu` (hợp đồng `kiem.so_huu`): đóng `n.p.stdout` khi đích xong, `cho` có hạn,
    thu hồi `chu` trong `finally`."""
    chuan_bi_thuoc_tinh(kho)
    return khoi([*GIT, *ARCHIVE, "-C", str(kho), "archive", "--format=tar", commit], kill=kill_cuc_bo, chu=chu,
                env=_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


def loi_cau_hinh_kho(kho: Path) -> str | None:
    """Kho kiểm khai `filter.*` (vd LFS cục bộ) thì archive chạy smudge của trạm — bản chép không còn theo commit."""
    r = _git(kho, "config", "--name-only", "--get-regexp", r"^filter\.", text=True)
    return None if r.returncode == 1 else f"kho kiểm có cấu hình filter riêng (mã {r.returncode}) — không chép"


def cay_goc(kho: Path, commit: str) -> str:
    """Mã cây (tree) của commit trong kho kiểm — bản chép phải dựng lại ĐÚNG cây này (R7)."""
    return _git(kho, "rev-parse", "--verify", f"{commit}^{{tree}}", check=True, text=True).stdout.strip()


def tar_mot_tep(dich: str, du_lieu: bytes) -> bytes:
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode="w") as t:
        ti = tarfile.TarInfo(dich)
        ti.size, ti.mode, ti.mtime = len(du_lieu), 0o600, int(time.time())
        t.addfile(ti, io.BytesIO(du_lieu))
    return b.getvalue()
