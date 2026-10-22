"""Skill "xem spec chờ duyệt" trên máy A (spec 4 §7.3): chỉ đọc, digest y hệt trạm, chạy được với python3 3.9."""
import ast
import subprocess
import sys
from pathlib import Path

from feature_gia import PLAN, SPEC, ke_hoach_json
from git_gia import MOI_TRUONG
from kho_kiem_gia import dung_kho
from tram.duong_dan import goc_repo
from tram.giao_viec.ke_hoach import digest_ke_hoach

THU_MUC = goc_repo() / "ky-nang" / "xem-spec-cho-duyet"
KICH_BAN = THU_MUC / "xem_spec.py"
DG = digest_ke_hoach(ke_hoach_json())


def chay(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(KICH_BAN), *args, "--repo", str(repo)], capture_output=True,
                          text=True, env=MOI_TRUONG)


def day(tmp_path, tep=None):
    k = dung_kho(tmp_path)
    c = k.day("tram/spec-hr-f", tep or {SPEC: "# Spec\n", PLAN: "# Plan\n",
                                       "docs/plans/hr-f.beads.json": ke_hoach_json()}, tu=k.main)
    return k, c


def trang_thai(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True,
                          env=MOI_TRUONG).stdout


def test_khop_digest_cua_tram_va_khong_ghi_gi(tmp_path):
    k, c = day(tmp_path)
    kq = chay(k.kho, "hr-codex", "hr-f", c, DG, "https://may-b/#/phe-duyet")
    assert kq.returncode == 0, kq.stdout
    assert "KHỚP dashboard" in kq.stdout and f"show {c}:{SPEC}" in kq.stdout and "[t2] task P1" in kq.stdout
    assert "https://may-b/#/phe-duyet" in kq.stdout and trang_thai(k.kho) == ""


def test_digest_khac_hoac_commit_khong_tren_nhanh(tmp_path):
    k, c = day(tmp_path)
    assert chay(k.kho, "hr-codex", "hr-f", c, "sha256:" + "0" * 64).returncode == 2
    kq = chay(k.kho, "hr-codex", "hr-f", k.main, DG)
    assert kq.returncode == 2 and "LỖI" in kq.stdout


def test_tham_so_la_va_thieu_file_plan(tmp_path):
    k, c = day(tmp_path, {SPEC: "# Spec\n", "docs/plans/hr-f.beads.json": ke_hoach_json()})
    assert chay(k.kho, "hr-codex", "hr-f;rm", c, DG).returncode == 2
    kq = chay(k.kho, "hr-codex", "hr-f", c, DG)
    assert kq.returncode == 2 and "THIẾU" in kq.stdout


def test_cu_phap_python_3_9_va_skill_chi_doc():
    ast.parse(KICH_BAN.read_text(encoding="utf-8"), feature_version=(3, 9))
    skill = (THU_MUC / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: xem-spec-cho-duyet\n") and "CHỈ ĐỌC" in skill and "Không** gọi" in skill
