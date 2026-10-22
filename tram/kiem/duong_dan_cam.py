"""Đường dẫn cấm (spec 4 §6.2 bước 0) — hàm chung của thợ (spec 3 §7.5 bước 1) và kiểm lại của trạm (phần 4).

Bảo vệ CHỈ DẪN cho lượt sau (file cấu hình agent, CI, manifest gói). Không phải hàng rào cho mã test — đó là việc
của cách ly (spec 3 §7.3)."""
from collections.abc import Iterable
from fnmatch import fnmatchcase

DUONG_DAN_CAM_TRAM = (
    "**/.claude/**", "**/.mcp.json", "**/CLAUDE.md", "**/AGENTS.md", ".github/workflows/**", "**/.tram/**",
    "**/composer.json", "**/package.json", "**/phpunit.xml*", "**/vitest.config.*", "**/jest.config.*",
    "**/.git/**", ".gitmodules",
)
KY_TU_GLOB = frozenset("*?[")


def _khop(phan: list[str], mau: list[str]) -> bool:
    if not mau:
        return not phan
    if mau[0] == "**":
        return any(_khop(phan[i:], mau[1:]) for i in range(len(phan) + 1))
    return bool(phan) and fnmatchcase(phan[0], mau[0]) and _khop(phan[1:], mau[1:])


def khop_mau(duong_dan: str, mau: str) -> bool:
    """Glob theo từng đoạn thư mục: `**` = 0..n đoạn; `*`, `?`, `[..]` không vượt `/`.
    Không phân biệt hoa thường — ổ đĩa macOS mặc định không phân biệt (`claude.md` vẫn là CLAUDE.md khi mở)."""
    return _khop(duong_dan.strip("/").lower().split("/"), mau.strip("/").lower().split("/"))


def duong_dan_cham_cam(cac_duong_dan: Iterable[str], *, them: Iterable[str] = (),
                       cho_phep: Iterable[str] = (), bat_buoc: Iterable[str] = ()) -> list[str]:
    """Các đường dẫn (tương đối POSIX từ gốc repo) chạm danh sách cấm, đã sắp xếp.
    `them`: mẫu dự án thêm (`duong_dan_cam`). `cho_phep`: ngoại lệ — CHỈ từng đường dẫn cụ thể; mục có ký tự glob
    bị bỏ qua (không dùng glob gỡ cả nhóm)."""
    mau = (*DUONG_DAN_CAM_TRAM, *them)
    mien = {p.strip("/") for p in cho_phep if not (set(p) & KY_TU_GLOB)}
    return sorted({p for p in cac_duong_dan if any(khop_mau(p, m) for m in bat_buoc)
                   or (p.strip("/") not in mien and any(khop_mau(p, m) for m in mau))})
