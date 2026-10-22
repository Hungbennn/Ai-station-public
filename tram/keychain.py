"""Đọc mục Keychain của tài khoản đang chạy bằng `security find-generic-password` — CÓ HẠN (bs-2bd.1.2).

Sau khi máy khởi động lại, Keychain đăng nhập còn khoá tới khi Đại ca đăng nhập; `security` có thể chờ mở khoá rất
lâu. Mọi lời đọc đi qua đây với hạn `HAN_GIAY`; quá hạn hay không chạy được thì coi như chưa có khoá (`doc_muc` trả
None) — dịch vụ báo "chưa có token" rồi dừng như hiện nay, không treo. Giá trị không bao giờ in, log hay đưa vào
thông báo lỗi; thông báo không chép argv hay stderr."""
import subprocess

HAN_GIAY = 10


class LoiKeychain(RuntimeError):
    """Không biết mục có hay chưa (Keychain khoá, `security` treo hoặc không chạy được)."""


def _chay(chay, argv: list[str]):
    try:                                   # `chay` đọc lúc gọi: test vá `subprocess.run` vẫn chặn được lời gọi thật
        return (chay or subprocess.run)(argv, capture_output=True, text=True, timeout=HAN_GIAY,
                                        stdin=subprocess.DEVNULL)
    except (subprocess.TimeoutExpired, OSError):
        return None


def doc_muc(dich_vu: str, *, chay=None) -> str | None:
    """Giá trị mục `dich_vu` (đã bỏ khoảng trắng hai đầu); None khi chưa có, rỗng, Keychain khoá hay quá hạn."""
    kq = _chay(chay, ["security", "find-generic-password", "-s", dich_vu, "-w"])
    if kq is None or kq.returncode != 0:
        return None
    return kq.stdout.strip() or None


def co_muc(dich_vu: str, *, chay=None) -> bool:
    """Chỉ mã 44 chứng minh chưa có; lỗi khác là không biết, không cho phép tạo khoá thay thế."""
    kq = _chay(chay, ["security", "find-generic-password", "-s", dich_vu])
    if kq is None or kq.returncode not in (0, 44):
        raise LoiKeychain("Không kiểm được Keychain; dừng để tránh ghi khi chưa biết mục có tồn tại")
    return kq.returncode == 0
