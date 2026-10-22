"""Kết thúc phiếu phía thợ (spec 3 §6.3, §7.4–§7.7). Luật chung: mọi kết thúc TRỪ `xong` và dừng cứng → commit WIP →
đưa lên ref tạm + `da-push` (hạn chót dừng mềm, mặc định 3 phút) → bàn giao tạm (agent gửi gần nhất, hoặc thợ dựng)
→ báo. Quá hạn chót mà chưa công bố → giữ WIP ở nhánh cục bộ `rac/…`, báo rõ snapshot là commit trạm đã công bố gần
nhất — KHÔNG ghi "đã lưu toàn bộ". `ngoai-luong` (ref công bố bị đẩy ngoài luồng) → `bi nhanh-bi-day-ngoai-luong`."""
import time

from tram.ban_giao.schema import BanGiao
from tram.cau_hinh.du_an import nap_du_an
from tram.deploy.cam import LOI_CAM, cam_tu_lenh_tho
from tram.giao_viec.khoi_qc import doc_khoi_qc
from tram.kiem.chay_lenh import moi_truong_kiem
from tram.kiem.lenh_tho import kiem_sau_xong
from tram.tho.ban_giao_tam import dung_ban_giao_tam
from tram.tho.chuan_bi import PhieuDangChay
from tram.tho.day import day_va_cong_bo, giu_nhanh_rac, luu_wip
from tram.tho.ngu_canh import NguCanhTho, rid


def bao(pc: PhieuDangChay, nc: NguCanhTho, than: dict, request_id: str | None = None):
    p = pc.p
    day_du = {"khe_id": p.khe_id, "giao_id": p.giao_id, "luot": p.luot, **than,
              "request_id": request_id or rid(p.giao_id, p.luot, "ket-thuc")}
    return pc.hop.gui_mot(nc.khach, "/api/tho/bao", day_du)


def _day(pc: PhieuDangChay, nc: NguCanhTho, commit: str, han: float) -> str:
    return day_va_cong_bo(pc.wt, pc.p, commit, khach=nc.khach, phuong_an=nc.ch.chay.day, han=han, cho=nc.cho_thu_lai)


def ket_thuc_mem(pc: PhieuDangChay, nc: NguCanhTho, ly_do: str, *, noi_dung: str = "",
                 request_id: str | None = None) -> str:
    """`ly_do`: một `LY_DO_BI` (agent, het-ngan-sach, khe-tat, estop, cau-dao, can-hoi, loi-may-tho) hoặc
    `het_han_muc`. Agent `--bi` dùng `request_id` của dòng hàng đợi."""
    han = time.monotonic() + nc.ch.chay.han_chot_dung_mem_phut * 60
    commit = luu_wip(pc.wt, f"wip: dừng ({ly_do})")
    cb = _day(pc, nc, commit, han)
    if cb == "luot-cu":
        return cb
    if cb == "ngoai-luong":
        ly_do, noi_dung = "nhanh-bi-day-ngoai-luong", "Ref công bố bị đẩy ngoài luồng — trạm không công bố"
    if cb not in ("cong_bo", "ngoai-luong"):
        rac = f"rac/{pc.p.bead_id}-{nc.dong_ho():%Y%m%dT%H%M%SZ}"
        giu_nhanh_rac(pc.wt, rac, commit)
        noi_dung = (noi_dung + f"\nChưa công bố được trước hạn chót: WIP giữ cục bộ ở nhánh {rac}; snapshot là commit "
                    "trạm đã công bố gần nhất (không phải toàn bộ việc đã làm).").strip()
    bg = pc.tt.ban_giao_tam or dung_ban_giao_tam(pc.wt, pc.p, commit, ghi_chu=noi_dung[:500])
    if nc.ch.tren_may_b:
        bg = {**bg, "commit": commit, "nhanh": pc.p.repo.nhanh, "luot": pc.p.luot}
    loai = "het_han_muc" if ly_do == "het_han_muc" else "bi"
    bao(pc, nc, {"loai": loai, "noi_dung": noi_dung[:4000], "ban_giao": bg, "commit": commit,
                 **({"ly_do": ly_do} if loai == "bi" else {})}, request_id)
    return cb


def ket_thuc_xong(pc: PhieuDangChay, nc: NguCanhTho, dong: dict) -> str:
    """CLI đã thoát. Worktree sạch (`wip: sau xong`) → lệnh kiểm của thợ → công bố → `bao.xong` nguyên kết quả."""
    p, ch = pc.p, nc.ch.chay
    if nc.ch.tren_may_b:
        from tram.tho.chot_bao_b import chot_bao_b
        dong = chot_bao_b(pc, dong)
    else:
        luu_wip(pc.wt, "wip: sau xong")
    bg = BanGiao.model_validate(dong["ban_giao"])
    ket_luan = None
    if p.buoc == "qc" and (pc.wt / bg.file_ban_giao).is_file():
        k = doc_khoi_qc((pc.wt / bg.file_ban_giao).read_text(encoding="utf-8", errors="replace"))
        ket_luan = k.ket_luan if k else None
    giao = nap_du_an(p.du_an).giao
    cam, loi_cam = (), None
    try:
        cam = cam_tu_lenh_tho(nc.khach, p.du_an, pc.wt, p.repo.nhanh_chinh)
    except OSError:
        loi_cam = LOI_CAM
    from tram.tho.deps_b import boc_kiem_b
    boc = boc_kiem_b(pc) if nc.ch.tren_may_b else pc.principal.boc
    kq = kiem_sau_xong(pc.wt, p, bg, thu_muc_log=nc.goc / "log" / "kiem", boc=boc,
                       env=moi_truong_kiem({"PATH": ch.path_cli, "LANG": "C.UTF-8"}),
                       them_cam=giao.duong_dan_cam,
                       bat_buoc=cam, loi_cam=loi_cam,
                       cho_phep_cam=giao.duong_dan_cam_cho_phep, thoi_gian_cho=ch.thoi_gian_cho_kiem_giay,
                       ket_luan_qc=ket_luan, kill=pc.principal.kill_nhom)
    cb = _day(pc, nc, kq.ban_giao.commit, time.monotonic() + ch.han_chot_dung_mem_phut * 60)
    if cb == "luot-cu":
        return cb
    if cb == "ngoai-luong":
        bao(pc, nc, {"loai": "bi", "ly_do": "nhanh-bi-day-ngoai-luong", "commit": kq.ban_giao.commit,
                     "noi_dung": "Ref công bố bị đẩy ngoài luồng — trạm không công bố kết quả xong"})
        return cb
    bao(pc, nc, {"loai": "xong", "noi_dung": dong.get("noi_dung", ""), "ban_giao": kq.ban_giao.model_dump(),
                 "commit": kq.ban_giao.commit, "loi_ban_giao": kq.loi_ban_giao[:50]}, dong["request_id"])
    return cb
