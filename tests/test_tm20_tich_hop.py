"""Đối soát không gửi lại lệnh, khoá tươi và lỗi không rò dữ liệu."""
from types import SimpleNamespace as NS
import pytest
from test_deploy_vong import t
from tram.api import doi_soat_deploy as api
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy.trang_thai import doc_su_kien
from tram.suy.deploy import chi_tiet_deploy
from tram.thao_tac.loi import KhongHopLe


def test_unknown_requires_explicit_confirmation_and_finished_target(t, monkeypatch):
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.add("khong_ro")
    t.buoc()
    can = chi_tiet_deploy(t.kho.db, t.da.ten)["doi_soat"]
    with pytest.raises(KhongHopLe):
        api._doi_soat(t.kho, t.da.ten, None)
    monkeypatch.setattr(api, "DuongDeploy", lambda *a: t)
    xn = NS(ma=can["ma"], commit=can["truoc"])
    t.hong.discard("khong_ro")
    n = len(t.calls)
    api._doi_soat(t.kho, t.da.ten, xn)
    assert t.calls[n:][0][0] == "doi_soat"
    assert not chua_doi_soat(doc_su_kien(t.kho.db, t.da.ten))
    api._doi_soat(t.kho, t.da.ten, xn)
    assert len(t.calls) == n + 1


def test_wait_reason_is_visible_and_deduplicated(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.uq = False
    t.buoc()
    t.buoc()
    ds = t.sk("deploy.cho")
    assert len(ds) == 1 and ds[0]["ly_do"] == "deploy_cho_kiem"
    assert "kiểm" in chi_tiet_deploy(t.kho.db, t.da.ten)["ly_do_deploy"]


def test_failed_rollback_disables_and_freezes(t):
    t.cd(tu_deploy=True)
    t.merge()
    t.hong.update(("deploy", "lui"))
    assert t.buoc() == {"deploy_lui_hong": 1}
    before = len(t.calls)
    t.buoc()
    assert len(t.calls) == before
