"""Gom việc chờ Đại ca cho trang Phê duyệt (spec 2 §5.2) — tính lúc đọc từ beads + sự kiện."""
from tram.ban_giao.doc import tom_tat_ban_giao
from tram.beads.mo_hinh import Bead
from tram.suy.chi_tiet import ban_giao_sach
from tram.suy.cot import NHAN_CO_DO, NHAN_ESCALATION, TRANG_THAI_HIEN
from tram.suy.lam_sach import lam_sach
from tram.suy.phe_duyet_bi import gan_bi
from tram.suy.phe_duyet_spec import bo_sung_spec
from tram.suy.pr_tram import pr_tram
from tram.suy.deploy import muc_san_sang

THU_TU = ("escalation", "decision", "co-do", "he", "cho-review", "spec", "feature-xong", "san-sang-deploy")
HET_BO_QUA = ("cham_cot.bo_qua", "cham_cot.ket_qua", "cham_cot.thu_lai")
LOI_NHO = {"llm": "nho.loi_llm", "embedder": "nho.loi_embedder"}   # memory 1b: nạp ký ức đứng (plan 1b-1 G9)


def _khong_huy(s) -> bool:
    """`ket_qua{huy}` không phải lần chấm được (plan 1a G8) — không gỡ bead khỏi 'Hệ cần xem'."""
    return not (s.loai == "cham_cot.ket_qua" and s.du_lieu.get("huy"))


def _muc(loai: str, du_an: str, b: Bead | None, chi_tiet: dict | None = None) -> dict:
    return {"loai": loai, "du_an": du_an, "bead_id": b.id if b else None,
            "tieu_de": lam_sach(b.title, 200) if b else "", "uu_tien": b.priority if b else None,
            "updated_at": b.updated_at if b else None, "chi_tiet": chi_tiet or {}}


def _ban_giao(b: Bead) -> dict:
    return ban_giao_sach(tom_tat_ban_giao(b.notes)) or {
        "pr": None, "nhanh": None, "commit": None, "file_ban_giao": None, "loi": ["Thiếu khối bàn giao"]}


def muc_tu_beads(du_an: str, beads: list[Bead]) -> list[dict]:
    ra = []
    for b in beads:
        if b.status not in TRANG_THAI_HIEN:
            continue
        nhan = set(b.labels)
        if NHAN_ESCALATION in nhan:
            ra.append(_muc("escalation", du_an, b))
        elif b.issue_type == "decision":            # decision mở: cùng nút Trả lời (spec 2 §5.2)
            ra.append(_muc("decision", du_an, b))
        if NHAN_CO_DO in nhan:
            ra.append(_muc("co-do", du_an, b, _ban_giao(b)))
        if "cot:cho-review" in nhan:
            ra.append(_muc("cho-review", du_an, b, _ban_giao(b)))
        if "cho-duyet-spec" in nhan:
            ra.append(_muc("spec", du_an, b))
    return ra


def muc_he(du_an: str, kho, theo_id: dict[str, Bead]) -> list[dict]:
    ra, da_xet = [], set()
    for s in kho.gan_day(du_an, "cham_cot.bo_qua", 100):
        if s.bead_id in da_xet:
            continue
        da_xet.add(s.bead_id)
        b = theo_id.get(s.bead_id)
        cuoi = kho.moi_nhat_cac_loai(du_an, s.bead_id, HET_BO_QUA, dieu_kien=_khong_huy)
        if b is None or b.status not in TRANG_THAI_HIEN or cuoi is None or cuoi.loai != "cham_cot.bo_qua":
            continue
        loi = kho.moi_nhat(du_an, b.id, "cham_cot.loi")
        ra.append(_muc("he", du_an, b, {"su_kien": "cham_cot.bo_qua", "luc": cuoi.luc,
                                        "loi": lam_sach(loi.du_lieu.get("loi") if loi else "", 300)}))
    loi_q, xong = kho.gan_day(du_an, "quet.loi", 1), kho.gan_day(du_an, "quet.xong", 1)
    if loi_q and (not xong or loi_q[0].id > xong[0].id):
        ra.append(_muc("he", du_an, None, {"su_kien": "quet.loi", "luc": loi_q[0].luc,
                                           "loi": lam_sach(loi_q[0].du_lieu.get("loi"), 300)}))
    return ra + muc_nho(du_an, kho)


def muc_nho(du_an: str, kho) -> list[dict]:
    """`nho.loi_llm` / `nho.loi_embedder` chưa có `nho.phuc_hoi` cùng loại mới hơn → một mục 'Hệ cần xem'.
    Không gắn `bead_id` (nút "Thử lại" của mục hệ là chấm lại 1a; memory tự thử lại mỗi 2 phút) — mã bead ở `loi`."""
    ra = []
    for loai, ten in LOI_NHO.items():
        ln = kho.gan_day(du_an, ten, 1)
        ph = kho.gan_day(du_an, "nho.phuc_hoi", 1, du_lieu_co={"loai": loai})
        if ln and (not ph or ln[0].id > ph[0].id):
            d = ln[0].du_lieu
            loi = f"Nạp ký ức đứng ở bead {ln[0].bead_id} (sự kiện {d.get('su_kien_id')}): {d.get('loi')}"
            ra.append(_muc("he", du_an, None, {"su_kien": ten, "luc": ln[0].luc, "loi": lam_sach(loi, 300)}))
    return ra


def gan_pr_tram(du_an: str, muc: list[dict], kho) -> list[dict]:
    """Mục `cho-review` mang `chi_tiet.pr_tram`: PR trạm mở sau lần vào cột 3 hiện hành, hoặc None (2d G21, D38)."""
    ra = []
    for m in muc:
        if m["loai"] == "cho-review":
            vc3 = kho.moi_nhat(du_an, m["bead_id"], "bead.vao_cot_3")
            m = {**m, "chi_tiet": {**m["chi_tiet"], "pr_tram": pr_tram(kho, du_an, m["bead_id"], vc3) if vc3 else None}}
        ra.append(m)
    return ra


def gom_phe_duyet(cac_du_an: list[str], theo_du_an: dict[str, list[Bead]], kho, them: list[dict] = ()) -> list[dict]:
    """`them`: mục không gắn dự án (2b: cầu dao khe — `tram/suy/phe_duyet_khe.py`), xếp chung theo độ gấp."""
    ra = list(them)
    for du_an in cac_du_an:
        beads = theo_du_an.get(du_an, [])
        muc = gan_bi(du_an, gan_pr_tram(du_an, muc_tu_beads(du_an, beads), kho), kho, {b.id: b for b in beads})  # 2f T4
        ra += bo_sung_spec(du_an, muc, beads, kho) + muc_he(du_an, kho, {b.id: b for b in beads})
        ra += muc_san_sang(du_an, kho)
    return sorted(ra, key=lambda m: (THU_TU.index(m["loai"]), 9 if m["uu_tien"] is None else m["uu_tien"],
                                     m["updated_at"] or "", m["du_an"], m["bead_id"] or ""))
