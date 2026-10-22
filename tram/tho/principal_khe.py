"""Principal của MỘT khe trong ngữ cảnh máy thợ (spec 3 §7.1, §7.3): hồ sơ sandbox theo lần chạy (cơ chế `sandbox`) và
lệnh trao quyền ghi worktree cho principal (cả hai cơ chế — ACL macOS do CHỦ worktree, tức tiến trình quản lý, đặt;
không cần sudo). CHỜ S6: cú pháp `chmod +a`, phạm vi `.git` cần mở (index, objects, ref nhánh của phiếu) và việc CẤM
ghi `.git/config`, `.git/hooks` của kho (ghi được config = chạy lệnh dưới quyền tiến trình quản lý qua
`core.fsmonitor`…). Hồ sơ sandbox nằm ở `~/.tram/sandbox/` (0755) để principal đọc được, không ghi được."""
from pathlib import Path

from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.principal import Principal, doc_principal
from tram.tho.sandbox import ghi_ho_so, ho_so_sandbox

FIND = "/usr/bin/find"
QUYEN_GHI = ("list,add_file,search,delete,add_subdirectory,delete_child,readattr,writeattr,readextattr,writeextattr,"
             "readsecurity,file_inherit,directory_inherit")


def principal_cua(ch: CauHinhTho, k: KheCauHinh, *, goc: Path, goc_wt: Path, wt: Path | None, ten: str) -> Principal:
    """`goc`: ~/.tram của tài khoản quản lý thợ; `goc_wt`: ~/tram/worktrees. Cơ chế `user` trả principal nguyên."""
    p = doc_principal(k.principal)
    if p.co_che != "sandbox":
        return p
    khac = [x for x in ch.khe if x.ten != k.ten]
    cam = [goc / "tho", *(goc / "hang-doi" / ch.may_id / x.ten for x in khac), *(x.thu_muc_cau_hinh for x in khac)]
    cam += [ch.chay.thu_muc_tram] if ch.chay.thu_muc_tram else []
    cho = [goc / "hang-doi" / ch.may_id / k.ten, k.thu_muc_cau_hinh, *([wt] if wt else [])]
    hs = ho_so_sandbox(cam=cam, cam_ghi=[goc_wt, goc_wt.parent / "kho"], cho_ghi=cho, cong_cam=list(ch.chay.cong_cam))
    thu_muc = goc / "sandbox" / ch.may_id / k.ten
    thu_muc.mkdir(parents=True, exist_ok=True, mode=0o755)
    return p.voi_ho_so(ghi_ho_so(thu_muc / f"{ten}.sb", hs))


def lenh_trao_quyen(*duong: Path, user: str, thu: bool = False) -> list[list[str]]:
    """Mở (`thu=True`: thu lại) quyền ghi cho principal trên từng thư mục: worktree, metadata worktree
    `.git/worktrees/<tên>` (`git rev-parse --absolute-git-dir`), thư mục hàng đợi của phiếu. KHÔNG mở `.git/config`,
    `.git/hooks` của kho; objects/ref nhánh của kho chung — S6 chốt cách mở hẹp nhất.
    Lát 3c: duyệt bằng `find` (không đi theo symlink, chỉ thư mục/file thường) — `chmod -R +a` của macOS ĐI THEO
    symlink kể cả với `-P`, nên symlink agent commit trỏ ra file của tiến trình quản lý sẽ nhận ACL."""
    return [[FIND, str(d), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "/bin/chmod", "-a" if thu else "+a",
             f"user:{user} allow {QUYEN_GHI}", "{}", "+"] for d in duong]
