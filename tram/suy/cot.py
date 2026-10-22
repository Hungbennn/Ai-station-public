"""Suy vị trí bead trên bảng lúc đọc (spec 2 §5.1, kiến trúc Q12) — không lưu trạng thái riêng."""
from dataclasses import dataclass

from tram.beads.mo_hinh import Bead
from tram.cham_cot.ghi import NHAN_KHOA
from tram.cham_cot.luat_cung import bi_chan_boi
from tram.suy.lam_sach import lam_sach

HANG = ("ai-lam", "can-chot", "cho-review", "chua-cham", "epic", "theo-plan")
NHAN_COT_HANG = {"cot:ai-lam": "ai-lam", "cot:can-chot": "can-chot", "cot:cho-review": "cho-review"}
NHAN_LUONG = {"can-spec", "cho-duyet-spec", "theo-plan"}
NHAN_ESCALATION = "tram:escalation"
NHAN_CO_DO = "co-do"
TRANG_THAI_HIEN = {"open", "in_progress", "blocked"}


@dataclass(frozen=True)
class ViTri:
    hang: str
    tu_nhan_cot: bool      # vị trí đến từ nhãn cot:* (chỉ khi đó mới được kéo / chốt)
    lech: bool             # ≥ 2 nhãn cot:* hoặc nhãn cot:* lạ
    khe_spec: bool         # feature can-spec: hiện mờ ở cột 1
    cho: tuple[str, ...]   # bị chặn bởi (kể cả ID không có trong snapshot — fail-closed)


def hien_tren_bang(bead: Bead) -> bool:
    return bead.status in TRANG_THAI_HIEN


def suy_vi_tri(bead: Bead, theo_id: dict[str, Bead]) -> ViTri:
    cho = bi_chan_boi(bead, theo_id)
    so_cot = sum(1 for n in bead.labels if n.startswith("cot:"))
    if bead.issue_type == "epic":
        return ViTri("epic", False, so_cot > 1, False, cho)
    nhan = bead.nhan_cot()
    if nhan is not None:
        hang = NHAN_COT_HANG.get(nhan)
        return ViTri(hang or "chua-cham", hang is not None, so_cot > 1 or hang is None, False, cho)
    tap = set(bead.labels)
    if "can-spec" in tap:
        return ViTri("ai-lam", False, False, True, cho)
    if "cho-duyet-spec" in tap or NHAN_ESCALATION in tap:
        return ViTri("can-chot", False, False, False, cho)
    if "theo-plan" in tap:
        return ViTri("theo-plan", False, False, False, cho)
    return ViTri("chua-cham", False, False, False, cho)


def _ngoai_luong(bead: Bead) -> str | None:
    if bead.status not in TRANG_THAI_HIEN:
        return "Bead đã đóng hoặc hoãn"
    if NHAN_ESCALATION in bead.labels or NHAN_LUONG & set(bead.labels):
        return "Bead trong luồng feature / escalation do phần 4 quản"
    return None


def ly_do_khong_keo(bead: Bead, vt: ViTri) -> str | None:
    if bead.issue_type == "epic":
        return "Epic không được kéo (#9)"
    if bead.issue_type == "decision":
        return "Decision mở được trả lời bằng nút Trả lời, không kéo cột"
    if (ly_do := _ngoai_luong(bead)) is not None:
        return ly_do
    if not vt.tu_nhan_cot or vt.hang not in ("ai-lam", "can-chot"):
        return "Chỉ kéo giữa cột 1 và cột 2"
    return None


def ly_do_khong_chot(bead: Bead, vt: ViTri) -> str | None:
    if bead.issue_type in ("epic", "decision"):
        return "Không chốt epic / bead quyết định"
    if (ly_do := _ngoai_luong(bead)) is not None:
        return ly_do
    if not vt.tu_nhan_cot or vt.hang != "can-chot":
        return "Chỉ chốt bead ở cột 2"
    return None


def ly_do_khong_tra_loi(bead: Bead) -> str | None:
    """Nút Trả lời (spec 2 §5.2): escalation hoặc decision mở — đóng chính decision kèm câu trả lời."""
    if bead.issue_type != "decision" or not hien_tren_bang(bead):
        return "Chỉ trả lời escalation / decision đang mở"
    return None


def the_bead(du_an: str, bead: Bead, theo_id: dict[str, Bead]) -> dict:
    vt = suy_vi_tri(bead, theo_id)
    return {"du_an": du_an, "id": bead.id, "tieu_de": lam_sach(bead.title, 200), "loai": bead.issue_type,
            "uu_tien": bead.priority, "hang": vt.hang, "mo": bool(vt.cho) or vt.khe_spec, "cho": list(vt.cho),
            "khoa": NHAN_KHOA in bead.labels, "co_do": NHAN_CO_DO in bead.labels, "lech": vt.lech,
            "khe_spec": vt.khe_spec, "keo_duoc": ly_do_khong_keo(bead, vt) is None,
            "chot_duoc": ly_do_khong_chot(bead, vt) is None, "tra_loi_duoc": ly_do_khong_tra_loi(bead) is None,
            "updated_at": bead.updated_at}


def cham_gan_nhat(kho, du_an: str, bead_id: str):
    """`cham_cot.ket_qua` mới nhất không bị huỷ (plan 1a G8: `huy = bead_doi_khi_cham`)."""
    return kho.moi_nhat(du_an, bead_id, "cham_cot.ket_qua", dieu_kien=lambda s: not s.du_lieu.get("huy"))
