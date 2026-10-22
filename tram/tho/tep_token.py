"""File bí mật của chính UID: dirfd/no-follow, 0700/0600, thay nguyên tử; không log giá trị."""
import os
import re
import secrets
import stat
from contextlib import contextmanager
from pathlib import Path

TOKEN = re.compile(r'[!-~]{1,4096}')


def kiem(s, mode, *, thu_muc=False):
    dung_loai = stat.S_ISDIR(s.st_mode) if thu_muc else stat.S_ISREG(s.st_mode) and s.st_nlink == 1
    if not dung_loai or s.st_uid != os.geteuid() or stat.S_IMODE(s.st_mode) != mode:
        raise ValueError('Kho token sai chủ/quyền/loại')


@contextmanager
def thu_muc(p: Path, *, tao=False):
    if not p.is_absolute() or '..' in p.parts:
        raise ValueError('Đường token phải tuyệt đối')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for i, ten in enumerate(p.parts[1:]):
            if tao and i == len(p.parts) - 2:
                try:
                    os.mkdir(ten, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            moi = os.open(ten, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = moi
        kiem(os.fstat(fd), 0o700, thu_muc=True)
        yield fd
    finally:
        os.close(fd)


def mo(p: Path) -> int:
    with thu_muc(p.parent) as d:
        fd = os.open(p.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=d)
    try:
        kiem(os.fstat(fd), 0o600)
        return fd
    except BaseException:
        os.close(fd)
        raise


def doc(p: Path) -> str:
    with os.fdopen(mo(p), 'r', encoding='ascii') as f:
        token = f.read(4097)
    if not TOKEN.fullmatch(token):
        raise ValueError('Token sai dạng')
    return token


def ghi(p: Path, token: str) -> None:
    if not TOKEN.fullmatch(token):
        raise ValueError('Token sai dạng')
    with thu_muc(p.parent, tao=True) as d:
        try:
            kiem(os.stat(p.name, dir_fd=d, follow_symlinks=False), 0o600)
        except FileNotFoundError:
            pass
        ten = '.token-' + secrets.token_hex(12)
        fd = os.open(ten, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=d)
        try:
            with os.fdopen(fd, 'w', encoding='ascii') as f:
                os.fchmod(f.fileno(), 0o600)
                f.write(token)
                f.flush()
                os.fsync(f.fileno())
            os.replace(ten, p.name, src_dir_fd=d, dst_dir_fd=d)
            os.fsync(d)
        finally:
            try:
                os.unlink(ten, dir_fd=d)
            except FileNotFoundError:
                pass
