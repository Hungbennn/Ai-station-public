from pathlib import Path

import pytest

from tram.cau_hinh.cong_bo import nap_cau_hinh_cong_bo
from tram.cong_bo.nguon import NguonKhoTho, NguonRefTam, chon_nguon


def test_nap_lai_can_map_kho(tmp_path):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text("cong_bo:\n  phuong_an: lai\n  kho_tho: {B: /Users/tram-tho/tram/kho}\n")
    cb = nap_cau_hinh_cong_bo(p)
    assert cb.phuong_an == "lai"
    p.write_text("cong_bo: {phuong_an: lai}\n")
    with pytest.raises(ValueError):
        nap_cau_hinh_cong_bo(p)


def test_lai_chon_theo_may_khong_giu_trang_thai_request(tmp_path, monkeypatch):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text("cong_bo:\n  phuong_an: lai\n  kho_tho: {B: /Users/tram-tho/tram/kho}\n")
    n = chon_nguon(nap_cau_hinh_cong_bo(p))
    monkeypatch.setattr(NguonKhoTho, "lay", lambda self, kho, **kw: "local-" + kw["may_id"])
    monkeypatch.setattr(NguonRefTam, "lay", lambda self, kho, **kw: "remote-" + kw["may_id"])
    kw = dict(du_an="hr", ref_tam="tram/luot/hr-1/1", giao_id="g-1", timeout=1)
    assert n.lay(Path("/k"), may_id="B", **kw) == "local-B"
    assert n.lay(Path("/k"), may_id="C", **kw) == "remote-C"
    assert n.lay(Path("/k"), may_id="B", **kw) == "local-B"


def test_local_loi_khong_fallback_remote(tmp_path, monkeypatch):
    from tram.cong_bo.nguon_lai import NguonLai
    monkeypatch.setattr(NguonKhoTho, "lay", lambda *a, **kw: None)
    monkeypatch.setattr(NguonRefTam, "lay", lambda *a, **kw: pytest.fail("không fallback"))
    n = NguonLai({"B": tmp_path})
    assert n.lay(tmp_path, may_id="B", du_an="hr", ref_tam="r", giao_id="g", timeout=1) is None


def test_don_remote_van_qua_cas(tmp_path, monkeypatch):
    from tram.cong_bo.nguon_lai import NguonLai
    goi = []
    def don(self, kho, **kw):
        goi.append((kho, kw))
        return ["tram/luot/hr-1/1"]
    monkeypatch.setattr(NguonRefTam, "don_cu", don)
    assert NguonLai({"B": tmp_path}).don_cu(tmp_path, bead_id="hr-1", luot=2, timeout=1) == ["tram/luot/hr-1/1"]
    assert goi == [(tmp_path, {"bead_id": "hr-1", "luot": 2, "timeout": 1})]
