"""Cờ đỏ theo gitnexus `detect_changes` khi vào cột 3 (spec 4 §6.4 mục 3, lát 4c) — gitnexus giả, Git cục bộ."""
from dataclasses import replace

from bead_gia import KHOI_BAN_GIAO
from gitnexus_gia import GnGia
from kho_phieu_gia import LUC
from su_kien_gia import ds, sk
from test_bang_chung import DA, chuan_bi, m  # noqa: F401 — fixture `m`
from tram.ban_giao.doc import tom_tat_ban_giao
from tram.giao_viec.bang_chung import vao_cot_3
from tram.giao_viec.co_do_gn import co_do_gitnexus
from tram.kiem.diff import goc_nhanh

DA_GN = replace(DA, gitnexus_repo="hr-interview-copilot")


def chay(m, gn, da=DA_GN):
    k, kho, g = m
    return vao_cot_3(g, kho, k.kho, da, g.beads["hr-1"], ds(kho), la_spike=False, luc=LUC, gitnexus=gn)


def vao(m):
    return [s for s in ds(m[1]) if s.loai == "bead.vao_cot_3"][-1].du_lieu


def test_luong_cham_hang_rao_thi_co_do(m, tmp_path):
    c, q = chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})            # đường dẫn không chạm hàng rào
    gn = GnGia({"src/tom_tat.py", "erp/app/Modules/Fin/So.php"})   # nhưng luồng bị ảnh hưởng đi qua Fin
    assert chay(m, gn) and "co-do" in m[2].beads["hr-1"].labels
    assert vao(m)["co_do"] is True and vao(m)["co_do_ly_do"] == ["gitnexus"]
    [(wt, base, repo, head)] = gn.goi
    assert head == q and base == goc_nhanh(m[0].kho, "origin/main", q) and repo == "hr-interview-copilot"
    assert not wt.exists()                                           # worktree tạm đã dọn


def test_khong_cham_thi_khong_co(m):
    chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    assert chay(m, GnGia({"src/tom_tat.py"})) and "co-do" not in m[2].beads["hr-1"].labels
    assert vao(m)["co_do_ly_do"] == []


def test_duong_dan_va_gitnexus_cung_ghi(m):
    chuan_bi(m, {"erp/app/Modules/Fin/Tien.php": "<?php"})
    assert chay(m, GnGia({"erp/app/Modules/Fin/Tien.php"})) and vao(m)["co_do_ly_do"] == ["duong-dan", "gitnexus"]


def test_khong_chac_hoac_loi_van_gan_co_do(m, tmp_path):
    chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    assert chay(m, GnGia(khong_chac=True)) and vao(m)["co_do_ly_do"] == ["gitnexus-loi"]
    k, kho, g = m
    assert co_do_gitnexus(GnGia(loi=True), k.kho, DA_GN, vao(m)["commit_ban_giao"]) == ("gitnexus-loi",)


def test_chua_cau_hinh_thi_khong_goi(m):
    chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    gn = GnGia({"erp/app/Modules/Fin/So.php"})
    assert chay(m, gn, da=DA) and gn.goi == [] and vao(m)["co_do"] is False
    assert co_do_gitnexus(None, m[0].kho, DA_GN, "a" * 40) == ()


def test_pr_cua_agent_khong_vao_khoi_ban_giao_cot_3(m):
    chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    bx = [s for s in ds(m[1]) if s.loai == "bao.xong"][-1].du_lieu
    sk(m[1], "bao.xong", {**bx, "ban_giao": {**bx["ban_giao"], "pr": KHOI_BAN_GIAO["pr"]}})   # agent tự ghi link
    assert chay(m, None) and tom_tat_ban_giao(m[2].beads["hr-1"].notes)["pr"] is None
