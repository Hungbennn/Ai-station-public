"""Đọc seal cột 3 còn hiệu lực trước khi mở PR hoặc đóng bead — không tin notes agent."""
from tram.beads.mo_hinh import Bead
from tram.giao_viec.su_kien import SK, cua_so, moi_nhat, ref_cong_bo
from tram.giao_viec.tieu_chi import digest_tieu_chi, tach_tieu_chi


def bang_chung_hien_hanh(b: Bead, ds: list[SK]) -> SK | None:
    if b.status == "closed" or "cot:cho-review" not in b.labels:
        return None
    v = moi_nhat(cua_so(ds), "bead.vao_cot_3")
    if v is None or v.du_lieu.get("commit_ban_giao") != ref_cong_bo(ds):
        return None
    if v.du_lieu.get("digest_tieu_chi") != digest_tieu_chi(tach_tieu_chi(b.acceptance_criteria)):
        return None
    return v
