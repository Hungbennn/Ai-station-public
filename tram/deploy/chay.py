"""Chốt M/L/cài đặt; Uq kiểm M, quyền dự án chạy triển khai. Không checkout mã dưới trạm."""
from tram.chu import estop
from tram.deploy.ban import ban_an_toan, chon_ban, kiem_ban, pham_vi_du
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy.duong import DuongDeploy
from tram.deploy.ghi import ghi, ket_thuc, ma_chuoi
from tram.deploy.git import la_to_tien
from tram.deploy.thuc_hien import thuc_hien
from tram.deploy.trang_thai import doc_su_kien, ma, merge_chua_deploy, tu_merge_cho_deploy
from tram.tu_dong.cong_kiem import cong_mo
from tram.tu_dong.khoa import ly_do_chan
from tram.tu_dong.luu import doc_trang_thai


def huy(db, ten, yc, ly):
    ghi(db, ten, "deploy.huy", {"ma_thao_tac": ma(yc), "commit": yc.du_lieu.get("commit"), "ly_do": ly})
    return "deploy_huy"


def phu(kg, ds, commit):
    return [s.id for s in merge_chua_deploy(ds) if la_to_tien(kg, s.du_lieu["merge_commit"], commit)]


def chuoi(db, kg, da, commit, nguon, ma_yc, bat_ghi, yc=None):
    m = ma_chuoi(da.ten, commit, nguon, ma_yc)
    ds = doc_su_kien(db, da.ten)
    if any(s.loai == "deploy.bat_dau" and ma(s) == m for s in ds):
        return "deploy_da_co"
    if chua_doi_soat(ds) or not cong_mo():
        return "deploy_cho_doi_soat"
    tt = doc_trang_thai(db, da.ten)
    if yc is not None and yc.du_lieu.get("phien_ban") != tt.phien_ban:
        return huy(db, da.ten, yc, "cai_dat_doi")
    try:
        duong = DuongDeploy(da.ten, tt.cai_dat)
    except (OSError, ValueError, KeyError):
        return "deploy_cho_duong"
    if not kiem_ban(db, kg, da, commit, tt.phien_ban):
        return "deploy_cho_kiem"
    nen = duong.goi("chuan_bi", m, commit, "")
    if not nen or not all(nen[k] for k in ("dat", "da_dung", "san_sang")):
        return "deploy_cho_ban_nen"
    truoc = nen["ban_truoc"]
    if not ban_an_toan(kg, da, truoc, commit):
        return "deploy_cho_cam"
    if not pham_vi_du(kg, ds, truoc, commit) and nguon != "dai_ca":
        return "deploy_cho_pham_vi"
    moi = doc_trang_thai(db, da.ten)
    ly = ly_do_chan(moi, viec="deploy_tay" if yc else "deploy", bat_ghi=bat_ghi(da.ten),
                   estop_bat=estop.dang_bat())
    ds = doc_su_kien(db, da.ten)
    if (ly or moi.phien_ban != tt.phien_ban or not cong_mo() or chua_doi_soat(ds)
            or chon_ban(kg, ds, da.nhanh_chinh) != commit):
        return huy(db, da.ten, yc, "cai_dat_hoac_ban_doi") if yc else "deploy_hoan"
    if yc is None:
        tm = tu_merge_cho_deploy(ds, ma_nguon=ma_yc)
        if tm is None or tm.du_lieu.get("merge_commit") != commit:
            return "deploy_hoan"
    ghi(db, da.ten, "deploy.bat_dau", {"ma_thao_tac": m, "commit": commit, "commit_truoc": truoc,
                                      "nguon": nguon, "bao_gom": phu(kg, ds, commit),
                                      "phien_ban": tt.phien_ban, "cai_dat": tt.cai_dat.phang(),
                                      **({"yeu_cau": ma(yc)} if yc else {})})
    kq = thuc_hien(db, da.ten, duong, m, commit, truoc)
    ket_thuc(db, da.ten, m, kq)
    return f"deploy_{kq}"
