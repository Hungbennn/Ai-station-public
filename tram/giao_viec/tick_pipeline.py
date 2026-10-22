"""Vòng tick — phần đẩy pipeline (spec 4 §10 bước 1, §6.2, §6.4, §5.1 điều kiện 9): với mỗi bead trạm đang giữ
(`in_progress`, assignee trạm) tính `buoc_ke_tiep`: `kiem_lai` → chạy kiểm lại; `cot_3` → vào cột 3; `code`/`qc`
mà `not du_mot_phieu` → escalation `het-ngan-sach`. Dự án thiếu `moi_truong_kiem` → MỘT escalation mở mỗi dự án.
4a-2: `viec` chọn phần việc theo pha — pha nhanh chỉ `het_ngan_sach` (G5), pha Git làm phần còn lại."""
from datetime import datetime
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.deploy.cam import cam_tu_lenh
from tram.duong_dan import tram_home
from tram.giao_viec.dieu_kien import ASSIGNEE, ly_do_khong_giao
from tram.giao_viec.co_nguon import chan_buoc
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.kiem_lai import kiem_lai
from tram.giao_viec.ngan_sach import bat_dau_chu_ky, du_mot_phieu, ngan_sach_phieu
from tram.giao_viec.pipeline import buoc_ke_tiep, sha_code_hop_le
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.su_kien import SK, cua_so, ghi_mot_lan, moi_nhat, su_kien_bead
from tram.giao_viec.tick_cot_3 import vao_cot_3_an_toan
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.giao_viec.ung_vien import trang_thai_bead, viec_ton_cua
from tram.phieu.kho import KhoPhieu

VIEC_NHANH = frozenset({"het_ngan_sach"})
VIEC_GIT = frozenset({"kiem_lai", "cot_3", "moi_truong"})


def _esc_moi_truong_dang_mo(kho: KhoPhieu, du_an: str) -> bool:
    tao = {r[0] for r in kho.db.execute("SELECT json_extract(du_lieu, '$.escalation_id') FROM su_kien WHERE du_an = ?"
                                        " AND loai = 'escalation.tao' AND json_extract(du_lieu, '$.ly_do') ="
                                        " 'thieu-moi-truong-kiem'", (du_an,))}
    dong = {r[0] for r in kho.db.execute("SELECT json_extract(du_lieu, '$.escalation_id') FROM su_kien WHERE"
                                         " du_an = ? AND loai = 'escalation.dong'", (du_an,))}
    return bool(tao - dong)


def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: datetime) -> str:
    w = cua_so(ds)
    code = moi_nhat(w, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "code")
    p, sha = kho.lay(code.du_lieu["giao_id"]).phieu, sha_code_hop_le(w)
    if p.can_lenh_kiem and bo.boc is None and bo.kiem_tu_xa is None:
        return "cho_boc"                                 # chưa có principal tram-kiem (S6) — không chạy dưới quyền trạm
    ham = bo.kiem_tu_xa or kiem_lai
    them = {'luot': p.luot} if bo.kiem_tu_xa is not None else {}
    kq = ham(kg, da, giao_id=p.giao_id, commit=sha, lenh_kiem=list(p.lenh_kiem),
                  lenh_cho_phep=list(p.lenh_cho_phep),
                  chay_lenh=p.can_lenh_kiem, thu_muc=bo.thu_muc_kiem or tram_home() / "kiem",
                  thu_muc_log=tram_home() / "log" / "kiem-lai", boc=bo.boc or (lambda a: a), env_goc=bo.env_goc,
                  don_sach=bo.don_sach, kill=bo.kill, cong=bo.cong, boc_luot=bo.boc_luot,
                  them_cam=cam_tu_lenh(kho.db, kg, da, sha), **them)
    if kq.loi is not None:
        tao_escalation(bd, kho, da.ten, b, ly_do=kq.loi, cau_hoi="", giao_id=p.giao_id, nguon=f"kl-{sha}", luc=luc)
        if kq.loi in ("thieu-moi-truong-kiem", "cay-khac-nguon"):
            return "escalation"                          # không ghi kiem.lai: trả lời xong thì kiểm lại (dòng 5)
    from tram.quan_kiem.fencing import ghi_ket_qua
    return ghi_ket_qua(kho, da, p, sha, {
        "giao_id": p.giao_id, "bead_id": b.id, "luot": p.luot, "commit": sha,
        "digest_tieu_chi": digest_tieu_chi(list(p.tieu_chi)), "dat": kq.dat,
        "nguon_kiem": "uq" if bo.kiem_tu_xa is not None and p.can_lenh_kiem else "legacy",
        "ket_qua": list(kq.ket_qua), "digest_log": kq.digest_log, "cham_cam": list(kq.cham_cam)}, luc)


def day_pipeline(bo, kho: KhoPhieu, da: DuAn, bd, beads: list, san_sang: set[str], kg: Path | None,
                 luc: datetime, *, viec: frozenset[str] = VIEC_NHANH | VIEC_GIT) -> dict[str, int]:
    theo_id, ton, dem = {b.id: b for b in beads}, viec_ton_cua(kho, da.ten), {}
    merge = feature_da_merge(kho, da, beads, kg) if kg is not None else frozenset()
    for b in beads:
        ly = ly_do_khong_giao(b, theo_id, san_sang, da, merge)
        if ly == "thieu-moi-truong-kiem" and "moi_truong" in viec and not _esc_moi_truong_dang_mo(kho, da.ten):
            tao_escalation(bd, kho, da.ten, b, ly_do=ly, cau_hoi="", giao_id=None, nguon=f"du-an-{luc:%Y%m%d%H%M}",
                           luc=luc)
            dem["escalation"] = dem.get("escalation", 0) + 1
        if ly is not None or b.status != "in_progress" or b.assignee != ASSIGNEE:
            continue
        ds = su_kien_bead(kho, da.ten, b.id)
        buoc, kq = buoc_ke_tiep(ds, trang_thai_bead(kho, da.ten, b, theo_id, ton)), None
        if kg is not None and buoc in ("kiem_lai", "cot_3") and chan_buoc(kho, da, b, theo_id, kg, luc):
            continue
        if buoc == "kiem_lai" and kg is not None and "kiem_lai" in viec:
            kq = _kiem_lai(bo, kho, da, bd, b, ds, kg, luc)
        elif buoc == "cot_3" and kg is not None and "cot_3" in viec:
            kq = vao_cot_3_an_toan(bd, kho, kg, da, b, luc, gitnexus=bo.p4c.gitnexus)
        elif buoc in ("code", "qc") and "het_ngan_sach" in viec and not du_mot_phieu(
                kho, ds, ngan_sach_phieu(buoc, da.giao.ngan_sach), da.giao.ngan_sach.bead):
            kq = "het_ngan_sach" if tao_escalation(bd, kho, da.ten, b, ly_do="het-ngan-sach", cau_hoi="", giao_id=None,
                                                   nguon=f"ns-{bat_dau_chu_ky(ds)}", luc=luc) else None
        if kq:
            dem[kq] = dem.get(kq, 0) + 1
    return dem
