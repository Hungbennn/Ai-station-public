"""Chứng cứ sở hữu dịch vụ trạm cho `go-dich-vu` (bs-2bd.1.17).

- `doc_chung_cu`: biên nhận `~/.tram/dich-vu/<nhãn>.json` + plist (file thường, mở `O_NOFOLLOW`) — đúng đường và
  sha256 trong biên nhận; ghi lại NỘI DUNG và ĐỊNH DANH (dev, inode) của cả hai lúc lập kế hoạch.
- `kiem_lai`: ngay TRƯỚC thao tác phá trạng thái, đọc lại cả hai — khác nội dung hay khác file (kể cả cùng nội dung)
  → `LoiGo`, chưa đụng gì (CLI hỏi `dong-y` có thể lâu).
- `nguon_nap`: plist mà job cùng nhãn đang nạp từ đó — dòng `path = …` mức một của `launchctl print` (đo 18/10 trên
  macOS của máy dev: có dòng này; dịch vụ vắng thì mã 113).
- `rut`: xoá GIỮ ĐỊNH DANH — đổi tên sang tên tạm trong cùng thư mục (qua fd thư mục được tin), đọc lại CHÍNH file đã
  đổi tên: đúng định danh + nội dung thì cất (callback) rồi xoá tên tạm; lệch hay cất lỗi thì trả lại tên cũ bằng
  `link` (không ghi đè gì) và dừng. File ai đó đặt vào đúng tên trong lúc cất không bao giờ bị xoá."""
import hashlib
import json
import os
import stat
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.su_kien import thu_muc_an_toan

_DOC = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK


class LoiGo(RuntimeError):
    pass


@dataclass(frozen=True)
class Tep:
    duong: Path
    noi_dung: bytes
    dinh_danh: tuple[int, int]


@dataclass(frozen=True)
class MucGo:
    ten: str
    nhan: str
    plist: Tep
    bien_nhan: Tep


def _doc(ten: str | Path, dir_fd: int | None = None) -> Tep:
    fd = os.open(ten, _DOC, dir_fd=dir_fd)
    with open(fd, "rb") as f:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise OSError("không phải file thường")
        return Tep(Path(ten), f.read(), (st.st_dev, st.st_ino))


def doc_chung_cu(ten: str, nhan: str, plist: Path, bien_nhan: Path) -> MucGo:
    try:
        bn, pl = _doc(bien_nhan), _doc(plist)
        ghi = json.loads(bn.noi_dung)
    except (OSError, ValueError):
        raise LoiGo(f"{nhan}: thiếu plist hay biên nhận cài của trạm — không có chứng cứ sở hữu, không gỡ gì. "
                    "Dịch vụ cài trước lát này: chạy lại tram chu cai-dat rồi gỡ.") from None
    if ghi != {"nhan": nhan, "plist": str(plist), "sha256": hashlib.sha256(pl.noi_dung).hexdigest()}:
        raise LoiGo(f"{nhan}: plist không khớp biên nhận cài của trạm — không gỡ gì, Đại ca kiểm tay")
    return MucGo(ten, nhan, pl, bn)


def kiem_lai(m: MucGo) -> None:
    for tep in (m.plist, m.bien_nhan):
        try:
            dung = _doc(tep.duong) == tep
        except OSError:
            dung = False
        if not dung:
            raise LoiGo(f"{m.nhan}: plist hay biên nhận đổi trong lúc chờ dong-y — không gỡ gì; chạy lại lệnh")


def nguon_nap(ra: str) -> str | None:
    return next((d[len("\tpath = "):].strip() for d in ra.splitlines() if d.startswith("\tpath = ")), None)


def _tra_lai(dfd: int, tam: str, ten: str) -> None:
    try:
        os.link(tam, ten, src_dir_fd=dfd, dst_dir_fd=dfd, follow_symlinks=False)
        os.unlink(tam, dir_fd=dfd)
    except OSError:                         # tên cũ đã có file khác: không ghi đè, để bản ở tên tạm
        pass


def rut(tep: Tep, cat: Callable[[bytes], object] | None = None) -> None:
    """Cất (nếu có `cat`) rồi xoá đúng file đã kiểm. Lệch định danh/nội dung → `LoiGo`, trả lại tên cũ."""
    try:
        dfd, _ = thu_muc_an_toan.mo_thu_muc(tep.duong.parent)
    except thu_muc_an_toan.LoiDuongDan as e:
        raise LoiGo(f"{tep.duong.name}: thư mục không dùng được ({e}) — dừng") from None
    ten, tam = tep.duong.name, f".{tep.duong.name}.go-{os.getpid()}"
    try:
        try:
            os.close(os.open(tam, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dfd))
            os.rename(ten, tam, src_dir_fd=dfd, dst_dir_fd=dfd)
        except OSError:
            raise LoiGo(f"{ten}: tên tạm đã có hoặc không chuyển được — dừng, giữ file để kiểm tay") from None
        try:
            try:
                doc = _doc(tam, dfd)
            except OSError:
                doc = None
            if doc is None or (doc.noi_dung, doc.dinh_danh) != (tep.noi_dung, tep.dinh_danh):
                raise LoiGo(f"{ten}: bị thay giữa chừng — đã trả lại, dừng")
            if cat:
                cat(tep.noi_dung)
        except BaseException:
            _tra_lai(dfd, tam, ten)
            raise
        os.unlink(tam, dir_fd=dfd)
    finally:
        os.close(dfd)
