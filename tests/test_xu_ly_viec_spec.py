"""Tick bước 0 cho phiếu `spec` (spec 4 §7.2, §10): kết luận vào `giao.ket_thuc`; chạm file cấm → escalation."""
import pytest

from bd_gia import BdGia
from bead_gia import bead
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, dat_phieu, kho_tam
from su_kien_gia import cong_bo, ds
from test_xet_spec import DA, TC, bg_spec, tep_spec
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.su_kien import moi_nhat
from tram.giao_viec.xu_ly_viec import xu_ly_cong_viec
from tram.phieu.cong_viec import cong_viec_cho
from xu_ly_gia import ket_thuc_bang


@pytest.fixture
def m(tmp_path):
    g = BdGia([bead("hr-f", title="Hoa hồng", issue_type="feature", labels=["can-spec"])])
    return dung_kho(tmp_path), kho_tam(tmp_path), g


def spec_xong(m, tep):
    k, kho, g = m
    sha = k.day("tram/spec-hr-f", tep, tu=k.main)
    fetch(k.kho)
    p = dat_phieu(kho, bead_id="hr-f", buoc="spec", tieu_chi=[TC], cha=k.main)
    cong_bo(kho, p.luot, sha, bead_id="hr-f")
    cv = ket_thuc_bang(kho, p, "xong", commit=sha, ban_giao=bg_spec(sha))
    assert xu_ly_cong_viec(kho, cv, du_an=DA, bd=g, kho_git=k.kho, luc=LUC) and cong_viec_cho(kho) == []
    return sha, moi_nhat(ds(kho, "hr-f"), "giao.ket_thuc").du_lieu


def test_spec_xong_hop_le(m):
    sha, kt = spec_xong(m, tep_spec())
    assert (kt["buoc"], kt["ket_thuc"], kt["ly_do"], kt["commit"], kt["loi"]) == ("spec", "xong", None, sha, [])


def test_spec_ngoai_docs_khong_hop_le_khong_escalation(m):
    _, kt = spec_xong(m, tep_spec(**{"src/a.py": "x\n"}))
    assert kt["ly_do"] == "spec-ngoai-docs" and m[2].so_lan("tao") == 0


def test_spec_cham_file_cam_tao_escalation(m):
    _, kt = spec_xong(m, tep_spec(**{"docs/CLAUDE.md": "x\n"}))
    esc = [b for b in m[2].beads.values() if b.issue_type == "decision"]
    assert kt["ly_do"] == "dong-file-cau-hinh" and len(esc) == 1 and "bead_goc: hr-f" in esc[0].description
