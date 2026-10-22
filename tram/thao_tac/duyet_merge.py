"""Bằng chứng cho Duyệt tay cột 3 — Đại ca chốt 21/10 sau bs-8zi."""
from dataclasses import dataclass
from pathlib import Path
import subprocess

from tram.ban_giao.doc import tom_tat_ban_giao
from tram.giao_viec.gh import GhCli, LoiGh
from tram.giao_viec.gh_tu_merge import SHA_RE
from tram.giao_viec.git_kiem import fetch, la_to_tien, sha_cua
from tram.suy.pr_tram import URL_PR
from tram.thao_tac.loi import KhongHopLe


@dataclass(frozen=True)
class NguonDuyet:
    kho_git: Path | None
    nhanh_chinh: str = "main"
    gh: GhCli | None = None


def nguon_duyet_that(ten: str) -> NguonDuyet:
    from tram.cau_hinh.du_an import nap_du_an
    from tram.giao_viec.git_kiem import kho_kiem
    return NguonDuyet(kho_kiem(ten), nap_du_an(ten).nhanh_chinh, GhCli())


def pr_cua(nc, bead_id: str) -> str | None:
    """PR hiện hành: sự kiện trạm đúng commit/vòng, rồi đến khối bàn giao cuối trong notes."""
    v = nc.kho.moi_nhat(nc.du_an, bead_id, "bead.vao_cot_3")
    tv = nc.kho.moi_nhat(nc.du_an, bead_id, "cot.tra_ve")
    if v is not None and (tv is None or v.id > tv.id):
        mo = nc.kho.moi_nhat(nc.du_an, bead_id, "pr.mo", dieu_kien=lambda s: (
            s.id > v.id and s.du_lieu.get("commit") == v.du_lieu.get("commit_ban_giao")
            and s.du_lieu.get("loai") == "bead"))
        if mo is not None:
            return mo.du_lieu.get("url")
    tt = tom_tat_ban_giao(nc.bd.mot(bead_id).notes)
    return tt["pr"] if tt else None


def kiem_da_merge(nc, bead_id: str) -> tuple[str | None, str | None, str]:
    v = nc.kho.moi_nhat(nc.du_an, bead_id, "bead.vao_cot_3")
    tv = nc.kho.moi_nhat(nc.du_an, bead_id, "cot.tra_ve")
    if v is None or (tv is not None and v.id <= tv.id):
        raise KhongHopLe("Chưa có bead.vao_cot_3 sau lần Trả về gần nhất để xác định commit bàn giao")
    c = v.du_lieu.get("commit_ban_giao")
    if not isinstance(c, str) or not SHA_RE.fullmatch(c):
        raise KhongHopLe("Không xác định được commit bàn giao trong bead.vao_cot_3")

    def chap_nhan(pr, commit, nhanh):
        hien = nc.kho.moi_nhat(nc.du_an, bead_id, "bead.vao_cot_3")
        tra = nc.kho.moi_nhat(nc.du_an, bead_id, "cot.tra_ve")
        if hien is None or hien.id != v.id or (tra is not None and tra.id > v.id):
            raise KhongHopLe("Bàn giao/cột đã đổi trong lúc xác minh — tải lại rồi bấm Duyệt")
        return pr, commit, nhanh

    if nc.nguon_duyet is None:
        raise KhongHopLe("Chưa có kho kiểm để xác minh commit đã vào nhánh chính")
    try:
        ns = nc.nguon_duyet(nc.du_an)
        if ns.kho_git is None or not ns.kho_git.is_dir():
            raise KhongHopLe("Chưa có kho kiểm để xác minh commit đã vào nhánh chính")
        fetch(ns.kho_git)
        chinh = f"origin/{ns.nhanh_chinh}"
        if sha_cua(ns.kho_git, chinh) is None:
            raise KhongHopLe("Không tìm thấy nhánh chính remote trong kho kiểm sau fetch")
        da_vao = la_to_tien(ns.kho_git, c, chinh)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise KhongHopLe(f"Không xác minh được kho kiểm/fetch nhánh chính ({type(e).__name__}) — thử lại") from None
    pr = pr_cua(nc, bead_id)
    if da_vao:
        return chap_nhan(pr, c, ns.nhanh_chinh)
    if not pr:
        raise KhongHopLe(f"Commit chưa vào {ns.nhanh_chinh} và trạm chưa mở PR — ghép nhánh tram/{bead_id} "
                         f"vào {ns.nhanh_chinh} rồi bấm Duyệt")
    if not isinstance(pr, str) or not URL_PR.fullmatch(pr):
        raise KhongHopLe("Không xác minh được PR: URL không phải PR GitHub hợp lệ")
    if ns.gh is None:
        raise KhongHopLe("Không có gh để xác minh PR đã merge — chưa thể Duyệt")
    repo, so = "/".join(pr.split("/")[-4:-2]), int(pr.rsplit("/", 1)[1])
    try:
        p = ns.gh.xem_pr(repo, so)
    except LoiGh:
        raise KhongHopLe("gh lỗi/không chạy được — chưa xác minh được PR đã merge, thử lại") from None
    if p.url != pr or p.base != ns.nhanh_chinh:
        raise KhongHopLe("PR không đúng URL hoặc không vào nhánh chính của dự án — chưa thể Duyệt")
    if p.trang_thai != "MERGED" or p.merged_at is None:
        raise KhongHopLe(f"PR {pr} chưa merge — merge trên GitHub (Create a merge commit) rồi bấm Duyệt")
    return chap_nhan(pr, None, ns.nhanh_chinh)
