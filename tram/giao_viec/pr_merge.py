"""Trạm tự xác minh PR đã merge rồi mới đóng bead (spec 4 §6.5, spec 2 §5.2 hàng "Chờ review") — lát 4c.

Chỉ đóng khi MỌI điều kiện đúng: PR là PR trạm đã ghi (`pr.mo` của `commit_ban_giao` hiện hành), trạng thái
MERGED, head `tram/<bead>` cùng repo, base `<nhanh_chinh>`; merge commit có trong kho kiểm và thuộc
`origin/<nhanh_chinh>`; `commit_ban_giao` là tổ tiên `origin/<nhanh_chinh>` (merge thật — squash/rebase không
xác minh được); head của PR đúng `commit_ban_giao`; hậu duệ kể cả merge phải kiểm lại, không suy an toàn chỉ từ
topology. Sai một điều → `pr.khong_xac_minh` một lần, bead ở lại cột 3 cho Đại ca (nút Duyệt tay vẫn có)."""
import subprocess
from datetime import datetime
from pathlib import Path

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.gh import GhCli, PrInfo
from tram.giao_viec.git_kiem import GIT, la_to_tien, sha_cua
from tram.giao_viec.pr import NHAN_REVIEW
from tram.giao_viec.pr_bang_chung import bang_chung_hien_hanh
from tram.giao_viec.su_kien import SK, cua_so, ghi_mot_lan, moi_nhat, su_kien_bead
from tram.phieu.kho import KhoPhieu

CHO = "cho"     # merge commit chưa có trong kho kiểm (fetch đầu vòng tick chưa thấy) — vòng sau


def ly_do_khong_xac_minh(pr: PrInfo, mo: dict, kg: Path, da: DuAn, bead_id: str, c: str) -> str | None:
    chinh = f"origin/{da.nhanh_chinh}"
    if pr.so != mo["pr"] or pr.url != mo["url"]:
        return "pr-khac"
    if pr.nhanh != f"tram/{bead_id}" or pr.ngoai_repo:
        return "sai-nhanh"
    if pr.base != da.nhanh_chinh:
        return "sai-nhanh-chinh"
    if pr.merge_commit is None:
        return "thieu-merge-commit"
    if sha_cua(kg, pr.merge_commit) is None:
        return CHO
    if not la_to_tien(kg, pr.merge_commit, chinh):
        return "merge-khong-tren-nhanh-chinh"
    if not la_to_tien(kg, c, pr.merge_commit):
        return "khong-phai-merge-commit"
    return None if pr.head == c else "head-khac-commit-ban-giao"


def kiem_merge(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK],
               luc: datetime) -> str | None:
    w = cua_so(ds)
    v = bang_chung_hien_hanh(b, ds)
    if v is None:
        return None
    c = v.du_lieu["commit_ban_giao"]
    mo = moi_nhat(w, "pr.mo", lambda s: s.du_lieu["commit"] == c)
    if mo is None or moi_nhat(w, "pr.khong_xac_minh", lambda s: s.du_lieu["commit"] == c) is not None:
        return None
    xong = moi_nhat(w, "pr.da_merge", lambda s: s.du_lieu["commit"] == c)
    if xong is None:
        pr = gh.xem_pr(repo, mo.du_lieu["pr"])
        if pr.trang_thai != "MERGED":
            return None
        ma = mo.du_lieu["ma_thao_tac"]
        if (ly := ly_do_khong_xac_minh(pr, mo.du_lieu, kg, da, b.id, c)) == CHO:
            return "pr_cho_fetch"
        if ly is not None:
            ghi_mot_lan(kho, da.ten, "pr.khong_xac_minh", {"bead_id": b.id, "pr": pr.so, "commit": c, "ly_do": ly,
                        "ma_thao_tac": ma}, bead_id=b.id, luc=luc, khoa=("ma_thao_tac",))
            return "pr_khong_xac_minh"
        d = {"bead_id": b.id, "pr": pr.so, "url": pr.url, "commit": c, "merge_commit": pr.merge_commit,
             "nhanh_chinh": da.nhanh_chinh, "ma_thao_tac": ma}
        ghi_mot_lan(kho, da.ten, "pr.da_merge", d, bead_id=b.id, luc=luc, khoa=("ma_thao_tac",))
    else:
        d = xong.du_lieu
    # HTTP GitHub có thể chậm: đọc lại bead/sự kiện trước ghi và khi resume pr.da_merge.
    moi = bd.mot(b.id)
    hien = bang_chung_hien_hanh(moi, su_kien_bead(kho, da.ten, b.id))
    if hien is None or hien.id != v.id:
        return "pr_cho"
    bd.dong(b.id, f"Trạm xác minh PR #{d['pr']} đã merge {c[:12]} vào {d['nhanh_chinh']} "
                  f"(merge {d['merge_commit'][:12]}) — {d['ma_thao_tac']}")
    return "da_merge"
