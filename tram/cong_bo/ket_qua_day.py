"""Phần chung của `da-push` (spec 3 §6.4): thẻ chắn trong giao dịch, nhớ kết quả dứt khoát theo request_id, và xử lý
kết quả CAS."""
from datetime import datetime
from pathlib import Path

from tram.cong_bo.doi_soat import hoan_tac
from tram.cong_bo.git import LoiGit, sha_remote
from tram.cong_bo.op import dat_trang_thai, ghi_cong_bo, op_mo
from tram.phieu.kho import BanGhiPhieu, KhoPhieu, LuotCu
from tram.phieu.mo_hinh import Phieu
from tram.phieu.yeu_cau_tho import luu_ket_qua


def the_chan(kho: KhoPhieu, than, bay_gio: datetime) -> BanGhiPhieu | LuotCu:
    """Trong giao dịch; trượt → ghi `tho.tu_choi` và TRẢ (không ném) LuotCu để giao dịch vẫn commit; người gọi ném."""
    try:
        return kho.kiem_the_chan(than.khe_id, than.giao_id, than.luot)
    except LuotCu as e:
        kho.ghi_tu_choi(e, khe_id=than.khe_id, giao_id=than.giao_id, luot=than.luot, luc=bay_gio)
        return e


def chot(kho: KhoPhieu, than, dg: str, kq: dict, giao_id: str, bay_gio: datetime) -> dict:
    """Trong giao dịch: nhớ kết quả DỨT KHOÁT theo request_id (gửi lại cùng nội dung → kết quả này)."""
    luu_ket_qua(kho, than.request_id, giao_id=giao_id, loai="da_push", digest=dg, ket_qua=kq, luc=bay_gio)
    return kq


def sau_cas(kho: KhoPhieu, than, dg: str, p: Phieu, op_id: int, sha_cu: str | None, kq_ok: dict, kq_day: str, *,
            kho_git: Path, t: float, bay_gio: datetime, nguon) -> dict:
    """Sau `day_cas`: `khong_ro` → thao tác chờ đối soát; `tu_choi` → lệch ngoài luồng hay remote chặn; `ok` → phiếu
    còn hiệu lực thì `giao.cong_bo`, không thì hoàn tác CAS về `sha_cu` rồi 409 (H2)."""
    if kq_day == "khong_ro":
        with kho.giao_dich():
            dat_trang_thai(kho, op_id, "khong_ro", bay_gio)
        return {"cong_bo": False, "ly_do": "khong-ro"}
    if kq_day == "tu_choi":
        with kho.giao_dich():
            dat_trang_thai(kho, op_id, "bo", bay_gio)
        try:
            lech = sha_remote(kho_git, p.repo.nhanh, timeout=t) != sha_cu
        except LoiGit:
            return {"cong_bo": False, "ly_do": "khong-ro"}
        if not lech:
            return {"cong_bo": False, "ly_do": "remote-tu-choi"}
        with kho.giao_dich():
            return chot(kho, than, dg, {"cong_bo": False, "ly_do": "nhanh-bi-day-ngoai-luong"}, p.giao_id, bay_gio)
    with kho.giao_dich():
        b = the_chan(kho, than, bay_gio)
        if not isinstance(b, LuotCu):
            ghi_cong_bo(kho, du_an=p.du_an, bead_id=p.bead_id, luot=p.luot, commit=than.commit, ref=p.repo.nhanh,
                        luc=bay_gio)
            dat_trang_thai(kho, op_id, "xong", bay_gio)
            kq = chot(kho, than, dg, kq_ok, p.giao_id, bay_gio)
        else:
            dat_trang_thai(kho, op_id, "can_hoan_tac", bay_gio)
    if isinstance(b, LuotCu):
        hoan_tac(kho, op_mo(kho, p.du_an, p.bead_id), kho_git=kho_git, timeout=t, bay_gio=bay_gio)
        raise b
    nguon.don_cu(kho_git, bead_id=p.bead_id, luot=p.luot, timeout=t)
    return kq
