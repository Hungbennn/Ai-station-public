"""Vào cột 3 (spec 4 §6.4, §6.7) — G10: bằng chứng gắn đúng commit ở ref công bố; thay toàn bộ nhãn cột."""
from pathlib import Path

import pytest

from bd_gia import BdGia
from bead_gia import KHOI_BAN_GIAO, bead
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, kho_tam
from su_kien_gia import nhan, ket_thuc, DA as TEN, cong_bo, ds, kiem, qc, sk
from tram.ban_giao.doc import tom_tat_ban_giao
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.giao_viec.bang_chung import vao_cot_3
from tram.giao_viec.tieu_chi import digest_tieu_chi, tach_tieu_chi
from tram.giao_viec.git_kiem import fetch
from tram.su_kien.kho import KhoSuKien

DA = DuAn(TEN, Path("/r"), None, {"tien": HangRao(duong_dan=("*Modules/Fin/*",))})


@pytest.fixture
def m(tmp_path):
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    g = BdGia([bead("hr-1", status="in_progress", labels=["cot:ai-lam", "cot:can-chot"])])
    return k, kho, g


def chuan_bi(m, tep_code, *, qc_dat=True):
    k, kho, _ = m
    c = k.day("tram/hr-1", tep_code, tu=k.main)
    q = k.day("tram/hr-1", {"docs/handovers/qc.md": "qc"}, tu=c)
    fetch(k.kho)
    sk(kho, "bao.xong", {"giao_id": "g-1", "commit": c, "ban_giao": {**KHOI_BAN_GIAO, "commit": c, "pr": None}})
    nhan(kho, "g-1", 1)
    ket_thuc(kho, "g-1", 1, commit=c)
    kiem(kho, "g-1", c, digest=digest_tieu_chi(tach_tieu_chi(m[2].beads["hr-1"].acceptance_criteria)))
    cong_bo(kho, 2, q)
    qc(kho, "g-2", c, q, ket_luan="dat" if qc_dat else "tra_ve")
    return c, q


def chay(m, la_spike=False):
    k, kho, g = m
    return vao_cot_3(g, kho, k.kho, DA, g.beads["hr-1"], ds(kho), la_spike=la_spike, luc=LUC)


def test_vao_cot_3_thay_nhan_cot_va_ghi_bang_chung(m, tmp_path):
    c, q = chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    assert chay(m)
    b = m[2].beads["hr-1"]
    assert b.labels == ("cot:cho-review",) and f'"commit_ban_giao": "{q}"' in b.notes
    assert tom_tat_ban_giao(b.notes)["commit"] == c                     # dashboard 2a đọc được khối bàn giao
    e = KhoSuKien(tmp_path / "su-kien.db").gan_day(TEN, "bead.vao_cot_3", 5)
    assert len(e) == 1 and e[0].du_lieu["commit_code"] == c and e[0].du_lieu["co_do"] is False
    so = len(m[2].goi)
    assert chay(m) and len(m[2].goi) == so                               # phát lại: không ghi lại
    assert len(KhoSuKien(tmp_path / "su-kien.db").gan_day(TEN, "bead.vao_cot_3", 5)) == 1


def test_co_do_theo_duong_dan_hang_rao(m):
    chuan_bi(m, {"erp/app/Modules/Fin/Tien.php": "<?php"})
    assert chay(m) and "co-do" in m[2].beads["hr-1"].labels


def test_ref_cong_bo_doi_sau_qc_khong_vao(m):
    chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    cong_bo(m[1], 3, "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
    assert not chay(m) and m[2].goi == []


def test_qc_tra_ve_khong_vao(m):
    chuan_bi(m, {"src/tom_tat.py": "x = 2\n"}, qc_dat=False)
    assert not chay(m)


def test_commit_qc_khong_noi_tu_commit_code_khong_vao(m):
    k, kho, g = m
    c, _ = chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    la = k.day("khac", {"z": "z"}, tu=k.main)
    fetch(k.kho)
    cong_bo(kho, 3, la)
    qc(kho, "g-3", c, la)
    assert not chay(m)


def test_spike_vao_bang_commit_cua_spike(m):
    k, kho, g = m
    s = k.day("tram/hr-1", {"docs/spikes/x.md": "kết luận"}, tu=k.main)
    fetch(k.kho)
    cong_bo(kho, 1, s)
    nhan(kho, "g-1", 1)
    ket_thuc(kho, "g-1", 1, commit=s)
    kiem(kho, "g-1", s, digest=digest_tieu_chi(tach_tieu_chi(g.beads["hr-1"].acceptance_criteria)))
    assert chay(m, la_spike=True) and g.beads["hr-1"].labels == ("cot:cho-review",)


def test_tieu_chi_doi_truoc_ghi_cot_3_khong_vao(m):
    from dataclasses import replace
    chuan_bi(m, {"src/tom_tat.py": "x = 2\n"})
    m[2].beads["hr-1"] = replace(m[2].beads["hr-1"], acceptance_criteria="Tiêu chí mới")
    assert not chay(m) and not m[2].goi

