"""Ngoại lệ hẹp cho find vùng ghi-chung; không bỏ qua lỗi quan sát khác."""
import errno
import re
import stat
from pathlib import Path


def find_quan_sat_duoc(r) -> bool:
    if r.returncode == 0:
        return not r.stderr
    if r.returncode != 1 or not r.stderr:
        return False
    # B5 19/10/2026: find dưới 501 báo EPERM ở amsengagementd.classicdatavault, aneuserd, aned.
    for dong in r.stderr.removesuffix('\n').split('\n'):
        m = re.fullmatch(r'find: (/Library/Caches/com\.apple\.[^/\r\n]+): Operation not permitted', dong)
        if m is None:
            return False
        try:
            st = Path(m[1]).lstat()
        except PermissionError as e:
            # Đo 20/10: data vault Apple (SIP) trả EPERM cả cho lstat; user thường không tạo được vault (ACL ra EACCES).
            if e.errno == errno.EPERM:
                continue
            return False
        except (OSError, ValueError):
            return False
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o022:
            return False
    return True
