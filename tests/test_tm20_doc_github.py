"""Lỗi đọc bền qua tick; không lặp merge, thành công xoá chuỗi lỗi đọc."""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from gh_gia import REPO
from su_kien_gia import ds
from test_tu_merge import cot_3_co_pr, dung_tu_merge
from tram.giao_viec.gh import LoiGh
from tram.giao_viec.tu_merge_gui import gui_merge


@pytest.mark.parametrize("hong", ["xem_pr", "cong_merge"])
def test_ba_vong_doc_hong_dung_thu(tmp_path, monkeypatch, hong):
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    calls = []
    def loi(*args):
        calls.append(1)
        raise LoiGh("github-doc-loi")
    monkeypatch.setattr(gh, hong, loi)
    for _ in range(4):
        gui_merge(gh, REPO, t.kho, "hr-codex", "hr-1", ds(t.kho), so_pr=1, commit=q,
                  loai="code", ly_do=lambda pr: [], luc=datetime.now(timezone.utc))
    assert len(calls) == 3
    assert sum(s.loai == "tu_merge.loi" for s in ds(t.kho)) == 1
    assert not any(s.loai == "tu_merge.bat_dau" for s in ds(t.kho))


def test_doc_tot_xoa_chuoi_loi(tmp_path, monkeypatch):
    from tram.giao_viec.doc_merge import ghi_doc
    t, _, _ = dung_tu_merge(tmp_path, monkeypatch)
    luc = datetime.now(timezone.utc)
    def ghi(loi):
        return ghi_doc(t.kho, "hr-codex", "hr-1", ds(t.kho), "tm-doc", loi, luc)
    assert [ghi(True), ghi(True), ghi(False), ghi(True)] == [1, 2, 0, 1]


def test_crash_before_deploy_result_blocks_merge(tmp_path, monkeypatch):
    from tram.deploy.ghi import ghi
    from test_tu_merge import merge_goi
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    ghi(t.kho.db, 'hr-codex', 'deploy.bat_dau', {'ma_thao_tac': 'dp-pending'})
    gui_merge(gh, REPO, t.kho, 'hr-codex', 'hr-1', ds(t.kho), so_pr=1, commit=q,
              loai='code', ly_do=lambda pr: [], luc=datetime.now(timezone.utc))
    assert not merge_goi(gh)
