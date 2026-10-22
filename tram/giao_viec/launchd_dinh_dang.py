"""Bố cục `launchctl print` ĐÃ ĐO ở G3 (máy B 18/10, macOS 15.6.1 24G90; `tests/du_lieu/launchd/`) — 3C-D7.
Lược đồ đóng: mỗi khoá cấp một (hợp của `user.txt` và `login.txt`) là KHỐI (`= {` … `\t}`) hoặc VÔ HƯỚNG với mẫu giá
trị đo được; sai loại, sai mẫu, khoá lạ, lặp, khối chưa đóng, dòng trống trong khối → ValueError. `BAT_BUOC_USER`:
khối/khoá có trong `user.txt` mà quan sát cần (thiếu = không quan sát được, KHÔNG coi là rỗng); khoá chỉ đo ở miền
login là tuỳ chọn nhưng có mặt thì vẫn đúng lược đồ."""
import re

KHOI = None
SO = r"\d+"
KHOA = {"type": r"user|login", "handle": SO, "active count": SO, "service count": SO, "active service count": SO,
        "creator": r"[\w.-]+\[\d+\]", "creator euid": SO, "session": r"[A-Za-z]+", "endpoint destination": r"[\w.]+",
        "auxiliary bootstrapper": r"[\w.]+ \(\w+\)", "bringup time": r"\d+ ms", "death port": r"0x[0-9a-f]+",
        "in-progress bootstraps": SO, "external activation count": SO, "properties": r"[a-z |]*",
        "security context": KHOI, "environment": KHOI, "services": KHOI, "unmanaged processes": KHOI,
        "endpoints": KHOI, "externally-hosted endpoints": KHOI, "task-special ports": KHOI, "disabled services": KHOI}
BAT_BUOC_USER = ("type", "handle", "session", "security context", "services", "unmanaged processes", "endpoints",
                 "task-special ports")
DONG_KHOA = re.compile(r"\t([a-z][a-z -]*[a-z]) = (.*)")
DONG_DV = re.compile(r"\t\t +\d+ +(?:-|-?\d+|\(\w+\)) \t([^\t]+)")   # pid, trạng thái thoát (-, số, (jt)), nhãn


def tach(van_ban: str, ten: str) -> dict[str, str | list[str]]:
    """`launchctl print <ten>` → {khoá: giá trị vô hướng | các dòng của khối}. Lệch bố cục đã đo → ValueError."""
    dong = van_ban.split("\n")
    if dong[0] != f"{ten} = {{" or dong[-2:] != ["}", ""]:
        raise ValueError("đầu/cuối")
    kq, khoi = {}, None
    for d in dong[1:-2]:
        if khoi is not None:
            if d == "\t}":
                khoi = None
            elif d.startswith("\t\t"):
                kq[khoi].append(d)
            else:
                raise ValueError("dòng lạ trong khối")
        elif d:
            m = DONG_KHOA.fullmatch(d)
            if not m or m[1] not in KHOA or m[1] in kq:
                raise ValueError("khoá lạ hoặc lặp")
            mau = KHOA[m[1]]
            if (mau is KHOI) != (m[2] == "{") or (mau is not KHOI and not re.fullmatch(mau, m[2])):
                raise ValueError("sai loại hoặc sai mẫu giá trị")
            khoi = m[1] if mau is KHOI else None
            kq[m[1]] = [] if khoi else m[2]
    if khoi is not None:
        raise ValueError("khối chưa đóng")
    return kq
