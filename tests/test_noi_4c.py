"""Nối 4c dùng giả, không mạng, không đọc Keychain hay chạy CLI thật."""
from types import SimpleNamespace

import pytest

from tram.giao_viec.noi_4c import nap_phu_thuoc_4c
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c


def test_mac_dinh_khong_goi_dependency(tmp_path):
    def cam(**kwargs):
        raise AssertionError("không được gọi khi tắt")
    p = tmp_path / "c.yaml"
    assert nap_phu_thuoc_4c(p, tao=cam, nho=cam) == PhuThuoc4c()
    p.write_text("phu_thuoc_4c: {github: false, gitnexus: false, memory: false}")
    assert nap_phu_thuoc_4c(p, tao=cam, nho=cam) == PhuThuoc4c()


def test_cau_hinh_chi_boolean_va_khoa_biet(tmp_path):
    p = tmp_path / "c.yaml"
    for raw in ('{github: 1}', '{memory: "false"}', '{ngoai: true}', '[]'):
        p.write_text("phu_thuoc_4c: " + raw)
        with pytest.raises(ValueError):
            nap_phu_thuoc_4c(p)


def test_noi_that_va_tung_dependency(tmp_path, monkeypatch):
    from tram.giao_viec import noi_that
    p = tmp_path / "c.yaml"
    p.write_text("phu_thuoc_4c: {github: true, memory: true}")
    calls = []
    gh, recall = object(), lambda *a: []
    def tao(**kw):
        calls.append(kw)
        return PhuThuoc4c(gh=gh)
    dep = nap_phu_thuoc_4c(p, tao=tao, nho=lambda: recall)
    assert calls == [{"github": True, "gitnexus": False, "memory": False}]
    assert dep.gh is gh and dep.nho_lai is recall
    monkeypatch.setattr(noi_that, "nap_phu_thuoc_4c", lambda: dep)
    cg = SimpleNamespace(bat=False, principal_kiem=None, thu_muc_kiem=None)
    assert noi_that.dung_bo_that(cg, None).p4c == PhuThuoc4c()
    cg.bat = True
    assert noi_that.dung_bo_that(cg, None).p4c is dep
