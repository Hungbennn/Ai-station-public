"""Vòng tick bước 0 (spec 4 §10, §9): xử lý CÔNG VIỆC CHỜ phần 3 ghi khi phiếu hết hiệu lực, và câu hỏi của agent.

Mỗi công việc: xét kết thúc → (escalation nếu cần) → `qc.ket_qua` → `giao.ket_thuc` (xác nhận đã xử lý, kèm kết
luận) → đánh dấu xong. Mọi bước idempotent theo nguồn — restart giữa chừng thì làm lại được."""
import json
from datetime import datetime
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.deploy.cam import cam_tu_lenh
from tram.de_nghi.bi_chan import cau_hoi_esc
from tram.giao_viec.escalation import LY_DO_BI, LY_DO_HOI, ma_escalation, tao_escalation
from tram.giao_viec.su_kien import cong_bo_cua_luot, da_co, ghi_mot_lan, moi_nhat, su_kien_bead
from tram.giao_viec.xet_spec import xet_xong_spec
from tram.giao_viec.xet_xong import xet_xong_code, xet_xong_qc
from tram.phieu.cong_viec import CongViecCho, danh_dau_xong_viec
from tram.kiem.diff import diff_cham_cam
from tram.phieu.kho import KhoPhieu

LOAI_BAO = {"xong": "bao.xong", "bi": "bao.bi", "het_han_muc": "bao.het_han_muc", "thu_hoi": "giao.thu_hoi"}


def _xet(kho: KhoPhieu, cv: CongViecCho, du_an: DuAn, kho_git: Path, luc: datetime):
    """→ (ly_do, loi, commit, escalation (ly_do, câu hỏi) | None)."""
    p = kho.lay(cv.giao_id).phieu
    ds = su_kien_bead(kho, cv.du_an, cv.bead_id)
    bao = moi_nhat(ds, LOAI_BAO[cv.ket_thuc], lambda s: s.du_lieu.get("giao_id") == p.giao_id)
    d = bao.du_lieu if bao else {}
    if cv.ket_thuc == "bi":
        ly = d.get("ly_do")
        esc = LY_DO_BI.get(ly)                       # TC (D-6): nút bị chặn bật → lý do của agent được lọc
        return ly, (), None, (esc, cau_hoi_esc(kho.db, cv.du_an, esc, d.get("noi_dung", ""))) if esc else None
    if cv.ket_thuc != "xong":
        return d.get("ly_do") or cv.ket_thuc, (), None, None             # het_han_muc, thu_hoi: giao lại
    sha = cong_bo_cua_luot(ds, p.luot)
    if p.co and p.co.get("pha"):
        from tram.giao_viec.co_xet_plan import xet_plan
        if sha:
            cam = cam_tu_lenh(kho.db, kho_git, du_an, sha)
            cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", sha,
                                them=du_an.giao.duong_dan_cam, bat_buoc=cam,
                                cho_phep=du_an.giao.duong_dan_cam_cho_phep)
            if cham:
                return "dong-file-cau-hinh", (), sha, ("dong-file-cau-hinh", "Plan chạm đường cấm")
        return xet_plan(kho, kho_git, p, d, sha, luc)
    if p.buoc in ("code", "spec"):                                       # spec: 4b — §7.2
        cam = cam_tu_lenh(kho.db, kho_git, du_an, sha) if sha else ()      # TM-3 vòng 2, D89
        kl = (xet_xong_code if p.buoc == "code" else xet_xong_spec)(kho_git, p, d, sha, du_an, them_cam=cam)
        esc = ("dong-file-cau-hinh", f"Diff chạm: {', '.join(kl.cham_cam)}") if kl.cham_cam else None
        return kl.ly_do, kl.loi, kl.commit, esc
    kq = xet_xong_qc(kho_git, p, d, sha)
    if kq.ket_luan is not None:
        ghi_mot_lan(kho, cv.du_an, "qc.ket_qua", {
            "giao_id": p.giao_id, "bead_id": p.bead_id, "commit_code": p.repo.cha, "commit_qc": kq.commit_qc,
            "ket_luan": kq.ket_luan, "phat_hien": list(kq.phat_hien), "ly_do": kq.ly_do},
            bead_id=p.bead_id, luc=luc, khoa=("giao_id",))
    esc = ("qc-doi-ma", "") if kq.ly_do == "qc-doi-ma" else None
    return kq.ly_do, (), kq.commit_qc, esc


def xu_ly_cong_viec(kho: KhoPhieu, cv: CongViecCho, *, du_an: DuAn, bd, kho_git: Path | None,
                    luc: datetime) -> bool:
    """False = chưa xử lý được (kho kiểm chưa có — chờ 3a-2/S7); công việc giữ nguyên để vòng sau làm."""
    p = kho.lay(cv.giao_id).phieu
    if cv.ket_thuc == "xong" and kho_git is None:
        return False
    ly_do, loi, commit, esc = _xet(kho, cv, du_an, kho_git, luc)
    if esc is not None:
        tao_escalation(bd, kho, cv.du_an, bd.mot(cv.bead_id), ly_do=esc[0], cau_hoi=esc[1], giao_id=p.giao_id,
                       nguon=p.giao_id, luc=luc)
    ghi_mot_lan(kho, cv.du_an, "giao.ket_thuc", {"giao_id": p.giao_id, "luot": p.luot, "buoc": p.buoc,
                                                 "ket_thuc": cv.ket_thuc, "ly_do": ly_do, "commit": commit,
                                                 "loi": list(loi)[:20]},
                bead_id=p.bead_id, luc=luc, khoa=("giao_id",))
    danh_dau_xong_viec(kho, cv.id, luc)
    return True


def escalation_cau_hoi(kho: KhoPhieu, du_an: DuAn, bd, luc: datetime) -> int:
    """`bao.can_hoi` → escalation ngay (§9); phiếu đã dừng mềm (phần 3). Một escalation mỗi câu hỏi."""
    so = 0
    for i, bead_id, d in kho.db.execute("SELECT id, bead_id, du_lieu FROM su_kien WHERE du_an = ? AND loai ="
                                        " 'bao.can_hoi' ORDER BY id", (du_an.ten,)).fetchall():
        d = json.loads(d)
        ly_do = LY_DO_HOI.get(d.get("loai_hoi"), "agent-can-hoi")
        if da_co(kho, du_an.ten, "escalation.tao", {"ma_thao_tac": ma_escalation(du_an.ten, bead_id, ly_do,
                                                                                  f"hoi-{i}")}):
            continue
        tao_escalation(bd, kho, du_an.ten, bd.mot(bead_id), ly_do=ly_do,
                       cau_hoi=cau_hoi_esc(kho.db, du_an.ten, ly_do, d.get("noi_dung", "")),
                       giao_id=d.get("giao_id"), nguon=f"hoi-{i}", luc=luc)
        so += 1
    return so
