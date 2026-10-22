"""Đọc cổng hiện có; không mở lại và không fallback sang principal trạm."""
from tram.duong_dan import tram_home
from tram.quan_kiem.client import CongTuXa


def cong_mo():
    try:
        return (not (tram_home() / "kiem-lai.dong").exists()
                and CongTuXa().trang_thai().get("trang_thai") == "mo")
    except (OSError, ValueError):
        return False
