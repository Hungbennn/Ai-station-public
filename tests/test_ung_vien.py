"""Ứng viên (§5.1, §5.2, §6.6) và dựng đề xuất phiếu (§6.1, §6.3) cho phần 3."""
from pathlib import Path

import pytest

from bead_gia import bead
from kho_kiem_gia import dung_kho
from kho_phieu_gia import dat_phieu, kho_tam
from su_kien_gia import cong_bo, ds, ket_thuc, kiem, nhan, sk
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.du_an_giao import CauHinhGiao, NganSachBead, NganSachGiao
from tram.giao_viec.chon import UngVien
from tram.giao_viec.de_xuat import dung_de_xuat
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.giao_viec.ung_vien import liet_ke

TC = "- Tên kết thúc 'ỷ' không mất byte"
DG = digest_tieu_chi(["Tên kết thúc 'ỷ' không mất byte"])
DA = DuAn("hr-codex", Path("/r"), None, {}, lenh_cho_phep=("sh kiem.sh", "sh kiem.sh *"),
          moi_truong_kiem=MoiTruongKiem(Path("/env"), ".env.testing"),
          giao=CauHinhGiao(lenh_kiem_mac_dinh=("sh kiem.sh",)))


def b(id="hr-1", **kw):
    kw.setdefault("labels", ["cot:ai-lam"])
    kw.setdefault("acceptance_criteria", TC)
    kw.setdefault("issue_type", "bug")
    return bead(id, **kw)


def lk(kho, *beads, san=None, da=DA):
    return liet_ke(kho, da, list(beads), {x.id for x in beads} if san is None else san)


def test_lan_dau_la_code(tmp_path):
    kho = kho_tam(tmp_path)
    [u] = lk(kho, b(), b("hr-2", labels=["cot:can-chot"]))
    assert (u.bead.id, u.buoc, u.do, u.da_code) == ("hr-1", "code", False, frozenset())


def test_co_phieu_hieu_luc_khong_la_ung_vien(tmp_path):
    kho = kho_tam(tmp_path)
    dat_phieu(kho, bead_id="hr-1")
    assert lk(kho, b()) == []


def test_sau_kiem_lai_dat_la_qc_va_nho_khe_da_code(tmp_path):
    kho = kho_tam(tmp_path)
    nhan(kho, "g-1", 1, khe_id="B/c1")
    cong_bo(kho, 1, "c1c1c1c")
    ket_thuc(kho, "g-1", 1, commit="c1c1c1c")
    kiem(kho, "g-1", "c1c1c1c", digest=DG)
    [u] = lk(kho, b(status="in_progress", assignee="tram/giao-viec"), san=set())
    assert (u.buoc, u.da_code) == ("qc", frozenset({"B/c1"}))


def test_bead_do_va_het_ngan_sach(tmp_path):
    kho = kho_tam(tmp_path)
    nhan(kho, "g-1", 1)
    ket_thuc(kho, "g-1", 1, ket_thuc="thu_hoi", ly_do="mat-nhip")
    x = b(status="in_progress", assignee="tram/giao-viec")
    assert lk(kho, x, san=set())[0].do
    het = DuAn(**{**DA.__dict__, "giao": CauHinhGiao(ngan_sach=NganSachGiao(bead=NganSachBead(3, 5, 360)))})
    assert lk(kho, x, san=set(), da=het) == []                          # 3 giữ trước + 3 phiếu mới > 5


@pytest.fixture
def g(tmp_path):
    return dung_kho(tmp_path), kho_tam(tmp_path)


def dx(g, x, buoc="code"):
    k, kho = g
    fetch(k.kho)
    return dung_de_xuat(UngVien(DA, x, buoc, False, frozenset()), ds(kho, x.id), {x.id: x}, k.kho)


def test_de_xuat_code_lan_dau(g):
    p = dx(g, b(design="Chạy `sh kiem.sh TomTat` để kiểm"))
    assert p.repo.cha == g[0].main and p.repo.nhanh == "tram/hr-1" and p.vai == "coder"
    assert p.lenh_kiem == ["sh kiem.sh", "sh kiem.sh TomTat"] and p.can_lenh_kiem and p.can_moi_truong_kiem
    assert p.tieu_chi == ["Tên kết thúc 'ỷ' không mất byte"] and p.ngan_sach.so_lan_chay == 3
    assert "# Quy ước dự án" in p.goi_ngu_canh and "## Lớp 4" in p.goi_ngu_canh
    assert p.khoa_chong_trung.startswith("sha256:") and p.lenh_cho_phep == ["sh kiem.sh", "sh kiem.sh *"]


def test_giao_lai_tu_snapshot_va_khoa_doi_theo_cha(g):
    k, kho = g
    p1 = dx(g, b())
    sk(kho, "giao.snapshot", {"bead_id": "hr-1", "luot": 1, "commit": "abcdef1"})
    p2 = dx(g, b())
    assert p2.repo.cha == "abcdef1" and p2.khoa_chong_trung != p1.khoa_chong_trung


def test_de_xuat_qc_cha_la_commit_code(g):
    k, kho = g
    c = k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=k.main)
    kiem(kho, "g-1", c, digest=DG)
    p = dx(g, b(), "qc")
    assert (p.repo.cha, p.vai, p.lenh_kiem, p.can_lenh_kiem, p.ngan_sach.so_lan_chay) == (c, "qc", [], False, 2)
    assert c in p.goi_ngu_canh and "src/tom_tat.py" in p.goi_ngu_canh


def test_spike_tai_lieu(g):
    p = dx(g, b(issue_type="spike"))
    assert (p.lenh_kiem, p.lenh_cho_phep, p.can_lenh_kiem, p.can_moi_truong_kiem) == ([], [], False, False)


def test_de_xuat_qua_ngan_sach_goi_khong_cap(g):
    x = b(description="x" * 160_000)
    assert dx(g, x) is None


def test_code_khong_co_lenh_bat_buoc_thi_khong_dung(g):
    k, kho = g
    fetch(k.kho)
    da = DuAn("hr-codex", Path("/r"), None, {}, lenh_cho_phep=("sh kiem.sh",))
    assert dung_de_xuat(UngVien(da, b(), "code", False, frozenset()), [], {}, k.kho) is None
