"""Chép MÔI TRƯỜNG KIỂM (`moi_truong_kiem` của `du-an/<ten>.yaml`, Đại ca đặt tay, trỏ DB test) vào worktree —
hàm chung của thợ (spec 3 §7.1) và kiểm lại của trạm (spec 4 §6.2 bước 3). Đích là đường dẫn tương đối, không `..`,
và KHÔNG được thoát worktree qua symlink (kiểm đường dẫn thật sau khi phân giải). Gọi khi agent chưa chạy."""
import os
from pathlib import Path, PurePosixPath


class LoiMoiTruongKiem(ValueError):
    pass


def loi_dich(dich: object) -> str | None:
    if not isinstance(dich, str) or not dich or dich.startswith("/") or "\\" in dich or "\0" in dich:
        return f"đích môi trường kiểm không hợp lệ: {dich!r}"
    if any(p in ("..", ".", "") for p in dich.split("/")) or PurePosixPath(dich).is_absolute():
        return f"đích môi trường kiểm không được chứa '..', '.' hay '//': {dich}"
    return None


def chep_moi_truong_kiem(nguon: Path, worktree: Path, dich: str) -> Path:
    if (loi := loi_dich(dich)) is not None:
        raise LoiMoiTruongKiem(loi)
    if not nguon.is_file():
        raise LoiMoiTruongKiem(f"Không thấy file môi trường kiểm {nguon}")
    goc = worktree.resolve(strict=True)
    dich_p = goc / dich
    if not dich_p.parent.is_dir():
        raise LoiMoiTruongKiem(f"Thư mục đích không có trong worktree: {dich_p.parent.relative_to(goc)}")
    if not Path(os.path.realpath(dich_p.parent)).is_relative_to(goc):
        raise LoiMoiTruongKiem(f"Đích {dich} thoát worktree qua symlink")
    if dich_p.is_symlink():
        raise LoiMoiTruongKiem(f"Đích {dich} là symlink")
    fd = os.open(dich_p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(nguon.read_bytes())
    os.chmod(dich_p, 0o600)
    return dich_p
