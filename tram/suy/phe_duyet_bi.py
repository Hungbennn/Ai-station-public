"""Trang Phê duyệt — thẻ "Bí / cần quyết định" (lát 2f T4, khảo sát giao diện §1.10): mục `escalation` và
`decision` mang `chi_tiet.cau_hoi` (mô tả bead, ≤ 300); mục `escalation` thêm `khe_id`, `buoc`, `bead_goc` suy từ
`escalation.tao {escalation_id, bead_goc, giao_id}` (4a-1) rồi `giao.nhan` cùng `giao_id` (phần 3). Danh sách cho
phép — không trả thêm trường nào của sự kiện (`giao.nhan` không có `ma_giao`, nhưng vẫn không serialize cả khối)."""
from tram.beads.mo_hinh import Bead
from tram.suy.lam_sach import lam_sach

LOAI_CO_CAU_HOI = ("escalation", "decision")
DAU_MAY = ("ly_do: ", "bead_goc: ", "giao_id: ", "<!-- ma_thao_tac: ")   # dòng máy của escalation 4a-1 (mo_ta)


def cau_hoi(mo_ta: str) -> str:
    """Bỏ các dòng máy (`ly_do:`, `bead_goc:`, `giao_id:`, mốc `ma_thao_tac`) trạm ghi quanh câu hỏi."""
    dong = [d for d in (mo_ta or "").splitlines() if not d.startswith(DAU_MAY)]
    return lam_sach("\n".join(dong).strip(), 300)


def _chuoi(x) -> str | None:
    return lam_sach(x, 64) or None


def nguon_escalation(du_an: str, escalation_id: str, kho) -> dict:
    """`{khe_id, buoc, bead_goc}` — thiếu sự kiện thì None (escalation tạo tay, hoặc không gắn phiếu)."""
    ra = {"khe_id": None, "buoc": None, "bead_goc": None}
    tao = kho.gan_day(du_an, "escalation.tao", 1, du_lieu_co={"escalation_id": escalation_id})
    if not tao:
        return ra
    ra["bead_goc"] = _chuoi(tao[0].du_lieu.get("bead_goc"))
    giao_id = tao[0].du_lieu.get("giao_id")
    nhan = kho.gan_day(du_an, "giao.nhan", 1, du_lieu_co={"giao_id": giao_id}) if isinstance(giao_id, str) else []
    if nhan:
        ra["khe_id"], ra["buoc"] = _chuoi(nhan[0].du_lieu.get("khe_id")), _chuoi(nhan[0].du_lieu.get("buoc"))
    return ra


def gan_bi(du_an: str, muc: list[dict], kho, theo_id: dict[str, Bead]) -> list[dict]:
    """Như `gan_pr_tram` (2d): trả danh sách mới, chỉ THÊM khoá vào `chi_tiet` của mục escalation / decision."""
    ra = []
    for m in muc:
        if m["loai"] in LOAI_CO_CAU_HOI:
            b = theo_id.get(m["bead_id"])
            them = {"cau_hoi": cau_hoi(b.description if b else "")}
            if m["loai"] == "escalation":
                them |= nguon_escalation(du_an, m["bead_id"], kho)
            m = {**m, "chi_tiet": {**m["chi_tiet"], **them}}
        ra.append(m)
    return ra
