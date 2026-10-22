"""Codex Q3 — bead bs-2bd.1.28 (spec 4 §5.1 điều kiện 8; spec `tu-merge` Scenario "Con của feature đã duyệt"): con của
feature `theo-plan` mà commit spec đã duyệt NẰM TRONG nhánh chính đi hết đường thật — kiểm lại + QC đạt → vòng tick
đưa vào cột 3 (`vao_cot_3_an_toan` đọc lại Beads rồi xét lại điều kiện, CÓ tập feature đã merge spec) → mở PR → tự
merge → xác minh → đóng. Spec chưa vào nhánh chính → con vẫn chờ (`cho-merge-spec`), không vào cột 3."""
from bead_gia import bead
from gh_gia import REPO
from su_kien_gia import sk
from test_tu_merge import dung_tu_merge, merge_goi, tm
from tram.giao_viec.tick import mot_vong_tick

F = bead("hr-f", issue_type="feature", title="Hoa hồng tạm tính", labels=["theo-plan"])


def _duyet(t, commit):
    sk(t.kho, "spec.duyet", {"feature": "hr-f", "commit": commit, "digest_bead": "sha256:b", "bead_moi": [],
                             "ma_thao_tac": "dy-1"}, bead_id="hr-f")


def test_con_feature_spec_da_merge_vao_cot_3_roi_tu_merge(tmp_path, monkeypatch):
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, them=(F,), parent="hr-f")
    _duyet(t, t.k.main)                                          # commit spec đã duyệt là tổ tiên origin/main
    r = mot_vong_tick(t.bo)
    assert (r.get("cot_3"), r.get("pr_mo")) == (1, 1)
    gh.dat(1, ci="xanh")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and merge_goi(gh) == [("merge_pr", REPO, 1, q)]
    assert len(tm(t, "tu_merge.xong")) == 1
    assert mot_vong_tick(t.bo)["da_merge"] == 1 and t.g.beads["hr-1"].status == "closed"


def test_con_feature_spec_chua_merge_thi_chua_vao_cot_3(tmp_path, monkeypatch):
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, them=(F,), parent="hr-f")
    _duyet(t, t.k.day("tram/spec-hr-f", {"docs/specs/x.md": "spec\n"}, tu=t.k.main))
    r = mot_vong_tick(t.bo)
    assert "cot_3" not in r and "pr_mo" not in r and gh.goi == [] and tm(t) == []
