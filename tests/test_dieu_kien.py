"""§5.1 — G3: không bead nào thiếu điều kiện được giao."""
from pathlib import Path

import pytest

from bead_gia import bead
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.giao_viec.dieu_kien import ly_do_khong_giao

DA = DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(Path("/env"), "erp/.env.testing"))
TC = "- Tên kết thúc 'ỷ' không mất byte"


def b(id="hr-1", **kw):
    kw.setdefault("labels", ["cot:ai-lam"])
    kw.setdefault("acceptance_criteria", TC)
    kw.setdefault("issue_type", "bug")
    return bead(id, **kw)


def xet(x, *khac, san_sang=None, du_an=DA):
    theo_id = {y.id: y for y in (x, *khac)}
    return ly_do_khong_giao(x, theo_id, {x.id} if san_sang is None else san_sang, du_an)


@pytest.mark.parametrize("loai", ["bug", "task", "chore", "spike"])
def test_lan_dau_du_dieu_kien(loai):
    assert xet(b(issue_type=loai)) is None


def test_buoc_sau_in_progress_van_giao():
    assert xet(b(status="in_progress", assignee="tram/giao-viec"), san_sang=set()) is None


@pytest.mark.parametrize("kw, ly_do", [
    ({"labels": ["cot:ai-lam", "cot:can-chot"]}, "nhan-lech"),
    ({"labels": ["cot:can-chot"]}, "khong-o-cot-1"), ({"labels": []}, "khong-o-cot-1"),
    ({"labels": ["cot:ai-lam", "can-spec"]}, "nhan-luong"), ({"labels": ["cot:ai-lam", "theo-plan"]}, "nhan-luong"),
    ({"issue_type": "feature"}, "loai-khong-giao"), ({"issue_type": "decision"}, "loai-khong-giao"),
    ({"issue_type": "epic"}, "loai-khong-giao"),
    ({"acceptance_criteria": ""}, "thieu-tieu-chi"), ({"acceptance_criteria": " - \n"}, "thieu-tieu-chi"),
    ({"status": "blocked"}, "trang-thai"), ({"status": "closed"}, "trang-thai"),
    ({"status": "in_progress", "assignee": "hung"}, "nguoi-khac-nhan"),
])
def test_khong_du_dieu_kien(kw, ly_do):
    assert xet(b(**kw)) == ly_do


def test_lan_dau_phai_nam_trong_bd_ready():
    assert xet(b(), san_sang=set()) == "bi-chan"


def test_buoc_sau_bi_chan_boi_escalation_mo_hoac_bead_thieu():
    esc = bead("hr-e", issue_type="decision")
    x = b(status="in_progress", assignee="tram/giao-viec", chan_boi=["hr-e"])
    assert xet(x, esc) == "bi-chan"
    assert xet(x) == "bi-chan"                                                   # hr-e không có trong snapshot
    assert xet(x, bead("hr-e", issue_type="decision", status="closed")) is None


def test_con_cua_feature_theo_plan_chua_giao():
    assert xet(b(parent="hr-f"), bead("hr-f", issue_type="feature", labels=["theo-plan"])) == "cho-merge-spec"
    assert xet(b(parent="hr-f")) == "cho-merge-spec"                              # cha thiếu trong snapshot
    assert xet(b(parent="hr-ep"), bead("hr-ep", issue_type="epic")) is None


def test_thieu_moi_truong_kiem_chi_chan_phieu_chay_ma():
    khong_env = DuAn("hr-codex", Path("/r"), None, {})
    assert xet(b(), du_an=khong_env) == "thieu-moi-truong-kiem"
    assert xet(b(issue_type="spike"), du_an=khong_env) is None
