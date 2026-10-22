import fcntl
from contextlib import contextmanager

from tram.beads.bd import LoiBd
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.bao_cao import BaoCaoQuet, DongBaoCao, xuat_bao_cao
from tram.cham_cot.bo_qua import LOI_TOI_DA, TRANG_THAI_CHAM
from tram.cham_cot.cham_lai import phat_hien_decision_doi
from tram.cham_cot.mot_bead import xu_ly_bead
from tram.chu import estop
from tram.duong_dan import doc_luc, tram_home

__all__ = ["LOI_TOI_DA", "TRANG_THAI_CHAM", "BaoCaoQuet", "DongBaoCao", "quet", "xuat_bao_cao"]


@contextmanager
def _khoa(ten: str):
    with open(tram_home() / f"quet-{ten}.lock", "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        yield True


def _doc_beads(bd, kho, bc: BaoCaoQuet, ten: str):
    """`bd list` lỗi hoặc JSON hỏng → sự kiện `quet.loi`, không chấm, không đổi mốc (spec 2 §12.5)."""
    try:
        return bd.tat_ca()
    except LoiBd as e:
        kho.ghi(ten, "quet.loi", {"loi": str(e)[:500]})
        bc.loi.append(f"bd list: {str(e)[:200]}")
        return None


def quet(du_an: DuAn, *, bd, kho, client, vai, tat_ca=False, thu=True, gioi_han=None,
         nho=None) -> BaoCaoQuet | None:
    """`nho`: hàm recall của memory 1b (None = chưa cài memory → bài học từ sự kiện cũ)."""
    ten = du_an.ten
    if estop.dang_bat():
        kho.ghi(ten, "quet.bo_qua", {"vi_sao": "estop"})
        return None
    with _khoa(ten) as duoc:
        if not duoc:
            return None
        bc = BaoCaoQuet(ten, thu)
        beads = _doc_beads(bd, kho, bc, ten)
        if beads is None:
            return bc
        theo_id = {x.id: x for x in beads}
        moc = None if tat_ca else kho.doc_moc(ten)
        kho.ghi(ten, "quet.bat_dau", {"tat_ca": tat_ca, "thu": thu, "so_bead": len(beads)})
        kho.yeu_cau.nhan_su_kien_nguon(ten)  # idempotent — chế độ thử cũng nhận để thấy yêu cầu
        if not thu:  # chế độ thử không lưu ảnh decision, không tiêu yêu cầu
            phat_hien_decision_doi(kho, ten, beads)
        cho = kho.yeu_cau.dang_cho(ten)
        for bead in beads:
            if gioi_han is not None and len(bc.dong) >= gioi_han:
                break
            xu_ly_bead(bead, [] if thu else cho.get(bead.id, []), co_yeu_cau=bead.id in cho, du_an=du_an,
                       bd=bd, kho=kho, client=client, vai=vai, theo_id=theo_id, moc=moc, thu=thu, bc=bc, nho=nho)
        for bead_id in [] if thu else sorted(set(cho) - set(theo_id)):
            kho.yeu_cau.danh_dau_xong(ten, bead_id, cho[bead_id])  # bead không còn trong bd list
        if not thu and beads and gioi_han is None:
            kho.ghi_moc(ten, max((x.updated_at for x in beads), key=doc_luc))
        kho.ghi(ten, "quet.xong", {"da_cham": len(bc.dong), "bo_qua": dict(bc.bo_qua),
                                   "loi": len(bc.loi), "token_vao": bc.token_vao, "token_ra": bc.token_ra})
        return bc
