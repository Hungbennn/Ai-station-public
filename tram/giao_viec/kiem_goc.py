"""`tram giao kiem` — hai mục của D22 (lát 3c, bead bs-urj.13): thư mục gốc bản chép do CHÍNH `tram-kiem` sở hữu (trạm
chỉ cần đi qua được để làm cwd), và tài khoản trạm KHÔNG có dòng sudoers NOPASSWD nào chạy dưới root/ALL — D22 bỏ
helper root, nên dòng như vậy là sót lại hoặc lỗ. Chỉ XANH khi chạy thật trên máy B; test tiêm `lstat`/`chay`."""
import os
import pwd
import re
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.kiem_may import MucKiem
from tram.tho.principal import SUDO

RUNAS_NOPASSWD = re.compile(r"^\s*\(([^)]*)\)\s*NOPASSWD", re.M)


def uid_that(ten: str) -> int:
    return pwd.getpwnam(ten).pw_uid


def kiem_thu_muc_goc(pk: PrincipalKiem, thu_muc: Path | None, *, lstat: Callable = os.lstat,
                     uid_cua: Callable[[str], int] = uid_that,
                     di_qua: Callable[[Path], bool] = lambda p: os.access(p, os.X_OK)) -> MucKiem:
    ten = "principal: thư mục kiểm của tram-kiem"
    if thu_muc is None:
        return MucKiem(ten, "do", "chưa đặt giao_viec.thu_muc_kiem")
    try:
        s, uid = lstat(thu_muc), uid_cua(pk.ten)
    except (OSError, KeyError) as e:
        return MucKiem(ten, "do", f"{thu_muc}: {type(e).__name__}")
    loi = ("là symlink" if stat.S_ISLNK(s.st_mode) else "không phải thư mục" if not stat.S_ISDIR(s.st_mode)
           else f"chủ là uid {s.st_uid}, cần {pk.ten} (uid {uid})" if s.st_uid != uid
           else "nhóm/người khác ghi được" if s.st_mode & 0o022
           else "tài khoản trạm không đi qua được (cần quyền x)" if not di_qua(thu_muc) else None)
    return MucKiem(ten, "do" if loi else "xanh", f"{thu_muc}: {loi}" if loi else f"{thu_muc} thuộc {pk.ten}")


def kiem_sudoers_khong_root(*, chay: Callable = subprocess.run) -> MucKiem:
    ten = "principal: sudoers không NOPASSWD root"
    try:
        r = chay([SUDO, "-n", "-l"], capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, OSError) as e:
        return MucKiem(ten, "do", f"sudo -n -l: {type(e).__name__}")
    if r.returncode != 0:
        return MucKiem(ten, "do", "sudo -n -l lỗi — chưa có dòng NOPASSWD dưới tram-kiem?")
    xau = [m for m in RUNAS_NOPASSWD.findall(r.stdout) if re.search(r"\b(root|ALL)\b", m)]
    return MucKiem(ten, "do" if xau else "xanh",
                   f"NOPASSWD chạy dưới: {', '.join(xau)}" if xau else "chỉ NOPASSWD dưới user không đặc quyền")
