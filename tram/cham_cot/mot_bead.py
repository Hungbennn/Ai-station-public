"""Một bead trong lượt quét: bỏ qua → chấm → kiểm lại version → ghi; yêu cầu chấm lại bền (spec §5.6)."""
import anthropic

from tram.beads.bd import LoiBd
from tram.cham_cot.bao_cao import BaoCaoQuet, DongBaoCao
from tram.cham_cot.bo_qua import CO_DINH, LOI_TOI_DA, vi_sao_bo_qua
from tram.cham_cot.cham import cham_mot_bead
from tram.cham_cot.ghi import ghi_ket_qua
from tram.duong_dan import doc_luc
from tram.llm.claude import LoiChamLLM

HUY_BEAD_DOI = "bead_doi_khi_cham"
HUY_KHONG_DOC = "khong_doc_duoc_version"
HUY_CO_PHIEU = "co_phieu_hieu_luc"  # #10: phần 3 cấp phiếu trong lúc đang chấm
HUY_TOI_DA = 3  # số lần huỷ liền nhau cho một bead trước khi dừng vòng gọi LLM


class LoiHuyLienTiep(RuntimeError):
    """Kết quả bị huỷ HUY_TOI_DA lần liền — ghi lỗi, đóng yêu cầu, để chuỗi lỗi §6.3 lo tiếp."""


LOI_CHAM = (LoiChamLLM, LoiBd, anthropic.APIError, LoiHuyLienTiep)


def kiem_lai_truoc_ghi(bd, bead) -> str | None:
    """§5.6 (C05): đọc lại version ngay trước khi ghi. Khác lúc chấm, hoặc không đọc được → huỷ kết quả.
    Phiếu hiệu lực (#10) kiểm ở `_cham_va_ghi`, trước hàm này."""
    try:
        moi = doc_luc(bd.phien_ban(bead.id))
    except (LoiBd, ValueError):
        return HUY_KHONG_DOC
    return HUY_BEAD_DOI if moi != doc_luc(bead.updated_at) else None


def _cham_va_ghi(bead, *, du_an, bd, kho, client, vai, theo_id, thu: bool, bc: BaoCaoQuet, nho=None) -> bool:
    """Chấm + kiểm lại + ghi. Trả False khi kết quả bị huỷ (sự kiện huỷ thành yêu cầu ở lượt sau)."""
    phan = cham_mot_bead(bead, du_an=du_an, theo_id=theo_id, kho=kho, client=client, vai=vai, nho=nho)
    huy = None
    if not thu:
        huy = HUY_CO_PHIEU if kho.yeu_cau.dang_co_phieu(du_an.ten, bead.id) else kiem_lai_truoc_ghi(bd, bead)
    if huy is not None and not huy:  # SQL nhan_su_kien_nguon coi {"huy": ""} là có huỷ — cấm giá trị rỗng
        raise ValueError("kiem_lai_truoc_ghi phải trả None hoặc lý do huỷ khác rỗng")
    da_ghi = ghi_ket_qua(bd, kho, du_an.ten, bead, phan, thu=thu, huy=huy)
    bc.token_vao += phan.token_vao
    bc.token_ra += phan.token_ra
    if huy:
        bc.bo_qua[huy] += 1
        if kho.yeu_cau.dem_huy_lien_tiep(du_an.ten, bead.id) >= HUY_TOI_DA:
            raise LoiHuyLienTiep(f"kết quả bị huỷ {HUY_TOI_DA} lần liền ({huy})")
        return False
    bc.dong.append(DongBaoCao(bead.id, bead.title, phan.cot, phan.ly_do, phan.cau_hoi,
                              phan.du_lieu.get("cham_rao", []), da_ghi))
    return True


def _ghi_loi(kho, bc: BaoCaoQuet, ten: str, bead, e: Exception) -> None:
    kho.ghi(ten, "cham_cot.loi", {"loi": str(e)[:500]}, bead_id=bead.id)
    bc.loi.append(f"{bead.id}: {str(e)[:200]}")


def xu_ly_bead(bead, nguon: list[int], *, co_yeu_cau: bool, du_an, bd, kho, client, vai, theo_id,
               moc, thu: bool, bc: BaoCaoQuet, nho=None) -> None:
    """`nguon`: yêu cầu được phép đánh dấu xong ([] ở chế độ thử); `co_yeu_cau`: bead có yêu cầu đang chờ."""
    ten = du_an.ten
    try:
        vi_sao = vi_sao_bo_qua(bead, ten, moc, bd=bd, kho=kho, thu=thu, co_yeu_cau=co_yeu_cau)
    except LOI_CHAM as e:
        _ghi_loi(kho, bc, ten, bead, e)  # chưa thử chấm → giữ yêu cầu...
        if nguon and kho.dem_loi_lien_tiep(ten, bead.id) >= LOI_TOI_DA:
            kho.yeu_cau.danh_dau_xong(ten, bead.id, nguon)  # ...trừ khi bd hỏng kéo dài: trả về chuỗi lỗi §6.3
        return
    if vi_sao:
        bc.bo_qua[vi_sao] += 1
        if nguon and vi_sao in CO_DINH:
            kho.yeu_cau.danh_dau_xong(ten, bead.id, nguon)  # bỏ qua cố định: xong, không chấm
        return
    try:
        xong = _cham_va_ghi(bead, du_an=du_an, bd=bd, kho=kho, client=client, vai=vai,
                            theo_id=theo_id, thu=thu, bc=bc, nho=nho)
    except LoiHuyLienTiep as e:
        _ghi_loi(kho, bc, ten, bead, e)
        kho.yeu_cau.dong_het(ten, bead.id)  # gồm cả yêu cầu sinh từ các lần huỷ chưa nhận
        return
    except LOI_CHAM as e:
        _ghi_loi(kho, bc, ten, bead, e)
        xong = True  # đã thử chấm và ghi lỗi; chuỗi lỗi (§6.3) lo thử lại
    if nguon and xong:
        kho.yeu_cau.danh_dau_xong(ten, bead.id, nguon)
