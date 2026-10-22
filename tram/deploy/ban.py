"""Chỉ chọn merge đã xác minh; kiểm M qua cùng Uq, không suy từ QC của H."""
import fnmatch
import hashlib
import json

from tram.deploy.git import _git, la_to_tien
from tram.deploy.ghi import ghi
from tram.deploy.trang_thai import merge_chua_deploy
from tram.quan_kiem.client import kiem_tu_xa
from tram.tu_dong.cong_kiem import cong_mo
from tram.kiem.diff import tep_doi
from tram.kiem.duong_dan_cam import duong_dan_cham_cam


def chon_ban(kg, ds, nhanh):
    chon = None
    for s in merge_chua_deploy(ds):
        c = s.du_lieu.get("merge_commit")
        if not c or not la_to_tien(kg, c, f"origin/{nhanh}"):
            continue
        if chon is None or la_to_tien(kg, chon, c):
            chon = c
        elif not la_to_tien(kg, c, chon):
            return None
    return chon


def pham_vi_du(kg, ds, truoc, commit):
    if not la_to_tien(kg, truoc, commit):
        return False
    ds_sha = _git(kg, "rev-list", "--first-parent", f"{truoc}..{commit}").stdout.decode().splitlines()
    da = {s.du_lieu.get("merge_commit") for s in ds if s.loai == "pr.da_merge"}
    return bool(ds_sha) and set(ds_sha) <= da


def kiem_ban(db, kg, da, commit, pb):
    if not cong_mo():
        return False
    lenh = list(da.giao.lenh_kiem_mac_dinh)
    if not lenh:
        return False
    policy = json.dumps([da.ten, commit, pb, lenh, list(da.lenh_cho_phep)], sort_keys=True)
    ma = "dpkiem-" + hashlib.sha256(policy.encode()).hexdigest()[:24]
    try:
        r = kiem_tu_xa(kg, da, giao_id=ma, luot=1, commit=commit, lenh_kiem=lenh,
                       lenh_cho_phep=list(da.lenh_cho_phep), chay_lenh=True)
        dat = r.dat is True
    except (OSError, ValueError):
        dat = False
    ghi(db, da.ten, "deploy.kiem", {"ma_thao_tac": ma, "commit": commit, "phien_ban": pb,
                                    "dat": dat, "nguon_kiem": "uq"})
    return dat


def ban_an_toan(kg, da, truoc, commit):
    # M đã vào main: diff origin/main..M thường rỗng; phải kiểm từ bản thực đang chạy L.
    tep = tep_doi(kg, truoc, commit)
    schema = da.hang_rao.get("schema")
    return not duong_dan_cham_cam(tep, them=da.giao.duong_dan_cam) and not (
        schema and any(fnmatch.fnmatch(p, m) for p in tep for m in schema.duong_dan))
