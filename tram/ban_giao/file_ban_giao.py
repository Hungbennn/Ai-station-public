"""`file_ban_giao` của bàn giao `chinh-thuc` (spec 0+1a §4.3, bản chặt 13/10): đường dẫn tương đối dưới
`docs/handovers/`, không tuyệt đối, không `..`, là FILE THƯỜNG — không symlink, không submodule."""
import os
import subprocess
from pathlib import Path, PurePosixPath

THU_MUC = "docs/handovers/"
GIT = ("git", "-c", "core.hooksPath=/dev/null")
MODE_FILE_THUONG = ("100644", "100755")


def loi_duong_dan(p: str) -> str | None:
    if not p or p.startswith("/") or "\\" in p or "\0" in p:
        return f"file_ban_giao không hợp lệ: {p!r}"
    phan = PurePosixPath(p).parts
    if ".." in phan or "." in p.split("/") or "" in p.split("/"):
        return f"file_ban_giao không được chứa '..', '.' hay '//': {p}"
    if not p.startswith(THU_MUC) or len(phan) < 3:
        return f"file_ban_giao phải nằm dưới {THU_MUC}: {p}"
    return None


def loi_tai_commit(repo: Path, commit: str, p: str, *, chay=subprocess.run) -> str | None:
    """Kiểm trong cây Git của commit đã nhận — git không đi qua symlink nên thư mục cha là symlink cũng 'không thấy'."""
    kq = chay([*GIT, "-C", str(repo), "ls-tree", "-z", commit, "--", p], capture_output=True)
    if kq.returncode != 0:
        return f"Không đọc được commit {commit}"
    dong = [x for x in kq.stdout.split(b"\0") if x]
    if not dong:
        return f"Không thấy file bàn giao {p} tại {commit}"
    mode, loai = dong[0].split(b" ")[:2]
    if loai != b"blob" or mode.decode() not in MODE_FILE_THUONG:
        return f"file_ban_giao {p} không phải file thường (mode {mode.decode()})"
    return None


def loi_tren_dia(goc: Path, p: str) -> str | None:
    """Kiểm trong worktree (thợ, sau khi worktree sạch): từng đoạn không là symlink, đích là file thường."""
    hien = goc
    for ten in PurePosixPath(p).parts:
        hien = hien / ten
        if os.path.islink(hien):
            return f"file_ban_giao {p} đi qua symlink {ten}"
    return None if hien.is_file() else f"Không thấy file bàn giao {p}"
