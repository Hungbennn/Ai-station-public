"""Bản chép kiểm do `tram-kiem` SỞ HỮU (D22, lát 3c; spec 3 §7.3 mục 5, spec 4 §6.2 bước 1, 3) — không root, không ACL.
Trạm `git archive <commit>` từ kho kiểm, đưa qua stdin cho `tar -x` chạy DƯỚI `tram-kiem` (`boc`) vào một thư mục MỚI
dưới `thu_muc_kiem`; môi trường kiểm cũng qua stdin (tar một file); `tram-kiem` tự `rm -rf` khi xong. H1: mọi lệnh
qua `chay_gioi_han`, ống `git archive | tar` có chủ hai đầu (`ong_chep.py`). Mọi thao tác trên cây dưới quyền
`tram-kiem`, nên symlink/hardlink trong cây không với tới thứ gì `tram-kiem` vốn không với tới. Cây kiểm là repo git
MỘT commit do `tram-kiem` tự dựng (D40 (b), `repo_ban_chep.py`). Fail-closed: một lần kiểm lại một lúc (khoá
`~/.tram/kiem-lai.khoa`, không chờ — lần hai ném `KiemLaiDangBan`); `don_sach` trước khi chép và trước khi dọn — lỗi
→ ném; `tar`/`git` lỗi hoặc cây khác cây commit gốc (R7) → ném, không chạy lệnh kiểm; dọn xong mà thư mục còn → ném."""
import fcntl
import os
import subprocess
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.cay_kiem import cay_goc, loi_cau_hinh_kho, loi_dich_trong_cay, tar_mot_tep
from tram.giao_viec.ong_chep import chay_ong
from tram.giao_viec.repo_ban_chep import lenh_cay, lenh_repo, ten_ban_chep  # noqa: F401 — đường import cũ
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.moi_truong import LoiMoiTruongKiem, loi_dich
from tram.kiem.vong_doi import Kill, LoiThuHoi, kill_cuc_bo

TAR_NHAN = ("/usr/bin/tar", "-x", "--no-mac-metadata", "-f", "-", "-C")
THOI_GIAN = 600
Boc = Callable[[list[str]], list[str]]


class LoiBanChep(OSError):
    """Không bảo đảm được bản chép sạch — không chạy lệnh, không công nhận kết quả (vòng tick đếm lỗi, thử lại)."""


class KiemLaiDangBan(LoiBanChep):
    """Đang có lần kiểm lại khác (hoặc `tram giao kiem`) giữ khoá."""


class CayKhacNguon(LoiBanChep):
    """Không dựng được cây đúng commit (R7: CRLF/text, ident, encoding, hoa-thường, submodule, filter riêng của kho
    kiểm) — tất định, nên `kiem_lai` trả lỗi `cay-khac-nguon` (escalation) thay vì để vòng tick thử lại mãi."""


@contextmanager
def giu_khoa(p: Path | None = None):
    p = p or tram_home() / "kiem-lai.khoa"
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise KiemLaiDangBan("đang có lần kiểm lại khác chạy — thử lại vòng sau") from None
        yield
    finally:
        os.close(fd)


def _chay(argv: list[str], *, kill: Kill, timeout: float | None = None, **kw) -> subprocess.CompletedProcess:
    try:
        return chay_gioi_han(argv, kill=kill, capture_output=True, timeout=timeout or THOI_GIAN, **kw)
    except LoiThuHoi:                       # tick chỉ bắt OSError: chưa xác nhận thu hồi = bản chép không công nhận
        raise LoiBanChep("lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận") from None


def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc, kill: Kill = kill_cuc_bo) -> None:
    """`tram-kiem` tạo `wt` MỚI (đã có → lỗi), tự `tar -x` nội dung đúng commit từ stdin, rồi tự dựng repo git một
    commit (D40) — TRƯỚC khi môi trường kiểm vào cây, nên `.env.testing` không bao giờ thành đối tượng git. Cây của
    repo đó phải ĐÚNG cây commit gốc (R7): `git add` chuẩn hoá khác commit thì ném, không sửa cho khớp."""
    goc, loi = cay_goc(kho, commit), loi_cau_hinh_kho(kho)
    if loi is not None:
        raise CayKhacNguon(loi)
    _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), kill=kill, check=True)
    _chay(boc(["/bin/mkdir", str(wt)]), kill=kill, check=True)
    _chay(boc(["/bin/mkdir", "-m", "700", f"{wt}.nha", f"{wt}.nha/tmp"]), kill=kill, check=True)   # HOME/TMP lượt
    ma, tar = chay_ong(kho, commit, boc([*TAR_NHAN, str(wt)]), chay=lambda a, **kw: _chay(a, kill=kill, **kw),
                       han=THOI_GIAN, loi=LoiBanChep)               # nguồn chưa thu hồi → LoiBanChep, thắng lỗi đích
    if ma is None or ma or tar:
        raise LoiBanChep(f"git archive (mã {ma}) | tar (mã {tar}) lỗi")
    for buoc, argv in lenh_repo(wt).items():
        r = _chay(boc(argv), kill=kill)
        if r.returncode:
            raise LoiBanChep(f"git {buoc} dưới tram-kiem lỗi (mã {r.returncode}) — bản chép không thành repo kiểm")
    r = _chay(boc(lenh_cay(wt)), kill=kill)
    if r.returncode:
        raise LoiBanChep(f"git rev-parse dưới tram-kiem lỗi (mã {r.returncode}) — không đọc được cây bản chép")
    if r.stdout.decode(errors="replace").strip() != goc:
        raise CayKhacNguon(f"cây git của bản chép khác cây commit gốc {goc[:12]} (CRLF/encoding/hoa-thường/submodule)")


def nhan_moi_truong(kho: Path, commit: str, wt: Path, nguon: Path, dich: str, *, boc: Boc,
                    kill: Kill = kill_cuc_bo) -> None:
    """Môi trường kiểm vào bản chép QUA STDIN (tar một file, mode 0600) — không qua argv, trạm không ghi vào cây."""
    loi = loi_dich(dich) or loi_dich_trong_cay(kho, commit, dich)
    if loi is not None:
        raise LoiMoiTruongKiem(loi)
    if not nguon.is_file():
        raise LoiMoiTruongKiem(f"Không thấy file môi trường kiểm {nguon}")
    r = _chay(boc([*TAR_NHAN, str(wt)]), kill=kill, input=tar_mot_tep(dich, nguon.read_bytes()))
    if r.returncode:
        raise LoiMoiTruongKiem(f"tram-kiem không ghi được {dich} (tar mã {r.returncode})")


def don_ban(wt: Path, *, boc: Boc, don_sach: Callable[[], None] | None = None, kill: Kill = kill_cuc_bo) -> None:
    """Giết mọi tiến trình `tram-kiem` rồi `tram-kiem` tự `rm -rf` bản chép và nhà của lượt. Còn sót → ném."""
    loi = None
    if don_sach is not None:
        try:
            don_sach()
        except (OSError, subprocess.SubprocessError) as e:
            loi = e
    r = _chay(boc(["/bin/rm", "-rf", str(wt), f"{wt}.nha"]), kill=kill)
    if r.returncode or os.path.lexists(wt) or os.path.lexists(f"{wt}.nha"):
        raise LoiBanChep(f"không dọn được bản chép {wt} — không công nhận kết quả") from loi
    if loi is not None:
        raise loi
