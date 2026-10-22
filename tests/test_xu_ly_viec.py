"""Tick bước 0 (spec 4 §10, §9): công việc chờ → kết luận, escalation theo `ly_do`, `qc.ket_qua`, `giao.ket_thuc`."""
from pathlib import Path

import pytest

from bd_gia import BdGia
from bead_gia import bead
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, dat_phieu, kho_tam
from su_kien_gia import DA as TEN, cong_bo, ds, sk
from test_xet_xong import F, bg, khoi_qc
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.xu_ly_viec import escalation_cau_hoi, xu_ly_cong_viec
from tram.phieu.cong_viec import cong_viec_cho
from xu_ly_gia import ket_thuc_bang

DA = DuAn(TEN, Path("/r"), None, {})


@pytest.fixture
def m(tmp_path):
    return dung_kho(tmp_path), kho_tam(tmp_path), BdGia([bead("hr-1", title="Sửa", status="in_progress")])


def xu_ly(m, cv, kho_git="mac-dinh"):
    k, kho, g = m
    return xu_ly_cong_viec(kho, cv, du_an=DA, bd=g, kho_git=k.kho if kho_git == "mac-dinh" else kho_git, luc=LUC)


def kt(m):
    return moi_nhat(ds(m[1]), "giao.ket_thuc").du_lieu


def code_xong(m, tep):
    k, kho, _ = m
    sha = k.day("tram/hr-1", tep, tu=k.main)
    fetch(k.kho)
    p = dat_phieu(kho, bead_id="hr-1")
    cong_bo(kho, p.luot, sha)
    return sha, ket_thuc_bang(kho, p, "xong", commit=sha, ban_giao=bg(sha))


def test_code_xong_hop_le(m):
    sha, cv = code_xong(m, {"src/tom_tat.py": "x = 2\n", F: "x"})
    assert xu_ly(m, cv) and cong_viec_cho(m[1]) == []
    assert kt(m) == {"giao_id": cv.giao_id, "luot": 1, "buoc": "code", "ket_thuc": "xong", "ly_do": None,
                     "commit": sha, "loi": []}
    assert xu_ly(m, cv) and len([s for s in ds(m[1]) if s.loai == "giao.ket_thuc"]) == 1     # phát lại


def test_code_cham_cam_tao_escalation(m):
    _, cv = code_xong(m, {"erp/package.json": "{}", F: "x"})
    xu_ly(m, cv)
    assert kt(m)["ly_do"] == "dong-file-cau-hinh" and m[2].so_lan("tao") == 1
    assert "ly_do: dong-file-cau-hinh" in next(b for b in m[2].beads.values() if b.issue_type == "decision").description


def test_chua_co_kho_kiem_thi_de_nguyen(m):
    _, cv = code_xong(m, {F: "x"})
    assert not xu_ly(m, cv, kho_git=None) and len(cong_viec_cho(m[1])) == 1


@pytest.mark.parametrize("ly_do, esc", [("agent", "agent-bi"), ("thieu-moi-truong-kiem", "thieu-moi-truong-kiem"),
                                        ("khe-tat", None), ("estop", None), ("cau-dao", None),
                                        ("het-ngan-sach", None), ("can-hoi", None)])
def test_bao_bi_theo_ly_do(m, ly_do, esc):
    p = dat_phieu(m[1], bead_id="hr-1")
    xu_ly(m, ket_thuc_bang(m[1], p, "bi", ly_do=ly_do, noi_dung="vướng"))
    assert kt(m)["ly_do"] == ly_do and m[2].so_lan("tao") == (1 if esc else 0)


@pytest.mark.parametrize("ket", ["het_han_muc", "thu_hoi"])
def test_het_han_muc_va_thu_hoi_giao_lai_khong_escalation(m, ket):
    p = dat_phieu(m[1], bead_id="hr-1")
    assert xu_ly(m, ket_thuc_bang(m[1], p, ket)) and kt(m)["ket_thuc"] == ket and m[2].so_lan("tao") == 0


def qc_xong(m, tep_qc):
    k, kho, _ = m
    c = k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=k.main)
    q = k.day("tram/hr-1", tep_qc(c), tu=c)
    fetch(k.kho)
    p = dat_phieu(kho, bead_id="hr-1", buoc="qc", cha=c)
    cong_bo(kho, p.luot, q)
    return c, q, ket_thuc_bang(kho, p, "xong", commit=q, ban_giao=bg(q, lenh_kiem=[]))


def test_qc_dat_ghi_qc_ket_qua(m):
    c, q, cv = qc_xong(m, lambda c: {F: khoi_qc(c)})
    xu_ly(m, cv)
    r = moi_nhat(ds(m[1]), "qc.ket_qua").du_lieu
    assert (r["ket_luan"], r["commit_code"], r["commit_qc"]) == ("dat", c, q) and kt(m)["ly_do"] is None


def test_qc_doi_ma_khong_cong_nhan_va_escalation(m):
    c, q, cv = qc_xong(m, lambda c: {F: khoi_qc(c), "src/tom_tat.py": "x = 9\n"})
    xu_ly(m, cv)
    assert moi_nhat(ds(m[1]), "qc.ket_qua").du_lieu["ket_luan"] == "khong_cong_nhan" and m[2].so_lan("tao") == 1


def test_cau_hoi_cua_agent_thanh_escalation_mot_lan(m):
    k, kho, g = m
    sk(kho, "bao.can_hoi", {"giao_id": "g-1", "loai_hoi": "thao_tac_nguy_hiem", "noi_dung": "Xoá cột cũ?"})
    sk(kho, "bao.can_hoi", {"giao_id": "g-1", "loai_hoi": "can_quyet_dinh", "noi_dung": "Làm tròn lên?"})
    assert escalation_cau_hoi(kho, DA, g, LUC) == 2 and escalation_cau_hoi(kho, DA, g, LUC) == 0
    mo_ta = sorted(b.description for b in g.beads.values() if b.issue_type == "decision")
    assert "ly_do: can-thao-tac-nguy-hiem" in mo_ta[0] + mo_ta[1] and "ly_do: agent-can-hoi" in mo_ta[0] + mo_ta[1]
