"""Tạo / cập nhật kho kiểm của trạm từ remote dự án (spec 4 §6.2 bước 1; #2 GitHub; credential thật chờ S7).

Kho kiểm `~/.tram/kho-kiem/<du_an>` là bản clone `--no-checkout` do TÀI KHOẢN TRẠM giữ — không bao giờ fetch vào repo
làm việc của Đại ca; chỉ ĐỌC `remote.origin.url` của repo đó. Clone gọi mạng bằng credential của trạm → chỉ chạy sau
khi Đại ca đọc kế hoạch và gõ `dong-y` (khuôn `tram chu cai-dat`).
Kho có sẵn trỏ remote khác → báo lỗi, không tự xoá."""
import os
import re
import subprocess
import signal
from dataclasses import dataclass
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import GIT, kho_kiem, sha_cua

GITHUB_RE = re.compile(r"(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?")


def _env() -> dict[str, str]:
    return {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def url_origin(repo: Path) -> str | None:
    kq = subprocess.run([*GIT, "-C", str(repo), "config", "--get", "remote.origin.url"], capture_output=True,
                        text=True, env=_env())
    return (kq.stdout.strip() or None) if kq.returncode == 0 else None


def github_repo(url: str | None) -> str | None:
    """`owner/repo` nếu `url` là remote GitHub (https hoặc ssh), ngược lại None."""
    m = GITHUB_RE.fullmatch(url or "")
    return f"{m[1]}/{m[2]}" if m else None


def loi_remote(url: str | None) -> str | None:
    if not url:
        return "repo dự án chưa có remote origin"
    if github_repo(url) or (url.startswith("/") and Path(url).is_dir()):
        return None                     # GitHub (#2) hoặc repo cục bộ (repo nháp, kiểm thử không mạng)
    return f"remote không phải GitHub hay thư mục cục bộ: {url[:200]}"


@dataclass(frozen=True)
class KeHoachKhoKiem:
    du_an: str
    dich: Path
    remote: str
    co_san: bool
    lenh: tuple[tuple[str, ...], ...]


def lap_ke_hoach(da: DuAn) -> KeHoachKhoKiem:
    url = url_origin(da.duong_dan)
    if (loi := loi_remote(url)) is not None:
        raise ValueError(f"{da.ten}: {loi}")
    dich = kho_kiem(da.ten)
    if (dich / ".git").exists():
        if (cu := url_origin(dich)) != url:
            raise ValueError(f"{da.ten}: kho kiểm {dich} trỏ {cu!r}, khác remote dự án {url!r} — xoá tay rồi tạo lại")
        return KeHoachKhoKiem(da.ten, dich, url, True,
                              ((*GIT, "-C", str(dich), "fetch", "--quiet", "--prune", "origin"),))
    return KeHoachKhoKiem(da.ten, dich, url, False, (
        (*GIT, "clone", "--quiet", "--no-checkout", "--config", "core.hooksPath=/dev/null", url, str(dich)),))


def in_ke_hoach(kh: KeHoachKhoKiem) -> str:
    dau = f"Kho kiểm {kh.du_an}: {'cập nhật' if kh.co_san else 'TẠO MỚI'} {kh.dich}\n  remote: {kh.remote}"
    return dau + "".join(f"\n  $ {' '.join(lenh)}" for lenh in kh.lenh)


def thuc_hien(kh: KeHoachKhoKiem, nhanh_chinh: str) -> str | None:
    """Chạy kế hoạch (hook tắt, không hỏi mật khẩu); trả SHA `origin/<nhanh_chinh>` sau khi xong."""
    kh.dich.parent.mkdir(parents=True, exist_ok=True)
    for lenh in kh.lenh:
        subprocess.run(list(lenh), check=True, capture_output=True, env=_env(), timeout=600)
    return sha_cua(kh.dich, f"origin/{nhanh_chinh}")
