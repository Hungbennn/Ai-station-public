"""Đầu vào cỡ từ Beads và SHA do trạm công bố; lỗi Git giữ chờ, không đọc HEAD thay SHA."""
import hashlib
import json
import subprocess

from tram.cham_cot.luat_cung import kiem, bi_chan_boi
from tram.deploy.cam import cam_tu_lenh
from tram.giao_viec.co_dem import cham_co, pham_vi
from tram.giao_viec.co_plan import cong_plan
from tram.giao_viec.co_bao_ve import nguy_hiem
from tram.giao_viec.su_kien import su_kien_bead, moi_nhat, ghi_mot_lan
from tram.kiem.diff import tep_doi
from tram.giao_viec.git_kiem import _git

BAN_GIAO = "docs/handovers/"  # file bàn giao bắt buộc — không tính vào phạm vi/cỡ


def quyet_dinh(kho, da, b, theo_id, kg):
    ds = su_kien_bead(kho, da.ten, b.id)
    code = [s for s in ds if s.loai == "giao.nhan" and s.du_lieu.get("buoc") == "code"]
    luot = {s.du_lieu["luot"] for s in code}
    goc = code[0].du_lieu["cha"] if code else None
    diff, cam = set(), set(da.giao.duong_dan_cam)
    main = _git(kg, "rev-parse", "--verify", f"origin/{da.nhanh_chinh}^{{commit}}", timeout=60).stdout.decode().strip()
    cam.update(cam_tu_lenh(kho.db, kg, da, main))
    for s in ds:
        if s.loai == "giao.cong_bo" and s.du_lieu.get("luot") in luot:
            sha = s.du_lieu["commit"]
            diff.update(f for f in tep_doi(kg, goc, sha) if not f.startswith(BAN_GIAO))
            cam.update(cam_tu_lenh(kho.db, kg, da, sha))
    nguy = bool(kiem(b, da, theo_id).cham)
    cha, da_doc = b.parent, set()
    while cha and cha not in da_doc and cha in theo_id:
        da_doc.add(cha)
        c = theo_id[cha]
        nguy |= bool(kiem(c, da, theo_id).cham) or nguy_hiem(
            pham_vi(c.design) or (), c.labels, (*da.theo_co["nguy_hiem"], *cam), ben=da.ten == "ben-station")
        cha = c.parent
    q = cham_co(b, da.theo_co, theo_id, diff=diff, ben=da.ten == "ben-station", nguy_hiem=nguy,
                phu_thuoc_ro=not cha and not bi_chan_boi(b, theo_id)
                and all(p.depends_on_id in theo_id for p in b.phu_thuoc), them_cam=cam)
    q["goc_plan"] = main
    q["diff_ngoai"] = sorted(diff - set(pham_vi(b.design) or ()))
    q["lam_lai"] = max(0, len(code) - 1)
    q["yeu_cau"] = hashlib.sha256(json.dumps([b.description, b.design, b.acceptance_criteria]).encode()).hexdigest()
    return q


def ly_do(ds, da, q):
    if q["diff_ngoai"]:
        return "xac-nhan-pham-vi"
    if da.ten != "ben-station" and not da.theo_co["nguy_hiem"]:
        return "thieu-bo-bao-ve"
    if q["co"] == "lon" and not da.theo_co["lenh_ca_bo"]:
        return "thieu-lenh-ca-bo"
    return cong_plan(ds, q)


def ghi_cho(kho, da, b, ly, luc):
    ghi_mot_lan(kho, da.ten, "co.cho", {"bead_id": b.id, "ly_do": ly,
                 "ban_luat": da.theo_co["ban_luat"]}, bead_id=b.id, luc=luc,
                 khoa=("bead_id", "ly_do", "ban_luat"))


def chan_buoc(kho, da, b, theo_id, kg, luc):
    if da.theo_co is None:
        return None
    ds = su_kien_bead(kho, da.ten, b.id)
    cu = moi_nhat(ds, "giao.nhan")
    if cu and not cu.du_lieu.get("co"):
        return None
    try:
        q = quyet_dinh(kho, da, b, theo_id, kg)
        ly = ly_do(ds, da, q)
        if not q["diff_ngoai"] and danh_dau_code_lai(kho, da, b, ds, q, luc):
            ly = ly or "code-lai-theo-co"
    except (OSError, ValueError, subprocess.SubprocessError):
        ly = "khong-doc-duoc-pham-vi"
    if ly:
        ghi_cho(kho, da, b, ly, luc)
    return ly


def can_code_lai(ds, q):
    code = moi_nhat(ds, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "code")
    cu = code.du_lieu.get("co") if code else None
    return bool(cu) and ("nho", "vua", "lon").index(cu["co"]) < ("nho", "vua", "lon").index(q["co"])


def danh_dau_code_lai(kho, da, b, ds, q, luc):
    if not can_code_lai(ds, q):
        return False
    code = moi_nhat(ds, "giao.nhan", lambda s: s.du_lieu.get("buoc") == "code")
    ghi_mot_lan(kho, da.ten, "co.can-code-lai", {"giao_id": code.du_lieu["giao_id"]},
                 bead_id=b.id, luc=luc, khoa=("giao_id",))
    return True
