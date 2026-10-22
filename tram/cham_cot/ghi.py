from datetime import timedelta
from zoneinfo import ZoneInfo

from tram.beads.mo_hinh import Bead
from tram.cham_cot.cham import PhanCot
from tram.duong_dan import bay_gio, doc_luc
from tram.su_kien.kho import KhoSuKien

NHAN_COT = {"ai-lam": "cot:ai-lam", "can-chot": "cot:can-chot"}
NHAN_KHOA = "cot-khoa"
NHAN_BO_QUA = {"cot-khoa", "cot:cho-review", "can-spec", "cho-duyet-spec", "theo-plan"}  # theo-plan: spec 4 §14.5
GIO_VN = ZoneInfo("Asia/Ho_Chi_Minh")


def _lan_ghi_cuoi(kho: KhoSuKien, du_an_ten: str, bead_id: str):
    return kho.moi_nhat(du_an_ten, bead_id, "cham_cot.ket_qua", dieu_kien=lambda s: s.du_lieu.get("da_ghi"))


def dong_ghi_chu(cot: str, ly_do: str, cau_hoi: list[str], luc_utc: str) -> str:
    gio = doc_luc(luc_utc).astimezone(GIO_VN).strftime("%Y-%m-%d %H:%M")
    s = f"[tram/cham-cot {gio}] cột {1 if cot == 'ai-lam' else 2} — {ly_do}"
    if cau_hoi:
        s += " Cần chốt: " + " ".join(f"({i}) {q}" for i, q in enumerate(cau_hoi, 1))
    return s


def ghi_ket_qua(bd, kho: KhoSuKien, du_an_ten: str, bead: Bead, phan: PhanCot, *, thu: bool,
                huy: str | None = None) -> bool:
    """Thay toàn bộ nhãn `cot:*` bằng đúng một nhãn đích (§5.4). `huy` khác None → không ghi bd,
    chỉ ghi sự kiện (kết quả bị bỏ vì bead đổi trong lúc chấm — §5.6)."""
    truoc = _lan_ghi_cuoi(kho, du_an_ten, bead.id)
    doi_noi_dung = truoc is None or (truoc.du_lieu["cot"], truoc.du_lieu["ly_do"]) != (phan.cot, phan.ly_do)
    nhan_moi = NHAN_COT[phan.cot]
    cot_hien = [n for n in bead.labels if n.startswith("cot:")]
    them = [] if nhan_moi in cot_hien else [nhan_moi]
    bo = [n for n in cot_hien if n != nhan_moi]
    se_ghi = not thu and huy is None and bool(them or bo or doi_noi_dung)
    if se_ghi:
        bd.cap_nhat_nhan(bead.id, them=them, bo=bo,
                         ghi_chu=dong_ghi_chu(phan.cot, phan.ly_do, phan.cau_hoi, bay_gio()) if doi_noi_dung else None)
    du_lieu = {**phan.du_lieu, "cot": phan.cot, "ly_do": phan.ly_do, "cau_hoi": phan.cau_hoi,
               "da_ghi": se_ghi, "nhan_truoc": bead.nhan_cot()}
    if len(cot_hien) > 1:
        du_lieu["nhan_lech"] = cot_hien  # bead mang nhiều nhãn cột — báo, lượt ghi này sửa về một
    if huy:
        du_lieu["huy"] = huy
    kho.ghi(du_an_ten, "cham_cot.ket_qua", du_lieu, bead_id=bead.id, token_vao=phan.token_vao,
            token_ra=phan.token_ra, mo_hinh=phan.du_lieu.get("mo_hinh"), thoi_gian_ms=phan.thoi_gian_ms)
    return se_ghi


def _da_go_khoa(kho: KhoSuKien, du_an_ten: str, bead_id: str, hien: str) -> bool:
    """Lần khoá đã ghi là sự kiện mới nhất và nhãn vẫn như lúc khoá → Đại ca đã xoá cot-khoa."""
    cuoi = kho.moi_nhat_cac_loai(du_an_ten, bead_id, ("cham_cot.ket_qua", "cot.dai_ca_sua"),
                                 dieu_kien=lambda s: s.du_lieu.get("da_ghi"))
    return cuoi is not None and cuoi.loai == "cot.dai_ca_sua" and cuoi.du_lieu.get("cot_moi") == hien


def kiem_sua_tay(bd, kho: KhoSuKien, du_an_ten: str, bead: Bead, *, thu: bool) -> bool:
    hien = bead.nhan_cot()
    if hien not in NHAN_COT.values():
        return False
    truoc = _lan_ghi_cuoi(kho, du_an_ten, bead.id)
    cot_he = NHAN_COT[truoc.du_lieu["cot"]] if truoc else None
    if hien == cot_he or _da_go_khoa(kho, du_an_ten, bead.id, hien):
        return False
    if thu:
        return True
    bd.cap_nhat_nhan(bead.id, them=[NHAN_KHOA])
    kho.ghi(du_an_ten, "cot.dai_ca_sua",
            {"cot_he": cot_he, "cot_moi": hien, "ly_do_he": truoc.du_lieu["ly_do"] if truoc else None,
             "tieu_de": bead.title, "da_ghi": True},
            bead_id=bead.id, tac_nhan="dai-ca")
    return True


def do_he_vua_sua(kho: KhoSuKien, du_an_ten: str, bead: Bead, *, dung_sai_giay: int = 10) -> bool:
    truoc = _lan_ghi_cuoi(kho, du_an_ten, bead.id)
    return truoc is not None and doc_luc(bead.updated_at) <= doc_luc(truoc.luc) + timedelta(seconds=dung_sai_giay)
