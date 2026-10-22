import os

from kho_kiem_gia import dung_kho
from tram.giao_viec.git_kiem import (diff_theo_file, doc_file, fetch, kho_kiem, la_to_tien, sha_cua,
                                     tao_worktree, xoa_worktree)


def test_kho_kiem_nam_trong_tram_home(tram_home_tam):
    assert kho_kiem("hr-codex") == tram_home_tam / "kho-kiem" / "hr-codex"


def test_fetch_sha_to_tien(tmp_path):
    k = dung_kho(tmp_path)
    c1 = k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=k.main)
    assert sha_cua(k.kho, "origin/tram/hr-1") is None
    fetch(k.kho)
    assert sha_cua(k.kho, "origin/tram/hr-1") == c1 and sha_cua(k.kho, "origin/main") == k.main
    assert la_to_tien(k.kho, k.main, c1) and not la_to_tien(k.kho, c1, k.main)
    assert not la_to_tien(k.kho, "0" * 40, c1) and sha_cua(k.kho, "khong-co") is None


def test_doc_file_chi_file_thuong(tmp_path):
    k = dung_kho(tmp_path)
    os.symlink("AGENTS.md", k.dev / "lien_ket.md")
    c = k.day("tram/hr-1", {"docs/a.md": "nội dung dài " * 10}, tu=k.main)
    fetch(k.kho)
    assert doc_file(k.kho, "origin/main", "AGENTS.md") == "# Quy ước dự án\n"
    assert doc_file(k.kho, c, "docs/a.md", gioi_han=5) == "nội d"
    assert doc_file(k.kho, c, "lien_ket.md") is None                        # symlink
    assert doc_file(k.kho, c, "docs") is None and doc_file(k.kho, c, "khong.md") is None
    assert doc_file(k.kho, "khong-co-ref", "AGENTS.md") is None


def test_diff_theo_file(tmp_path):
    k = dung_kho(tmp_path)
    c = k.day("tram/hr-1", {"src/tom_tat.py": "x = 3\n", "docs/b.md": "b\n"}, tu=k.main)
    fetch(k.kho)
    ds = diff_theo_file(k.kho, k.main, c)
    assert [p for p, _ in ds] == ["docs/b.md", "src/tom_tat.py"] and "+x = 3" in ds[1][1]


def test_worktree_kiem_tach_roi_va_xoa_lai(tmp_path):
    k = dung_kho(tmp_path)
    c = k.day("tram/hr-1", {"src/tom_tat.py": "x = 4\n"}, tu=k.main)
    fetch(k.kho)
    wt = tao_worktree(k.kho, tmp_path / "kiem" / "g-1", c)
    (wt / "rac.txt").write_text("cũ")
    wt = tao_worktree(k.kho, tmp_path / "kiem" / "g-1", c)                  # tạo lại: sạch
    assert (wt / "src/tom_tat.py").read_text() == "x = 4\n" and not (wt / "rac.txt").exists()
    xoa_worktree(k.kho, wt)
    assert not wt.exists()
