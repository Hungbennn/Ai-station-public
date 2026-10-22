"""Một khoá/dự án, đối soát crash trước chọn bản; không chọn HEAD thay merge đã xác minh."""
import subprocess
from collections import Counter
import yaml
from tram.cau_hinh.bat_ghi import bat_ghi as doc_bat_ghi
from tram.chu import estop
from tram.deploy.ban import chon_ban
from tram.deploy.chay import chuoi, huy, phu
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy.ghi import ghi, ket_thuc
from tram.deploy.git import sha_cua
from tram.deploy.trang_thai import (cuoi, chuoi_dang_do, da_ghi_nhan, doc_su_kien, ma,
                                    merge_chua_deploy, tu_merge_cho_deploy, yeu_cau_cho)
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import giu_khoa, KiemLaiDangBan
from tram.tu_dong.khoa import ly_do_chan
from tram.tu_dong.luu import doc_trang_thai


def bat_ghi_an_toan(ten):
    try:
        return doc_bat_ghi(ten)
    except (OSError, ValueError, AttributeError, yaml.YAMLError):
        return False


def _cho(db, ten, c, ly):
    d = {"commit": c, "ly_do": ly}
    cu = cuoi(doc_su_kien(db, ten), "deploy.cho")
    if cu is None or cu.du_lieu != d:
        ghi(db, ten, "deploy.cho", d)


def _buoc(bo, kho, da, bat_ghi, dem):
    db = kho.db
    for bd in chuoi_dang_do(doc_su_kien(db, da.ten)):
        ket_thuc(db, da.ten, ma(bd), "khong_ro")
        dem["deploy_khong_ro"] += 1
    ds = doc_su_kien(db, da.ten)
    if chua_doi_soat(ds):
        return
    yc = yeu_cau_cho(ds)
    if estop.dang_bat():
        if yc:
            dem[huy(db, da.ten, yc, "estop")] += 1
        return
    if (kg := bo.kho_git(da)) is None:
        return
    tt = doc_trang_thai(db, da.ten)
    ly = ly_do_chan(tt, viec="deploy_tay" if yc else "deploy", bat_ghi=bat_ghi(da.ten), estop_bat=False)
    if yc and ly:
        dem[huy(db, da.ten, yc, ly[0])] += 1
        return
    tm, gom = tu_merge_cho_deploy(ds), merge_chua_deploy(ds)
    if not yc and not (gom and bat_ghi(da.ten) and tt.cai_dat.du_lenh):
        return
    c = chon_ban(kg, ds, da.nhanh_chinh)
    if not c:
        return
    bao = phu(kg, ds, c)
    moi = bool(bao and not da_ghi_nhan(ds, c, bao, cho=ly))
    if not yc and moi:
        ghi(db, da.ten, "deploy.san_sang", {"commit": c, "so_merge": len(bao), "bao_gom": bao, "cho": ly})
    if yc:
        if yc.du_lieu.get("commit") != c:
            dem[huy(db, da.ten, yc, "ban_moi_hon")] += 1
            return
        kq = chuoi(db, kg, da, c, "dai_ca", ma(yc), bat_ghi, yc)
    elif tm and tm.du_lieu.get("merge_commit") == c and not ly:
        kq = chuoi(db, kg, da, c, "tu_dong", f"sk-{tm.id}", bat_ghi)
    else:
        if moi:
            dem["san_sang_deploy"] += 1
        return
    dem[kq] += 1
    _cho(db, da.ten, c, kq if kq.startswith("deploy_cho_") else "")


def buoc_deploy(bo, kho, da, *, bat_ghi=bat_ghi_an_toan):
    dem = Counter()
    try:
        with giu_khoa(tram_home() / "deploy-khoa" / f"{da.ten}.lock"):
            _buoc(bo, kho, da, bat_ghi, dem)
    except KiemLaiDangBan:
        return {"deploy_dang_chay": 1}
    except (OSError, subprocess.SubprocessError):
        dem["deploy_chuan_bi_loi"] += 1
    return dict(dem)
