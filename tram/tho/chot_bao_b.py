"""Chốt sau thu hồi; SHA do quản lý đọc, không tin SHA trong hàng đợi."""
from tram.tho.day import luu_wip


def chot_bao_b(pc, dong, *, chot=luu_wip):
    commit = chot(pc.wt, "xong: quản lý thợ chốt bản sửa")
    ra = {**dong, "commit": commit}
    if "ban_giao" in dong:
        ra["ban_giao"] = {**dong["ban_giao"], "commit": commit, "nhanh": pc.p.repo.nhanh,
                          "luot": pc.p.luot}
    return ra
