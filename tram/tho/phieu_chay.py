"""Chạy trọn MỘT phiếu trên máy thợ (spec 3 §6.3, §7.1–§7.7): chuẩn bị → các lần chạy CLI (≤ `so_lan_chay`, kiểm
trần trước MỖI lần) → kết thúc đúng một kiểu. Dừng cứng (`luot-cu`, `thu-hoi` từ nhịp tim) → kill, KHÔNG push, KHÔNG
báo. Dừng mềm (`khe-tat`, `estop`, `cau-dao`, `can-hoi`) → kill rồi `ket_thuc_mem`. `vk` cung cấp `lenh` (lệnh dừng
mới nhất của nhịp tim), `dung` (Event của lần chạy hiện tại) và `buoc` (buoc_tho gửi trong nhịp tim)."""
import os
import shutil
import threading
import subprocess
from pathlib import Path

from tram.kiem.vong_doi import LoiThuHoi
from tram.phieu.mo_hinh import Phieu
from tram.tho.chuan_bi import PhieuDangChay, chuan_bi
from tram.tho.co_model import dung_model
from tram.tho.day import xoa_ref_tam
from tram.tho.ket_thuc import ket_thuc_mem, ket_thuc_xong
from tram.tho.mo_coi import dat_khoa, go_khoa
from tram.tho.mot_lan import chay_mot_lan, ly_do_khong_chay
from tram.tho.ngu_canh import NguCanhTho, rid
from tram.tho.principal_khe import lenh_trao_quyen
from tram.tho.so_khe import TrangThaiPhieu
from tram.tho.theo_doi import DUNG_CUNG, TheoDoi


def bao_khong_chay(nc: NguCanhTho, vk, tt: TrangThaiPhieu, ly_do: str) -> None:
    p = Phieu.model_validate(tt.phieu)
    vk.hop.gui_mot(nc.khach, "/api/tho/bao", {
        "khe_id": p.khe_id, "giao_id": p.giao_id, "luot": p.luot, "loai": "bi", "ly_do": ly_do,
        "noi_dung": f"Thợ không chạy được phiếu: {ly_do}", "request_id": rid(p.giao_id, p.luot, "ket-thuc")})
    vk.so.xoa_phieu()


def don_phieu(pc: PhieuDangChay, nc: NguCanhTho) -> None:
    go_khoa(pc.wt)
    xoa_ref_tam(pc.wt, pc.p)
    if nc.ch.tren_may_b:
        from tram.tho.luot_b import don_luot_b
        don_luot_b(pc, nc)
    elif getattr(pc.principal, "user", None):
        git_wt = Path(subprocess.run(["git", "-C", str(pc.wt), "rev-parse", "--absolute-git-dir"],
                                     capture_output=True, text=True, check=True).stdout.strip())
        for lenh in lenh_trao_quyen(pc.wt, git_wt, pc.thu_muc, user=pc.principal.user, thu=True):
            nc.chay_lenh(lenh, check=False, capture_output=True)
    pc.so.xoa_phieu()
    pc.hop.gui(nc.khach)
    pc.hop.don()
    shutil.rmtree(pc.thu_muc, ignore_errors=True)


def _mot_vong(pc: PhieuDangChay, nc: NguCanhTho, vk) -> str | None:
    """Một lần chạy; trả kết thúc ("cung", "xong", …) hoặc None để chạy lần kế."""
    if vk.lenh in (*DUNG_CUNG, "tat-tho"):
        return "cung" if vk.lenh in DUNG_CUNG else "tat-tho"
    if (ly := vk.lenh or ly_do_khong_chay(pc, nc, nc.dong_ho())) is not None:
        ket_thuc_mem(pc, nc, ly)
        return ly
    vk.dung, vk.buoc = threading.Event(), "chay"
    td = TheoDoi(pc, nc, vk.dung, lenh_nhip=lambda: vk.lenh).bat_dau()
    try:
        kq = chay_mot_lan(pc, nc, vk.dung)
    except BaseException:
        td.dung_lai()                           # bs-863.16: có hạn; chưa dừng → LoiThuHoi thắng lỗi gốc
        raise
    td.ket_thuc()
    if vk.lenh in (*DUNG_CUNG, "tat-tho"):
        return "cung" if vk.lenh in DUNG_CUNG else "tat-tho"
    vk.buoc = "kiem"
    if td.can_hoi:                            # Q6 luôn thắng báo xong cùng lần đọc
        ket_thuc_mem(pc, nc, "can-hoi")
        return "can-hoi"
    if not dung_model(pc.p.co, kq):
        ket_thuc_mem(pc, nc, "sai-model")
        return "sai-model"
    if td.xong:
        ket_thuc_xong(pc, nc, td.xong)
        return "xong"
    if td.bi:
        pc.tt.ban_giao_tam = td.bi.get("ban_giao") or pc.tt.ban_giao_tam
        ket_thuc_mem(pc, nc, "agent", noi_dung=td.bi.get("noi_dung", ""), request_id=td.bi["request_id"])
        return "agent"
    ly = ("can-hoi" if td.can_hoi else vk.lenh or ("het_han_muc" if kq.het_han_muc else None)
          or ("het-ngan-sach" if kq.bi_dung else None))
    if ly is not None:
        ket_thuc_mem(pc, nc, ly, noi_dung="Vượt trần thời gian/token của phiếu" if ly == "het-ngan-sach" else "")
        return ly
    return None                                 # CLI thoát mà chưa xong/bi → lần kế (nếu còn ngân sách)


def chay_phieu(nc: NguCanhTho, vk, tt: TrangThaiPhieu) -> str:
    nc.don_khe(vk.k)                            # A02: khe sạch theo UID TRƯỚC mọi việc của phiếu (không → LoiThuHoi)
    vk.buoc = "chuan_bi"
    pc = chuan_bi(nc, vk.k, vk.so, vk.hop, tt)
    if isinstance(pc, str):
        bao_khong_chay(nc, vk, tt, pc)
        return pc
    if not dat_khoa(pc.wt, pid=os.getpid(), giao_id=pc.p.giao_id):
        bao_khong_chay(nc, vk, tt, "loi-may-tho")
        return "loi-may-tho"
    vk.pc, kt = pc, "tat-tho"
    try:
        while (kt := _mot_vong(pc, nc, vk)) is None:
            pass
    except LoiThuHoi:
        kt = "tat-tho"                          # P1: tiến trình có thể còn sống — giữ worktree/phiếu, vòng khe dừng
        raise
    finally:
        vk.pc, vk.buoc = None, "ranh"
        if kt == "tat-tho":
            go_khoa(pc.wt)                      # giữ phieu.json + hộp thư: khởi động lại chạy tiếp
            if nc.ch.tren_may_b:
                from tram.tho.luot_b import dong_cong
                dong_cong(pc.wt.parent, nc)
        else:
            don_phieu(pc, nc)
    return kt
