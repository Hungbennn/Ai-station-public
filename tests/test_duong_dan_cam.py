import pytest

from git_gia import git, ghi, tao_repo
from tram.kiem.diff import diff_cham_cam, goc_nhanh, tep_doi
from tram.kiem.duong_dan_cam import duong_dan_cham_cam, khop_mau


@pytest.mark.parametrize("p", [
    "erp/package.json", "package.json", "a/b/AGENTS.md", "AGENTS.md", "claude.md", "erp/Claude.MD",
    ".claude/settings.json", "x/.claude/agents/a.md", ".claude", ".mcp.json", "erp/.mcp.json",
    ".github/workflows/ci.yml", ".github/workflows/sub/x.yml", ".tram/goi.md", "a/.tram/x",
    "composer.json", "erp/composer.json", "phpunit.xml", "erp/phpunit.xml.dist", "vitest.config.ts",
    "web/jest.config.js", "a/.git/config", ".gitmodules"])
def test_cham_danh_sach_toi_thieu(p):
    assert duong_dan_cham_cam([p]) == [p]


@pytest.mark.parametrize("p", [
    "src/package.json.bak", "docs/AGENTS.md.txt", "erp/app/Foo.php", ".github/CODEOWNERS", "a/.gitmodules",
    "docs/handovers/x.md", "tests/claude_test.py", "x.tramx/a"])
def test_khong_cham(p):
    assert duong_dan_cham_cam([p]) == []


def test_glob_khong_vuot_thu_muc_va_hai_sao_khop_moi_cap():
    assert khop_mau("a/b/c.txt", "a/*.txt") is False
    assert khop_mau("a/c.txt", "a/*.txt") is True
    assert khop_mau("a/b/c/d.txt", "a/**/d.txt") is True and khop_mau("a/d.txt", "a/**/d.txt") is True


def test_du_an_them_va_ngoai_le_tung_duong_dan():
    ds = ["erp/package.json", "web/package.json", "config/app.php"]
    assert duong_dan_cham_cam(ds, them=["config/*.php"]) == ["config/app.php", "erp/package.json",
                                                             "web/package.json"]
    assert duong_dan_cham_cam(ds, cho_phep=["erp/package.json"]) == ["web/package.json"]
    assert duong_dan_cham_cam(ds, cho_phep=["**/package.json", "*"]) == ["erp/package.json", "web/package.json"]


def _repo_nhanh(tmp_path):
    r = tao_repo(tmp_path / "r")
    ghi(r, {"src/a.txt": "a", ".claude/x.md": "x", "README.md": "r"}, "goc")
    git(r, "branch", "chinh")
    git(r, "switch", "-q", "-c", "tram/b1")
    return r


def test_diff_lay_ca_ten_cu_va_moi_cua_rename(tmp_path):
    r = _repo_nhanh(tmp_path)
    git(r, "mv", "src/a.txt", "CLAUDE.md")
    (r / "docs").mkdir()
    git(r, "mv", ".claude/x.md", "docs/x.md")
    sha = ghi(r, {"erp/package.json": "{}", "src/b.txt": "b"}, "doi")
    goc = goc_nhanh(r, "chinh", sha)
    assert set(tep_doi(r, goc, sha)) == {"src/a.txt", "CLAUDE.md", ".claude/x.md", "docs/x.md",
                                         "erp/package.json", "src/b.txt"}
    assert diff_cham_cam(r, "chinh", sha) == [".claude/x.md", "CLAUDE.md", "erp/package.json"]


def test_diff_tinh_tu_goc_nhanh_khong_tu_cha(tmp_path):
    r = _repo_nhanh(tmp_path)
    ghi(r, {"AGENTS.md": "x"}, "lan 1")
    sha = ghi(r, {"src/c.txt": "c"}, "lan 2")      # lượt code lại: cha = đầu nhánh, diff từ cha sẽ rỗng
    assert diff_cham_cam(r, "chinh", sha) == ["AGENTS.md"]


def test_ten_file_co_khoang_trang_va_unicode(tmp_path):
    r = _repo_nhanh(tmp_path)
    sha = ghi(r, {"thư mục/package.json": "{}", "a b.txt": "x"}, "u")
    assert diff_cham_cam(r, "chinh", sha) == ["thư mục/package.json"]
