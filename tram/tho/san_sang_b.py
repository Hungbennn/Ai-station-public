"""Dò đăng nhập trước khi B bắt đầu vòng nhận việc; không coi đây là chứng cứ S2."""
from pathlib import Path

from tram.tho.dang_ky_b import kiem_b
from tram.tho.kiem_cong import dang_nhap


def san_sang_b(ch, *, do=dang_nhap) -> bool:
    from tram.duong_dan import tram_home
    if not ch.tren_may_b:
        return True
    kiem_b(ch)
    return all(do(ch, k, goc=tram_home(), goc_wt=Path.home() / "tram/worktrees")[0] == "xanh"
               for k in ch.khe)
