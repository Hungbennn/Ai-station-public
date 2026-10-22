"""Kho kiểm + remote file tạm và gh giả cho Duyệt cột 3; không mạng."""
import json
from dataclasses import replace
from types import SimpleNamespace

from bd_gia import BdGia
from bead_gia import bead, notes_ban_giao
from git_gia import ghi, git, tao_repo
from tram.giao_viec.gh import GhCli
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.duyet_merge import NguonDuyet
from tram.thao_tac.kho import KhoThaoTac

V, URL = "2026-10-13T01:00:00Z", "https://github.com/o/r/pull/7"


def tao(tmp_path, *, da_vao=False, pr=None, nhanh_chinh="main", notes=None, **kw_bd):
    remote = tao_repo(tmp_path / "remote")
    dau = ghi(remote, {"x": "gốc"})
    git(remote, "branch", "-m", nhanh_chinh)
    kg = tmp_path / "kiem"
    git(tmp_path, "clone", "-q", str(remote), str(kg))
    git(remote, "checkout", "-qb", "tram/hr-2")
    commit = ghi(remote, {"x": "bản bàn giao"})
    if da_vao:
        git(remote, "update-ref", f"refs/heads/{nhanh_chinh}", commit)
    db = tmp_path / "sk.db"
    n = NguCanhGhi(BdGia([bead("hr-2", labels=["cot:cho-review"], notes=(
        notes_ban_giao(pr=pr) if notes is None else notes))], **kw_bd), KhoSuKien(db), KhoThaoTac(db), "hr")
    n.kho.ghi("hr", "bead.vao_cot_3", {"commit_ban_giao": commit}, bead_id="hr-2")
    t = SimpleNamespace(n=n, kg=kg, remote=remote, commit=commit, dau=dau, nhanh_chinh=nhanh_chinh,
                        pr={"number": 7, "url": URL, "state": "OPEN", "headRefName": "tram/hr-2",
                            "headRefOid": commit, "baseRefName": nhanh_chinh, "isCrossRepository": False,
                            "mergedAt": None, "mergeCommit": None}, goi=[], loi_gh=False)

    def chay(argv, dau_vao):
        t.goi.append(argv)
        return (1, "", "lỗi bí mật") if t.loi_gh else (0, json.dumps(t.pr), "")

    t.n = replace(n, nguon_duyet=lambda ten: NguonDuyet(kg, nhanh_chinh, GhCli(chay)))
    return t


def ghi_sk(t, ten, **d):
    t.n.kho.ghi("hr", ten, d, bead_id="hr-2")
