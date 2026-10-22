"""Ứng viên của một dự án cho lần xin việc (spec 4 §5.1, §5.2, §6.6): bead đủ điều kiện, không có phiếu hiệu lực,
bước kế tiếp là `code`/`qc`, còn ngân sách cho một phiếu (`du_mot_phieu` — giữ trước, §8)."""
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.luat_cung import bi_chan_boi
from tram.giao_viec.chon import UngVien
from tram.giao_viec.dieu_kien import ly_do_khong_giao
from tram.giao_viec.escalation import LY_DO_HOI, ma_escalation
from tram.giao_viec.ngan_sach import du_mot_phieu, ngan_sach_phieu
from tram.giao_viec.pipeline import TrangThaiBead, buoc_ke_tiep
from tram.giao_viec.su_kien import SK, da_co, moi_nhat, su_kien_bead
from tram.giao_viec.tieu_chi import digest_tieu_chi, tach_tieu_chi
from tram.phieu.kho import KhoPhieu


import json


def la_do(ds: list[SK]) -> bool:
    """Bead dở: phiếu mới nhất đã kết thúc không phải `xong` (§5.2 mục 1)."""
    n = moi_nhat(ds, "giao.nhan")
    kt = n and moi_nhat(ds, "giao.ket_thuc", lambda s: s.du_lieu.get("giao_id") == n.du_lieu["giao_id"])
    return bool(kt) and kt.du_lieu["ket_thuc"] != "xong"


def khe_da_code(ds: list[SK]) -> frozenset[str]:
    return frozenset(s.du_lieu["khe_id"] for s in ds if s.loai == "giao.nhan" and s.du_lieu.get("buoc") == "code")


def trang_thai_bead(kho: KhoPhieu, du_an: str, b: Bead, theo_id: dict[str, Bead], viec_ton: set[str]) -> TrangThaiBead:
    return TrangThaiBead(kho.phieu_hieu_luc(du_an, b.id) is not None, bool(bi_chan_boi(b, theo_id)), b.id in viec_ton,
                         "cot:cho-review" in b.labels, digest_tieu_chi(tach_tieu_chi(b.acceptance_criteria)),
                         b.issue_type == "spike")


def viec_ton_cua(kho: KhoPhieu, du_an: str) -> set[str]:
    ton = {r[0] for r in kho.db.execute(
        "SELECT DISTINCT bead_id FROM cong_viec_cho WHERE du_an = ? AND xong_luc IS NULL", (du_an,))}
    for i, bead_id, raw in kho.db.execute(
            "SELECT id, bead_id, du_lieu FROM su_kien WHERE du_an = ? AND loai = 'bao.can_hoi'", (du_an,)):
        d = json.loads(raw)
        ly = LY_DO_HOI.get(d.get("loai_hoi"), "agent-can-hoi")
        ma = ma_escalation(du_an, bead_id, ly, f"hoi-{i}")
        if not da_co(kho, du_an, "escalation.tao", {"ma_thao_tac": ma}):
            ton.add(bead_id)
    return ton


def liet_ke(kho: KhoPhieu, du_an: DuAn, beads: list[Bead], san_sang: set[str],
            spec_da_merge: frozenset[str] = frozenset()) -> list[UngVien]:
    theo_id, ton, ra = {b.id: b for b in beads}, viec_ton_cua(kho, du_an.ten), []
    for b in beads:
        if ly_do_khong_giao(b, theo_id, san_sang, du_an, spec_da_merge) is not None:
            continue
        ds = su_kien_bead(kho, du_an.ten, b.id)
        buoc = buoc_ke_tiep(ds, trang_thai_bead(kho, du_an.ten, b, theo_id, ton))
        if buoc in ("code", "qc") and du_mot_phieu(kho, ds, ngan_sach_phieu(buoc, du_an.giao.ngan_sach),
                                                  du_an.giao.ngan_sach.bead):
            ra.append(UngVien(du_an, b, buoc, la_do(ds), khe_da_code(ds)))
    return ra
