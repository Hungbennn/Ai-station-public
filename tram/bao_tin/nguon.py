"""Nguồn tin lát 2a (spec 2 §6): so ảnh beads trước/sau `quet.xong`; trạm lỗi và estop từ sự kiện.
Lát 2b: `khe.cau_dao_ngat` (spec 3 §8.3) → "khe hết hạn mức" (ly_do `het-han-muc`) hoặc "cầu dao khe ngắt"."""
from tram.bao_tin.nguon_de_nghi import TIEN_TO as TIEN_TO_DE_NGHI, tin_de_nghi
from tram.bao_tin.nguon_tu_dong import TIEN_TO, tin_tu_dong
from tram.bao_tin.tin import Tin
from tram.beads.mo_hinh import Bead

NHAN_TIN = {"cot:cho-review": "cho_review", "cho-duyet-spec": "spec_cho_duyet", "co-do": "co_do"}
NHAN_ESCALATION = "tram:escalation"
NGUONG_QUET_LOI = 3
TIN_FEATURE = {"spec.cho_merge": "spec_cho_merge", "feature.xong": "feature_xong"}   # phần 4 §10 bước 4
# 2d (D15): PR do trạm mở đã merge — xác minh được / không. Chỉ mã bead; không số PR, URL, SHA, lý do.
TIN_PR = {"pr.da_merge": "pr_da_merge", "pr.khong_xac_minh": "pr_khong_xac_minh"}


def anh_tu_beads(beads: list[Bead]) -> dict[str, dict]:
    return {b.id: {"nhan": sorted(b.labels), "status": b.status} for b in beads}


def tin_tu_anh(du_an: str, truoc: dict, beads: list[Bead]) -> list[Tin]:
    ra = []
    for b in beads:
        if b.status == "closed":
            continue
        cu = truoc.get(b.id) or {"nhan": [], "status": ""}
        ra += [Tin(loai, du_an, b.id) for nhan, loai in NHAN_TIN.items() if nhan in b.labels and nhan not in cu["nhan"]]
        if NHAN_ESCALATION in b.labels and not (NHAN_ESCALATION in cu["nhan"] and cu["status"] != "closed"):
            ra.append(Tin("escalation", du_an, b.id))
    return ra


def so_quet_loi_lien_tiep(kho, du_an: str) -> int:
    xong = kho.gan_day(du_an, "quet.xong", 1)
    moc = xong[0].id if xong else 0
    return sum(1 for s in kho.gan_day(du_an, "quet.loi", 20) if s.id > moc)


def tin_tu_su_kien(sk, kho) -> list[Tin]:
    if sk.loai.startswith(TIEN_TO):                # TM-1: tự merge / tự deploy / cài đặt tự động
        return tin_tu_dong(sk)
    if sk.loai.startswith(TIEN_TO_DE_NGHI):        # TC: việc mới do agent tạo (một tin gộp mỗi đợt)
        return tin_de_nghi(sk)
    if sk.loai == "estop.bat":
        return [Tin("estop_bat", sk.du_an)]
    if sk.loai == "estop.tat":
        return [Tin("estop_tat", sk.du_an)]
    if sk.loai in ("cham_cot.bo_qua", "nho.loi_llm", "nho.loi_embedder"):   # nho.*: memory 1b nạp đứng
        return [Tin("tram_loi", sk.du_an, sk.bead_id)]
    if sk.loai in TIN_FEATURE:
        return [Tin(TIN_FEATURE[sk.loai], sk.du_an, sk.bead_id)]
    if sk.loai in TIN_PR:
        return [Tin(TIN_PR[sk.loai], sk.du_an, sk.bead_id)]
    if sk.loai == "khe.cau_dao_ngat":
        het = sk.du_lieu.get("ly_do") == "het-han-muc"
        return [Tin("khe_het_han_muc" if het else "khe_cau_dao", sk.du_an, sk.du_lieu.get("khe_id"))]
    if sk.loai == "quet.loi" and so_quet_loi_lien_tiep(kho, sk.du_an) >= NGUONG_QUET_LOI:
        return [Tin("tram_loi", sk.du_an)]
    return []
