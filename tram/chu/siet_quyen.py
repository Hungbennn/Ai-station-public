"""`tram chu siet-quyen` (bs-2bd.1.4): dữ liệu trạm chủ dưới `~/.tram` chỉ chủ đọc được — thư mục 700, file 600.

Chỉ chạy dưới TÀI KHOẢN TRẠM CHỦ. Bỏ qua `TRANH` ở gốc (thư mục principal của khe phải đọc được khi cùng tài khoản
chạy thợ: hàng đợi phiếu, hồ sơ sandbox — spec 3 §7.3). Đi cây QUA FD: gốc mở `O_NOFOLLOW`, mỗi mục con mở tương đối
fd của cha (`dir_fd`, `O_NOFOLLOW`), đối chiếu (dev, inode) với lstat, rồi `fchmod` trên chính fd đó — thay thư mục
cha bằng liên kết mềm giữa chừng không kéo việc đổi quyền ra ngoài cây. Danh sách in lúc hỏi chỉ là xem trước; lúc
thực hiện đi cây lại và báo đúng mục đã đổi. Không đổi, chỉ báo: liên kết mềm, mục không thuộc người chạy, file có
liên kết cứng (đổi quyền sẽ đổi luôn bản ở nơi khác), mục đổi giữa lúc xem và lúc mở. Mẫu `KeHoach`: chờ `dong-y`."""
import os
import stat
from collections.abc import Callable
from pathlib import Path

from tram.duong_dan import tram_home

TRANH = ("hang-doi", "sandbox")
_THU_MUC = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _duyet(dfd: int, rel: str, lam: bool, ra: list, bo: list, chen) -> None:
    st = os.fstat(dfd)
    if st.st_uid != os.getuid():
        bo.append(f"{rel}: không thuộc tài khoản này")
        return
    if stat.S_IMODE(st.st_mode) & 0o077:
        if lam:
            os.fchmod(dfd, 0o700)
        ra.append((rel, stat.S_IMODE(st.st_mode), 0o700))
    if chen:
        chen(rel)
    for ten in sorted(os.listdir(dfd)):
        con = ten if rel == "." else f"{rel}/{ten}"
        if rel == "." and ten in TRANH:
            continue
        ls = os.stat(ten, dir_fd=dfd, follow_symlinks=False)
        if stat.S_ISLNK(ls.st_mode):
            bo.append(f"{con}: liên kết mềm — không đi theo")
        elif stat.S_ISDIR(ls.st_mode):
            _mo_roi(ten, dfd, _THU_MUC, ls, con, bo, lambda fd: _duyet(fd, con, lam, ra, bo, chen))
        elif stat.S_ISREG(ls.st_mode) and stat.S_IMODE(ls.st_mode) & 0o077:
            if ls.st_uid != os.getuid():
                bo.append(f"{con}: không thuộc tài khoản này")
            elif ls.st_nlink > 1:
                bo.append(f"{con}: có liên kết cứng — Đại ca kiểm tay")
            elif not lam:
                ra.append((con, stat.S_IMODE(ls.st_mode), 0o600))
            elif _mo_roi(ten, dfd, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, ls, con, bo,
                         lambda fd: os.fchmod(fd, 0o600)):
                ra.append((con, stat.S_IMODE(ls.st_mode), 0o600))


def _mo_roi(ten: str, dfd: int, co: int, ls: os.stat_result, con: str, bo: list, lam: Callable[[int], None]) -> bool:
    try:
        fd = os.open(ten, co, dir_fd=dfd)
    except OSError:
        bo.append(f"{con}: đổi giữa chừng hoặc không mở được — bỏ qua")
        return False
    try:
        st = os.fstat(fd)
        if (st.st_dev, st.st_ino) != (ls.st_dev, ls.st_ino) or (stat.S_ISREG(st.st_mode) and st.st_nlink > 1):
            bo.append(f"{con}: đổi giữa chừng — bỏ qua")
            return False
        lam(fd)
        return True
    finally:
        os.close(fd)


def di_cay(goc: Path, *, lam: bool, chen=None) -> tuple[list[tuple[str, int, int]], list[str]]:
    """(mục cần/đã đổi: (đường tương đối, quyền cũ, quyền mới), mục bỏ qua kèm lý do). `lam=False`: chỉ xem."""
    ra, bo = [], []
    fd = os.open(goc, _THU_MUC)
    try:
        _duyet(fd, ".", lam, ra, bo, chen)
    finally:
        os.close(fd)
    return ra, bo


def can_siet(goc: Path) -> tuple[list[tuple[str, int, int]], list[str]]:
    return di_cay(goc, lam=False)


def siet(goc: Path) -> list[tuple[str, int, int]]:
    return di_cay(goc, lam=True)[0]


def _lenh(args) -> int:
    goc = tram_home()
    ds, bo = can_siet(goc)
    print(f"Siết quyền dưới {goc} (bỏ qua {', '.join(TRANH)}):")
    print("\n".join(f"  - {p}: {cu:04o} → {moi:04o}" for p, cu, moi in ds) or "  (không có gì cần siết)")
    if bo:
        print("Không đổi (Đại ca xem):\n" + "\n".join(f"  ! {b}" for b in bo))
    if not ds:
        return 0
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    print(f"Đã siết {len(siet(goc))} mục.")
    return 0


def them_lenh_siet(chu) -> None:
    s = chu.add_parser("siet-quyen", help="Siết quyền ~/.tram của trạm chủ về 700/600 (liệt kê, chờ dong-y)")
    s.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ dùng khi Đại ca đã đọc danh sách)")
    s.set_defaults(ham=_lenh)
