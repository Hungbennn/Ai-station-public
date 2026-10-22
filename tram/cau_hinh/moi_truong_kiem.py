"""Khoá `moi_truong_kiem` của du-an/<ten>.yaml (tách khỏi `du_an.py` — bs-2bd.1.20, chỉ dời chỗ)."""
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.moi_truong import loi_dich


@dataclass(frozen=True)
class MoiTruongKiem:
    """Spec 3 §7.1: Đại ca đặt tay, trỏ DB test. `file` trên máy chạy kiểm; `dich` tương đối trong worktree."""
    file: Path
    dich: str


def doc_moi_truong_kiem(raw: dict) -> MoiTruongKiem | None:
    mt = raw.get("moi_truong_kiem")
    if mt is None:
        return None
    if not isinstance(mt, dict) or set(mt) != {"file", "dich"}:
        raise ValueError("moi_truong_kiem phải là bảng {file, dich}")
    f = Path(str(mt["file"])).expanduser()
    if not f.is_absolute():
        raise ValueError("moi_truong_kiem.file phải là đường dẫn tuyệt đối")
    if (loi := loi_dich(mt["dich"])) is not None:
        raise ValueError(f"moi_truong_kiem.dich: {loi}")
    return MoiTruongKiem(f, mt["dich"])
