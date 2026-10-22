"""Kết thúc phiếu như phần 3 làm khi nhận báo (CHỈ DÙNG TRONG TEST) — sinh công việc chờ cho phần 4."""
from kho_phieu_gia import LUC
from tram.phieu.cong_viec import cong_viec_cho
from tram.phieu.ket_thuc import ket_thuc_phieu, thu_hoi

LOAI = {"xong": "bao.xong", "bi": "bao.bi", "het_han_muc": "bao.het_han_muc"}


def ket_thuc_bang(kho, p, ket_thuc, **du_lieu):
    """Ghi `bao.<loại>` (hoặc thu hồi) rồi để phần 3 kết thúc phiếu; trả công việc chờ của phiếu."""
    with kho.giao_dich():
        if ket_thuc == "thu_hoi":
            thu_hoi(kho, kho.lay(p.giao_id), ly_do="mat-nhip", luc=LUC)
        else:
            sk = kho.ghi_su_kien(p.du_an, LOAI[ket_thuc], {"giao_id": p.giao_id, "luot": p.luot, **du_lieu},
                                 luc=LUC, bead_id=p.bead_id, tac_nhan=f"tho/{p.khe_id}")
            ket_thuc_phieu(kho, kho.lay(p.giao_id), ket_thuc=ket_thuc, su_kien_id=sk, luc=LUC, moc_cuoi=LUC)
    return next(c for c in cong_viec_cho(kho) if c.giao_id == p.giao_id)
