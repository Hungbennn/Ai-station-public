"""Ngăn bên của bead (spec 2 §5.1): lý do chấm, câu hỏi, mô tả, nghiệm thu, bàn giao, dòng thời gian."""
import json

from tram.ban_giao.doc import tom_tat_ban_giao
from tram.suy.cot import cham_gan_nhat, the_bead
from tram.suy.lam_sach import co_ky_tu_an, lam_sach


def ban_giao_sach(tt: dict | None) -> dict | None:
    if tt is None:
        return None
    pr = tt["pr"] if tt["pr"] and not co_ky_tu_an(tt["pr"]) else None
    return {"pr": pr, **{k: lam_sach(tt[k], 200) or None for k in ("nhanh", "commit", "file_ban_giao")},
            "loi": [lam_sach(x, 300) for x in tt["loi"]]}


def chi_tiet_bead(du_an: str, bead, theo_id: dict, kho) -> dict:
    cham = cham_gan_nhat(kho, du_an, bead.id)
    return {
        "the": the_bead(du_an, bead, theo_id),
        "mo_ta": lam_sach(bead.description, 8000),
        "nghiem_thu": lam_sach(bead.acceptance_criteria, 4000),
        "cham_gan_nhat": None if cham is None else {
            "luc": cham.luc, "cot": cham.du_lieu.get("cot"), "ly_do": lam_sach(cham.du_lieu.get("ly_do"), 1000),
            "cau_hoi": [lam_sach(q, 500) for q in cham.du_lieu.get("cau_hoi") or []]},
        "ban_giao": ban_giao_sach(tom_tat_ban_giao(bead.notes)),
        "dong_thoi_gian": [
            {"id": s.id, "luc": s.luc, "loai": s.loai, "tac_nhan": s.tac_nhan,
             "tom_tat": lam_sach(json.dumps(s.du_lieu, ensure_ascii=False), 300)}
            for s in kho.cua_bead(du_an, bead.id)],
    }
