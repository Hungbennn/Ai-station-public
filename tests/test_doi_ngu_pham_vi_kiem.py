from types import SimpleNamespace
import pytest
from tram.tho.kiem_cong import dau_do_that


def test_chi_thu_hep_repo_khong_bo_kiem_khe(monkeypatch, tmp_path):
    from tram.tho import kiem_cong
    da = []
    monkeypatch.setattr(kiem_cong, "cach_ly", lambda ch, ds, **kw: da.extend(ds) or [])
    k = SimpleNamespace(du_an=lambda: ["ben-station", "hr-codex"], ping=lambda: {}, kiem_am=lambda: None)
    dd = dau_do_that(object(), k, du_an=("ben-station",))
    assert dd.du_an() == ["ben-station"] and dd.dang_nhap is not None
    dd.cach_ly()
    assert da == ["ben-station"]
    with pytest.raises(ValueError, match="không có"):
        dau_do_that(object(), k, du_an=("khong-co",))
