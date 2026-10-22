"""Đọc trước merge, đếm lỗi liên lạc liên tiếp trong kho sự kiện đang có."""
from dataclasses import replace

from tram.giao_viec.gh import LoiGh


def doc(gh, repo, so):
    pr = gh.xem_pr(repo, so)
    if pr.trang_thai == "OPEN":
        pr = replace(pr, ci=gh.cong_merge(repo, pr))
        if pr.ci == "loi":
            raise LoiGh("github-doc-loi")
    return pr


def ghi_doc(kho, du_an, bead_id, ds, ma, loi, luc):
    cu = next((s.du_lieu for s in reversed(ds) if s.loai == "tu_merge.doc"
               and s.du_lieu.get("ma_thao_tac") == ma), {})
    n = int(cu.get("loi_lien_tiep", 0)) + 1 if loi else 0
    if loi or cu.get("loi_lien_tiep", 0):
        with kho.giao_dich():
            kho.ghi_su_kien(du_an, "tu_merge.doc", {"ma_thao_tac": ma, "loi_lien_tiep": n},
                            luc=luc, bead_id=bead_id, tac_nhan="tram/tu-merge")
    return n
