"""D89: file trong repo dự án mà ba lệnh nhắc tới thành đường dẫn cấm hiệu lực (spec 4 §6.2 bước 0) — hàm tính.
TM-3 cộng kết quả vào `them=` của kiểm đường dẫn cấm; agent sửa file đó → `dong-file-cau-hinh`, không tự merge.
Đây là tập cấm BẮT BUỘC: bên gọi không để ngoại lệ dự án (`cho_phep`) miễn nó (Codex C2).

Hợp đồng (Codex Q1): `loai_trong_repo` nhận token NGUYÊN VĂN (tương đối hay tuyệt đối, kể cả phần sau `=` của
`--x=y`), tự chuẩn hoá từ gốc repo đáng tin (resolve, chặn thoát gốc qua `..`/symlink) và trả (đường dẫn tương đối
POSIX từ gốc, "file" | "dir") hoặc None. Hàm này chỉ bỏ token rỗng, `~…`, cờ `-…`, glob. Còn hở (design Risks):
script gọi tiếp file khác không nhắc trong lệnh, `make` đọc `Makefile` ngầm — khuyên để script deploy ngoài repo."""
import shlex
from collections.abc import Callable
from typing import Literal

from tram.tu_dong.cai_dat import TRUONG_LENH, CaiDatTuDong

KY_TU_GLOB = frozenset("*?[")
LoaiTrongRepo = Callable[[str], tuple[str, Literal["file", "dir"]] | None]


def _ung_vien(tok: str) -> list[str]:
    """Token và phần sau `=` đầu tiên. Đường tuyệt đối, `..` đi tiếp tới callback — chỉ nó biết gốc repo."""
    return [p for p in (tok, tok.split("=", 1)[1] if "=" in tok else "")
            if p and not p.startswith(("~", "-")) and not set(p) & KY_TU_GLOB]


def _mau(kq: object) -> str | None:
    """(rel, loại) → mẫu cấm: file → `rel`, thư mục → `rel/**`. Dạng lạ (gốc rỗng, tuyệt đối, `..`, `.`, loại
    khác) → None: không sinh mẫu sai từ callback hỏng."""
    rel, loai = kq if isinstance(kq, tuple) and len(kq) == 2 else ("", None)
    if not isinstance(rel, str) or loai not in ("file", "dir") or {"", ".", ".."} & set(rel.split("/")):
        return None
    return rel if loai == "file" else f"{rel}/**"


def duong_dan_tu_lenh(cd: CaiDatTuDong, loai_trong_repo: LoaiTrongRepo) -> tuple[str, ...]:
    """Mẫu cấm từ ba lệnh, đã sắp xếp, không trùng. Lệnh không tách được → bỏ qua (khi lưu đã bị từ chối)."""
    ra = set()
    for t in TRUONG_LENH:
        try:
            argv = shlex.split(getattr(cd, t))
        except ValueError:
            continue
        for p in (p for tok in argv for p in _ung_vien(tok)):
            if mau := _mau(loai_trong_repo(p)):
                ra.add(mau)
    return tuple(sorted(ra))
