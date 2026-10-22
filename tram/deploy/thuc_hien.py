"""Một chuỗi, chỉ lùi khi đường deploy xác nhận không còn writer của lượt."""
import time
from tram.deploy.ghi import ghi


def thuc_hien(db, ten, duong, m, commit, truoc):
    def goi(buoc, c):
        ghi(db, ten, "deploy.lenh", {"ma_thao_tac": m, "buoc": buoc, "bat_dau": True})
        start = time.monotonic()
        r = duong.goi(buoc, m, c, truoc)
        ghi(db, ten, "deploy.lenh", {"ma_thao_tac": m, "buoc": buoc,
                                     "ma_thoat": 0 if r and r["dat"] else 1,
                                     "giay": round(time.monotonic() - start), "het_gio": None,
                                     "da_dung": bool(r and r["da_dung"])})
        return r
    r = goi("deploy", commit)
    if not r or not r["da_dung"]:
        return "khong_ro"
    if r["dat"]:
        r = goi("kiem_song", commit)
        if not r or not r["da_dung"]:
            return "khong_ro"
        if r["dat"]:
            return "dat"
    r = goi("lui", truoc)
    if not r or not r["da_dung"]:
        return "khong_ro"
    if not r["dat"]:
        return "lui_hong"
    r = goi("kiem_song_sau_lui", truoc)
    if not r or not r["da_dung"]:
        return "khong_ro"
    return "da_lui" if r["dat"] else "lui_hong"
