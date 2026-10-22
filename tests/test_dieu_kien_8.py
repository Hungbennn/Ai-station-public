"""Điều kiện 8 thật (spec 4 §5.1, §7.3): con của feature `theo-plan` chờ commit spec đã duyệt vào nhánh chính."""
from pathlib import Path

from bead_gia import bead
from kho_kiem_gia import dung_kho
from kho_phieu_gia import kho_tam
from su_kien_gia import sk
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.giao_viec.dieu_kien import ly_do_khong_giao
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.ung_vien import liet_ke

DA = DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(Path("/env"), ".env.testing"))
FEAT = bead("hr-f", issue_type="feature", labels=["theo-plan"])
CON = bead("hr-f.1", issue_type="task", labels=["cot:ai-lam"], parent="hr-f", acceptance_criteria="- Đạt")


def test_cha_theo_plan_da_merge_thi_giao():
    theo_id = {"hr-f": FEAT, "hr-f.1": CON}
    assert ly_do_khong_giao(CON, theo_id, {"hr-f.1"}, DA) == "cho-merge-spec"
    assert ly_do_khong_giao(CON, theo_id, {"hr-f.1"}, DA, frozenset({"hr-f"})) is None
    assert ly_do_khong_giao(CON, {"hr-f.1": CON}, {"hr-f.1"}, DA, frozenset({"hr-f"})) == "cho-merge-spec"


def test_feature_da_merge_theo_git_kho_kiem(tmp_path):
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    c = k.day("tram/spec-hr-f", {"docs/specs/x.md": "# Spec\n"}, tu=k.main)
    sk(kho, "spec.duyet", {"feature": "hr-f", "commit": c, "digest_bead": "sha256:x", "bead_moi": ["hr-f.1"]},
       bead_id="hr-f")
    fetch(k.kho)
    beads = [FEAT, CON]
    assert feature_da_merge(kho, DA, beads, k.kho) == frozenset() and feature_da_merge(kho, DA, beads, None) == set()
    assert liet_ke(kho, DA, beads, {"hr-f.1"}) == []
    k.day("main", {}, tu=c)                                         # Đại ca merge PR spec (fast-forward)
    fetch(k.kho)
    merge = feature_da_merge(kho, DA, beads, k.kho)
    assert merge == {"hr-f"}
    assert [u.bead.id for u in liet_ke(kho, DA, beads, {"hr-f.1"}, merge)] == ["hr-f.1"]


def test_feature_chua_duyet_hoac_khong_theo_plan_khong_tinh(tmp_path):
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    fetch(k.kho)
    assert feature_da_merge(kho, DA, [FEAT, bead("hr-g", issue_type="feature", labels=["can-spec"])], k.kho) == set()
