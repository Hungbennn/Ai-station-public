"""Khớp lệnh với mẫu `lenh_cho_phep` — hàm chung của thợ (spec 3 §7.5) và kiểm lại (spec 4 §6.2 bước 4).

Luật: `shlex.split` cả lệnh và mẫu; số token bằng nhau; token mẫu `*` thay ĐÚNG MỘT token của lệnh — token đó không
chứa ký tự shell hay xuống dòng, không bắt đầu bằng `-`, không là đường dẫn tuyệt đối, không chứa `..`; token khác
phải bằng hệt. Trả danh sách đối số để chạy KHÔNG qua shell, hoặc None khi không khớp. Không qua shell không có
nghĩa là mã an toàn — mã test vẫn là mã repo, chạy trong môi trường cách ly (spec 3 §7.3)."""
import shlex
from collections.abc import Iterable

KY_TU_CAM = frozenset(";&|<>$`\n\r\0")
DONG_CAM = ("\n", "\r", "\0")


def _tach(s: object) -> list[str] | None:
    if not isinstance(s, str) or any(c in s for c in DONG_CAM):
        return None
    try:
        ds = shlex.split(s)
    except ValueError:
        return None
    return ds or None


def _token_sao_hop_le(t: str) -> bool:
    return (bool(t) and not (set(t) & KY_TU_CAM) and not t.startswith("-") and not t.startswith("/")
            and ".." not in t)


def kiem_mau(mau: object) -> str | None:
    """Lỗi của một mẫu, None = hợp lệ. Mẫu do Đại ca viết trong `du-an/<ten>.yaml` — vẫn kiểm, để mẫu hỏng
    không mở rộng được quyền chạy."""
    ds = _tach(mau)
    if ds is None:
        return "mẫu rỗng, có xuống dòng hoặc không tách được bằng shlex"
    if ds[0] == "*":
        return "token đầu (chương trình) không được là *"
    if any(t != "*" and "*" in t for t in ds):
        return "* phải đứng một mình thành một token"
    if any(set(t) & KY_TU_CAM for t in ds):
        return "mẫu chứa ký tự shell"
    return None


def khop_lenh(lenh: str, mau: str) -> list[str] | None:
    if kiem_mau(mau) is not None:
        return None
    l, m = _tach(lenh), _tach(mau)
    if l is None or len(l) != len(m):
        return None
    for tl, tm in zip(l, m):
        if tm == "*":
            if not _token_sao_hop_le(tl):
                return None
        elif tl != tm:
            return None
    return l


def khop_bat_ky(lenh: str, ds_mau: Iterable[str]) -> list[str] | None:
    """Đối số của mẫu đầu tiên khớp, hoặc None."""
    for mau in ds_mau:
        argv = khop_lenh(lenh, mau)
        if argv is not None:
            return argv
    return None
