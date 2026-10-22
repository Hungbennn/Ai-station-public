import pytest
from tram.giao_viec.co_plan import ghi_plan, duyet, review, cong_plan
from tram.giao_viec.su_kien import su_kien_bead
from kho_phieu_gia import kho_tam, LUC


def q(co="lon"):
    return {"co": co, "thieu": [], "pham_vi": ["src/a.py"], "ban_luat": "v1"}


def test_s4_s5(tmp_path):
    k = kho_tam(tmp_path)
    assert cong_plan([], q("nho")) is None
    assert cong_plan([], q("vua")) == "cho-plan"
    p = ghi_plan(k, "hr", "b", "a" * 40, "docs/plans/b.md", "b" * 64, "B/c1", q(), LUC)
    duyet(k, "hr", "b", p, LUC)
    ds = lambda: su_kien_bead(k, "hr", "b")
    assert cong_plan(ds(), q("vua")) is None
    assert cong_plan(ds(), q()) == "cho-review-plan"
    with pytest.raises(ValueError):
        review(k, "hr", "b", p, "B/c1", "dat", "r1", LUC)
    review(k, "hr", "b", p, "B/c2", "dat", "r1", LUC)
    assert cong_plan(ds(), q()) is None
    review(k, "hr", "b", p, "B/c2", "dat", "r1", LUC)
    assert len([s for s in ds() if s.loai == "co.review"]) == 1
    with pytest.raises(ValueError):
        review(k, "hr", "b", p, "B/c2", "tra-ve", "r1", LUC)
    with pytest.raises(ValueError):
        review(k, "hr", "b", p, "B/c3", "dat", "r2", LUC)
    assert cong_plan(ds(), {**q(), "pham_vi": ["src/a.py", "src/b.py"]}) == "cho-plan"
    k.close()


def test_ba_vong_khong_reset_khi_doi_plan(tmp_path):
    k = kho_tam(tmp_path)
    for i in range(3):
        p = ghi_plan(k, "hr", "b", "a" * 40, "docs/plans/b.md", str(i) * 64, "B/c1", q(), LUC)
        duyet(k, "hr", "b", p, LUC)
        review(k, "hr", "b", p, "B/c2", "tra-ve", str(i), LUC)
    ds = su_kien_bead(k, "hr", "b")
    assert cong_plan(ds, q()) == "hoi-dai-ca-ba-vong"
    p = ghi_plan(k, "hr", "b", "a" * 40, "docs/plans/b.md", "f" * 64, "B/c1", q(), LUC)
    assert cong_plan(su_kien_bead(k, "hr", "b"), q()) == "cho-duyet-plan"
    duyet(k, "hr", "b", p, LUC)
    with pytest.raises(ValueError):
        review(k, "hr", "b", p, "B/c3", "dat", "4", LUC)
    assert cong_plan(su_kien_bead(k, "hr", "b"), q()) == "hoi-dai-ca-ba-vong"
    assert cong_plan(ds, {**q(), "thieu": ["pham-vi"]}) == "lam-ro-du-lieu"
    k.close()
