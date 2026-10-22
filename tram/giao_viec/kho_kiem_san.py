"""Tra kho kiểm có sẵn của một dự án cho bộ giao việc (spec 4 §6.2 bước 1): trả đường dẫn khi kho đã được tạo."""
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import kho_kiem


def kho_kiem_co_san(da: DuAn) -> Path | None:
    """Kho kiểm của trạm nếu đã được tạo (tạo = clone từ GitHub — chờ S7)."""
    p = kho_kiem(da.ten)
    return p if (p / ".git").exists() else None
