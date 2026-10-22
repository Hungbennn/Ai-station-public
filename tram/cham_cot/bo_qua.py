"""Điều kiện bỏ qua của bộ quét (spec 0+1a §5, §5.6, §6.3)."""
from tram.cham_cot.ghi import NHAN_BO_QUA, do_he_vua_sua, kiem_sua_tay
from tram.duong_dan import doc_luc

TRANG_THAI_CHAM = {"open", "in_progress", "blocked"}
LOAI_BO_QUA = {"epic"}  # #9 — epic hiện ở hàng riêng trên dashboard, không chấm
LOI_TOI_DA = 3
CO_DINH = {"trang_thai", "epic", "nhan", "phieu"}  # lý do cố định (gồm phiếu hiệu lực — #10)


def ly_do_bo_qua_co_dinh(bead) -> str | None:
    """Bỏ qua không phụ thuộc mốc hay lịch sử chấm
    (`theo-plan` nằm trong NHAN_BO_QUA; phiếu hiệu lực: vi_sao_bo_qua)."""
    if bead.status not in TRANG_THAI_CHAM:
        return "trang_thai"
    if bead.issue_type in LOAI_BO_QUA:
        return "epic"
    if NHAN_BO_QUA & set(bead.labels):
        return "nhan"
    return None


def _da_bao_bo_qua(kho, ten: str, bead_id: str) -> bool:
    cuoi = kho.moi_nhat_cac_loai(ten, bead_id, ("cham_cot.loi", "cham_cot.bo_qua"))
    return cuoi is not None and cuoi.loai == "cham_cot.bo_qua"


def _doi_sau_loi_cuoi(kho, ten: str, bead) -> bool:
    """Bead được sửa sau lần lỗi cuối → gỡ đóng băng, chấm lại."""
    loi = kho.moi_nhat(ten, bead.id, "cham_cot.loi")
    return loi is not None and doc_luc(bead.updated_at) > doc_luc(loi.luc)


def _theo_lich_su(bead, ten: str, moc, *, kho, thu: bool) -> str | None:
    """Mốc quét, chuỗi lỗi liên tiếp, lần ghi của chính hệ."""
    vi_sao = "chua_doi" if moc and doc_luc(bead.updated_at) <= doc_luc(moc) else None
    so_loi = kho.dem_loi_lien_tiep(ten, bead.id)
    if vi_sao == "chua_doi" and so_loi > 0:
        vi_sao = None  # lượt trước lỗi → lượt này thử lại (spec §6.3)
    if vi_sao is None and so_loi >= LOI_TOI_DA and not _doi_sau_loi_cuoi(kho, ten, bead):
        # Chặn trước kiem_sua_tay: bd hỏng kéo dài không bị gọi lại mãi mỗi lượt.
        if not _da_bao_bo_qua(kho, ten, bead.id):
            kho.ghi(ten, "cham_cot.bo_qua", {"vi_sao": "loi_lien_tiep"}, bead_id=bead.id)
        vi_sao = "loi_lien_tiep"
    if vi_sao is None and not thu and do_he_vua_sua(kho, ten, bead):
        vi_sao = "he_vua_sua"
    return vi_sao


def vi_sao_bo_qua(bead, ten: str, moc, *, bd, kho, thu: bool, co_yeu_cau: bool = False) -> str | None:
    """`co_yeu_cau`: bead có yêu cầu chấm lại bền → bỏ qua mốc, he_vua_sua, chuỗi lỗi (§5.6);
    vẫn tôn trọng điều kiện cố định và vẫn nhận biết Đại ca sửa tay."""
    vi_sao = ly_do_bo_qua_co_dinh(bead)
    if vi_sao is None and kho.yeu_cau.dang_co_phieu(ten, bead.id):
        vi_sao = "phieu"  # #10: bead đang có phiếu hiệu lực — chấm lại khi phiếu kết thúc (spec 3 §6.3)
    if vi_sao is None and not co_yeu_cau:
        vi_sao = _theo_lich_su(bead, ten, moc, kho=kho, thu=thu)
    if vi_sao is None and kiem_sua_tay(bd, kho, ten, bead, thu=thu):
        vi_sao = "dai_ca_sua"
    return vi_sao
