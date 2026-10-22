"""Một lần chạy CLI của phiếu (spec 3 §7.2, §7.6, §7.8, §8.3; 3a-1 G35). TRƯỚC MỖI lần (kể cả lần 2, 3): `lan` ≤
ngân sách, trần thời gian/token của phiếu, trần giờ/ngày cục bộ, cầu dao cục bộ, hạn mức đã biết ≥ ngưỡng. Thứ tự
gửi: `chay.bat_dau` ghi BỀN trước khi spawn → spawn → `chay.xong` (cùng `lan`, request_id tất định)."""
import threading
from datetime import datetime, timedelta

from tram.chay_cli.giao_dien import KetQuaChay, ket_thuc_tu
from tram.chay_cli.lenh_claude import env_cli
from tram.chay_cli.bo_cli import BO_CLI
from tram.tho.co_model import lenh_model, dung_model
from tram.duong_dan import doc_luc
from tram.han_muc.log_claude import doc_log_claude, gop_han_muc
from tram.han_muc.luat import cham_nguong_ngung
from tram.han_muc.mo_hinh import lam_moi
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.ban_giao_tam import goi_lan_sau
from tram.tho.chuan_bi import PhieuDangChay, gui_su_kien
from tram.tho.mo_coi import ghi_pid
from tram.tho.ngu_canh import NguCanhTho

NGUONG_NGUNG = 90.0                        # = han_muc.ngung mặc định của trạm (§8.2 luật 1)


def giay_con_lai(pc: PhieuDangChay, bay_gio: datetime) -> float:
    return (doc_luc(pc.tt.nhan_luc) + timedelta(minutes=pc.p.ngan_sach.phut) - bay_gio).total_seconds()


def ly_do_khong_chay(pc: PhieuDangChay, nc: NguCanhTho, bay_gio: datetime) -> str | None:
    """`het-ngan-sach` | `cau-dao` | `het_han_muc` | None (được chạy)."""
    ns, tt = pc.p.ngan_sach, pc.tt
    if tt.lan >= ns.so_lan_chay or tt.token_ra >= ns.token_ra or giay_con_lai(pc, bay_gio) <= 0 \
            or not pc.so.con_cho_chay(bay_gio, nc.ch.chay):
        return "het-ngan-sach"
    if pc.so.cau_dao_ngat(bay_gio):
        return "cau-dao"
    hm = pc.so.doc_han_muc()
    if hm is not None and cham_nguong_ngung(lam_moi(hm, pc.p.khe_id, bay_gio), ngung=NGUONG_NGUNG):
        return "het_han_muc"
    return None


def _goi(pc: PhieuDangChay, lan: int):
    if lan == 1:
        return pc.wt / ".tram" / "goi.md"
    g = pc.wt / ".tram" / f"goi-{lan}.md"
    g.write_text(goi_lan_sau(pc.p.goi_ngu_canh, pc.tt.ban_giao_tam, lan), encoding="utf-8")
    return g


def chay_mot_lan(pc: PhieuDangChay, nc: NguCanhTho, dung: threading.Event) -> KetQuaChay:
    p, tt, so, ch = pc.p, pc.tt, pc.so, nc.ch.chay
    lan = tt.lan + 1
    gui_su_kien(nc, pc.hop, p, "chay.bat_dau", {"lan": lan}, lan)
    tt.lan = lan
    pc.luu()
    so.ghi_lan_chay(nc.dong_ho())
    env = env_cli(thu_muc_cau_hinh=pc.k.thu_muc_cau_hinh, giao_id=p.giao_id, hang_doi=pc.hang_doi, wt=pc.wt,
                  path=ch.path_cli, ma_giao=p.ma_giao if ch.nho_url else None, nho_url=ch.nho_url)
    if nc.ch.tren_may_b:
        env |= {"TRAM_GIT_QUA_QUAN_LY": "1", "TRAM_NHANH": p.repo.nhanh}
    bo = BO_CLI[pc.k.cli]
    env[bo.bien_thu_muc] = env.pop("CLAUDE_CONFIG_DIR")
    from tram.tho.deps_b import boc_kiem_b
    boc = boc_kiem_b(pc) if nc.ch.tren_may_b else pc.principal.boc
    cli = (nc.tao_cli or bo.tao_chay)(boc, khe_id=p.khe_id, kill=pc.principal.kill_nhom,
                     khi_bat_dau=lambda pid: ghi_pid(so.pid, pid=pid, giao_id=p.giao_id, luot=p.luot, lan=lan),
                     khi_han_muc=so.luu_han_muc, tran_token_ra=p.ngan_sach.token_ra - tt.token_ra)
    hen = threading.Timer(max(0.0, giay_con_lai(pc, nc.dong_ho())), dung.set)
    hen.start()
    try:
        kq = cli.chay(lenh_model(bo.lenh(worktree=pc.wt, thu_muc_phieu=pc.thu_muc, vai=p.vai,
                              lenh_cho_phep=p.lenh_cho_phep, settings=pc.settings, mcp=pc.mcp),
                                  pc.k.cli, pc.k.models, p.co), cwd=pc.wt, env=env,
                      stdin=_goi(pc, lan), log=nc.goc / "log" / "chay" / f"{p.giao_id}-{p.luot}-{lan}.jsonl",
                      dung=dung, nguon=nc.nguon_han_muc(pc.k.cli))
    except LoiThuHoi:
        raise                           # P1: chưa xác nhận thu hồi → GIỮ pid cho dọn mồ côi lần khởi động sau
    except BaseException:
        so.pid.unlink(missing_ok=True)
        raise
    finally:
        hen.cancel()
    nc.don_khe(pc.k)                    # A02: còn tàn dư (lẩn khỏi tầm chụp) → LoiThuHoi, GIỮ pid, không lần sau
    so.pid.unlink(missing_ok=True)
    tt.token_ra += kq.token_ra
    pc.luu()
    kt = ket_thuc_tu(kq) if dung_model(p.co, kq) else "loi_he"
    gui_su_kien(nc, pc.hop, p, "chay.xong", {
        "lan": lan, "ket_thuc": kt, "ma_thoat": kq.ma_thoat,
        "mo_hinh": None if p.co and kq.model_lech else kq.mo_hinh, "token_vao": kq.token_vao,
        "token_ra": kq.token_ra, "token_cache_doc": kq.token_cache_doc, "token_cache_ghi": kq.token_cache_ghi,
        "thoi_gian_ms": kq.thoi_gian_ms, "digest_log": kq.digest_log, "reset_luc": kq.reset_luc}, lan)
    bay = nc.dong_ho()
    # nguồn lùi §8.1: log của CLI chỉ có rate_limit_info khi đã bị chặn
    if pc.k.cli == "claude" and kt in ("loi", "loi_he"):
        hm = doc_log_claude(pc.k.thu_muc_cau_hinh, khe_id=p.khe_id, bay_gio=bay, nguon=nc.nguon_han_muc(pc.k.cli))
        if hm is not None:
            so.luu_han_muc(gop_han_muc(so.doc_han_muc(), hm))
    if kt == "het_han_muc":
        so.ngat_cau_dao(doc_luc(kq.reset_luc) if kq.reset_luc else bay + timedelta(minutes=60), "het-han-muc")
    if so.dem_loi_he(kt) >= 3:
        so.ngat_cau_dao(bay + timedelta(minutes=60), "loi-he")
    return kq
