"""Luật `chinh-thuc` bản chặt 13/10 (spec 0+1a §4.3, §11) — hàm chung phần 3 §7.5 và phần 4 §6.1."""
import os

import pytest

from git_gia import git, ghi, tao_repo
from tram.ban_giao.schema import BanGiao, kiem_ban_giao

FILE = "docs/handovers/bg.md"


def mau(**ghi_de) -> BanGiao:
    d = {"phien_ban": 1, "loai": "chinh-thuc", "luot": 2, "file_ban_giao": FILE, "nhanh": "tram/hr-1",
         "commit": None, "doi_chieu_nghiem_thu": [{"tieu_chi": "A", "dat": True, "bang_chung": "t::a"},
                                                 {"tieu_chi": "B", "dat": True, "bang_chung": "t::b"}],
         "lenh_kiem": [{"lenh": "php artisan test", "ket_qua": "pass", "tom_tat": "9 passed", "digest_log": "s"},
                       {"lenh": "npm run lint", "ket_qua": "pass", "tom_tat": "ok", "digest_log": "s"}],
         "quyet_dinh": [], "huong_da_bo": [], "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [],
         "thay_doi_vung_nhay_cam": []}
    d.update(ghi_de)
    return BanGiao.model_validate(d)


def dia(tmp_path):
    (tmp_path / "docs/handovers").mkdir(parents=True)
    (tmp_path / FILE).write_text("x")
    return tmp_path


def kiem(bg, goc, *, tieu_chi=("A", "B"), lenh=("php artisan test",), can=True, **kw):
    return kiem_ban_giao(bg, list(tieu_chi), goc, lenh_bat_buoc=list(lenh), can_lenh_kiem=can, **kw)


def test_hop_le(tmp_path):
    assert kiem(mau(), dia(tmp_path)) == []


def test_mot_tieu_chi_false_va_lint_pass_khong_dat(tmp_path):
    bg = mau(doi_chieu_nghiem_thu=[{"tieu_chi": "A", "dat": True, "bang_chung": "x"},
                                   {"tieu_chi": "B", "dat": False, "bang_chung": "x"}])
    assert kiem(bg, dia(tmp_path)) == ["Tiêu chí 'B' chưa đạt"]


def test_suite_bat_buoc_fail_va_test_nho_pass_khong_dat(tmp_path):
    bg = mau(lenh_kiem=[{"lenh": "php artisan test", "ket_qua": "fail", "tom_tat": "", "digest_log": ""},
                        {"lenh": "php artisan test --filter Nho", "ket_qua": "pass", "tom_tat": "", "digest_log": ""}])
    assert kiem(bg, dia(tmp_path)) == ["Lệnh bắt buộc không pass: php artisan test"]


def test_lenh_bat_buoc_lap_lai_mot_lan_fail_la_khong_dat(tmp_path):
    lk = [{"lenh": "php artisan test", "ket_qua": k, "tom_tat": "", "digest_log": ""} for k in ("pass", "fail")]
    assert kiem(mau(lenh_kiem=lk), dia(tmp_path)) == ["Lệnh bắt buộc không pass: php artisan test"]


def test_thieu_lenh_bat_buoc_va_lenh_bo_sung_khong_thay_duoc(tmp_path):
    assert kiem(mau(), dia(tmp_path), lenh=("php artisan test", "composer test")) == [
        "Thiếu lệnh bắt buộc: composer test"]


def test_can_lenh_kiem_ma_khong_co_lenh_bat_buoc_la_loi(tmp_path):
    assert kiem(mau(), dia(tmp_path), lenh=()) == ["Phiếu cần lệnh kiểm nhưng không có lệnh bắt buộc nào"]


def test_khong_can_lenh_kiem_chi_mien_lenh_khong_mien_tieu_chi(tmp_path):
    goc = dia(tmp_path)
    assert kiem(mau(lenh_kiem=[]), goc, lenh=(), can=False) == []
    assert kiem(mau(lenh_kiem=[]), goc, lenh=(), can=False, tieu_chi=("A", "C")) == [
        "Thiếu đối chiếu tiêu chí: C"]


def test_tieu_chi_trung_va_thieu_bang_chung(tmp_path):
    bg = mau(doi_chieu_nghiem_thu=[{"tieu_chi": "A", "dat": True, "bang_chung": "x"},
                                   {"tieu_chi": "A", "dat": True, "bang_chung": "y"},
                                   {"tieu_chi": "B", "dat": True, "bang_chung": "  "}])
    assert kiem(bg, dia(tmp_path)) == ["Trùng đối chiếu tiêu chí: A", "Tiêu chí 'B' không có bằng chứng"]


def test_ban_qc_dat_false_chi_khi_tra_ve(tmp_path):
    bg = mau(doi_chieu_nghiem_thu=[{"tieu_chi": "A", "dat": False, "bang_chung": "lỗi ở x"},
                                   {"tieu_chi": "B", "dat": True, "bang_chung": "y"}])
    goc = dia(tmp_path)
    assert kiem(bg, goc, can=False, la_qc=True, ket_luan_qc="tra_ve") == []
    assert kiem(bg, goc, can=False, la_qc=True, ket_luan_qc="dat") == [
        "Tiêu chí 'A' chưa đạt mà khối QC không kết luận tra_ve"]
    assert kiem(bg, goc, can=False, la_qc=True) != []


@pytest.mark.parametrize("p", ["/abs/docs/handovers/x.md", "docs/handovers/../x.md", "docs/x.md",
                               "docs/handovers/", "docs//handovers/x.md", "./docs/handovers/x.md",
                               "docs\\handovers\\x.md", ""])
def test_duong_dan_file_ban_giao_sai(tmp_path, p):
    loi = kiem(mau(file_ban_giao=p), dia(tmp_path))
    assert len(loi) == 1 and "file_ban_giao" in loi[0]


def test_symlink_tren_dia_bi_tu_choi(tmp_path):
    goc = dia(tmp_path)
    (tmp_path / "ngoai.md").write_text("x")
    os.symlink(tmp_path / "ngoai.md", goc / "docs/handovers/link.md")
    assert "symlink" in kiem(mau(file_ban_giao="docs/handovers/link.md"), goc)[0]


def test_tai_commit_file_thuong_symlink_submodule(tmp_path):
    r = tao_repo(tmp_path / "r")
    ghi(r, {FILE: "x", "docs/that.md": "y"})
    os.symlink("../that.md", r / "docs/handovers/link.md")
    git(r, "add", "docs/handovers/link.md")
    git(r, "update-index", "--add", "--cacheinfo", f"160000,{git(r, 'rev-parse', 'HEAD')},docs/handovers/sub")
    git(r, "commit", "-q", "-m", "link + submodule")
    sha = git(r, "rev-parse", "HEAD")
    assert kiem(mau(), r, commit=sha) == []
    assert "không phải file thường" in kiem(mau(file_ban_giao="docs/handovers/link.md"), r, commit=sha)[0]
    assert "không phải file thường" in kiem(mau(file_ban_giao="docs/handovers/sub"), r, commit=sha)[0]
    assert "Không thấy" in kiem(mau(file_ban_giao="docs/handovers/khong.md"), r, commit=sha)[0]


def test_ban_giao_tam_khong_can_lenh_hay_file(tmp_path):
    assert kiem(mau(loai="tam", file_ban_giao="", buoc_tiep=["làm tiếp"]), tmp_path, lenh=()) == []


def test_tieu_chi_chep_kem_gach_dau_dong_van_khop(tmp_path):
    # Gói ngữ cảnh in tiêu chí dạng "- X"; thợ chép nguyên văn cả gạch đầu dòng (bs-ie0, 21/10).
    bg = mau(doi_chieu_nghiem_thu=[{"tieu_chi": "- A", "dat": True, "bang_chung": "x"},
                                   {"tieu_chi": "B", "dat": True, "bang_chung": "y"}])
    assert kiem(bg, dia(tmp_path)) == []
