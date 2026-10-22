"""Tick bước 4 (spec 4 §10): nhắc merge spec sau 24 giờ (một lần mỗi commit), feature xong (một lần)."""
from datetime import timedelta
from pathlib import Path

from bead_gia import bead
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, kho_tam
from su_kien_gia import ds, sk
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.tick_theo_plan import buoc_theo_plan

DA = DuAn("hr-codex", Path("/r"), None, {})
F = bead("hr-f", issue_type="feature", labels=["theo-plan"])


def test_nhac_merge_sau_24_gio_mot_lan_va_thoi_khi_da_merge(tmp_path):
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    c = k.day("tram/spec-hr-f", {"docs/specs/x.md": "# x\n"}, tu=k.main)
    fetch(k.kho)
    sk(kho, "spec.duyet", {"feature": "hr-f", "commit": c, "digest_bead": "sha256:x", "bead_moi": []}, bead_id="hr-f")
    assert buoc_theo_plan(kho, DA, [F], k.kho, LUC + timedelta(hours=23)) == {}
    assert buoc_theo_plan(kho, DA, [F], k.kho, LUC + timedelta(hours=25)) == {"spec_cho_merge": 1}
    assert buoc_theo_plan(kho, DA, [F], k.kho, LUC + timedelta(hours=30)) == {}
    assert buoc_theo_plan(kho, DA, [F], None, LUC + timedelta(hours=30)) == {}
    k.day("main", {}, tu=c)
    fetch(k.kho)
    (tmp_path / "x").mkdir()
    kho2 = kho_tam(tmp_path / "x")                                  # spec.duyet mới, đã merge
    sk(kho2, "spec.duyet", {"feature": "hr-f", "commit": c, "digest_bead": "sha256:x", "bead_moi": []}, bead_id="hr-f")
    assert buoc_theo_plan(kho2, DA, [F], k.kho, LUC + timedelta(hours=25)) == {}


def test_feature_xong_khi_moi_con_dong_mot_lan(tmp_path):
    kho = kho_tam(tmp_path)
    con = [bead("hr-f.1", status="closed", parent="hr-f"), bead("hr-f.2", parent="hr-f")]
    assert buoc_theo_plan(kho, DA, [F, *con], None, LUC) == {}
    con[1] = bead("hr-f.2", status="closed", parent="hr-f")
    assert buoc_theo_plan(kho, DA, [F, *con], None, LUC) == {"feature_xong": 1}
    assert buoc_theo_plan(kho, DA, [F, *con], None, LUC) == {}
    assert [s.du_lieu for s in ds(kho, "hr-f") if s.loai == "feature.xong"] == [{"feature": "hr-f"}]
    assert buoc_theo_plan(kho, DA, [bead("hr-g", issue_type="feature", labels=["theo-plan"])], None, LUC) == {}
