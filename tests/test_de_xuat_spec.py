"""Đề xuất phiếu `spec` (spec 4 §6.1, §7.2): nhánh, cha, không chạy mã, tiêu chí = nghiệm thu sơ bộ, lớp 4."""
from pathlib import Path

from bead_gia import bead
from kho_kiem_gia import dung_kho
from kho_phieu_gia import kho_tam
from su_kien_gia import DA as TEN, ds, nhan, sk
from test_phieu_yeu_cau import mo_ta
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.prompt import nap_vai
from tram.giao_viec.chon import UngVien
from tram.giao_viec.de_xuat_spec import dung_de_xuat_spec
from tram.giao_viec.git_kiem import fetch

DA = DuAn(TEN, Path("/r"), None, {})
F = bead("hr-f", title="Hoa hồng tạm tính", issue_type="feature", labels=["can-spec"], description=mo_ta())


def dx(tmp_path, x=F):
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    fetch(k.kho)
    return k, kho, lambda: dung_de_xuat_spec(UngVien(DA, x, "spec", False, frozenset()), ds(kho, x.id), k.kho)


def test_lan_dau(tmp_path):
    k, _, lam = dx(tmp_path)
    p = lam()
    assert (p.buoc, p.vai, p.repo.nhanh, p.repo.cha) == ("spec", "spec", "tram/spec-hr-f", k.main)
    assert (p.lenh_kiem, p.lenh_cho_phep, p.can_lenh_kiem, p.can_moi_truong_kiem) == ([], [], False, False)
    assert p.tieu_chi == ["Booking có giảm giá hiện đúng số tạm tính"]
    assert (p.ngan_sach.so_lan_chay, p.ngan_sach.phut, p.ngan_sach.token_ra) == (2, 45, 100_000)
    assert "## Lớp 2 — Vai spec (phiên bản 1)" in p.goi_ngu_canh and "phieu-yeu-cau" in p.goi_ngu_canh
    assert "# Quy ước dự án" in p.goi_ngu_canh and p.khoa_chong_trung.startswith("sha256:")


def test_sau_tra_ve_cha_la_sha_spec_moi_nhat_va_gop_y_o_lop_4(tmp_path):
    k, kho, lam = dx(tmp_path)
    p1 = lam()
    nhan(kho, "g-1", 1, buoc="spec", bead_id="hr-f")
    sk(kho, "giao.cong_bo", {"bead_id": "hr-f", "luot": 1, "commit": "c1c1c1c", "ref": "tram/spec-hr-f"},
       bead_id="hr-f")
    sk(kho, "giao.ket_thuc", {"giao_id": "g-1", "luot": 1, "buoc": "spec", "ket_thuc": "xong", "ly_do": "ke-hoach-loi",
                              "commit": "c1c1c1c", "loi": ["bead.0.nhan: nhãn cot:ai-lam"]}, bead_id="hr-f")
    p2 = lam()
    assert p2.repo.cha == "c1c1c1c" and p2.khoa_chong_trung != p1.khoa_chong_trung
    assert "bead.0.nhan: nhãn cot:ai-lam" in p2.goi_ngu_canh
    sk(kho, "spec.tra_ve", {"gop_y": "Tách màn hình và API thành hai bead"}, bead_id="hr-f")
    p3 = lam()
    assert "Tách màn hình và API" in p3.goi_ngu_canh and "bead.0.nhan" not in p3.goi_ngu_canh


def test_phieu_khong_hop_le_thi_khong_dung(tmp_path):
    _, _, lam = dx(tmp_path, bead("hr-f", issue_type="feature", labels=["can-spec"], description="không phiếu"))
    assert lam() is None


def test_vai_spec():
    pb, than = nap_vai("spec")
    assert pb == "1" and "docs/plans/<feature-id>.beads.json" in than and "Chỉ đổi file dưới `docs/`" in than
