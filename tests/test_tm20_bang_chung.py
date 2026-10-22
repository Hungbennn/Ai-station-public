"""Không nâng kết quả legacy/agent thành Uq; khớp đủ bộ bằng chứng."""
from dataclasses import replace
import pytest
from test_tu_merge_xet import _ds
from tram.giao_viec.tu_merge_xet import kiem_lai_qc
from tram.tu_dong import cong_kiem


@pytest.mark.parametrize("k,v", [
    ("nguon_kiem", "agent"), ("nguon_kiem", None), ("luot", 2),
    ("giao_id", "g-khac"), ("commit", "c" * 40), ("digest_tieu_chi", "khac"), ("dat", False),
])
def test_sai_mot_phan_la_dong(k, v):
    ds = _ds()
    ds[2] = replace(ds[2], du_lieu={**ds[2].du_lieu, k: v})
    assert kiem_lai_qc(ds, ds[5]) == (False, False)


def test_cong_loi_thi_dong(monkeypatch):
    class Cong:
        def trang_thai(self):
            raise OSError("khong-doc-duoc")
    monkeypatch.setattr(cong_kiem, "CongTuXa", Cong)
    assert cong_kiem.cong_mo() is False


def test_cong_mo_chua_du_neu_con_dau(monkeypatch, tmp_path):
    class Cong:
        def trang_thai(self):
            return {"trang_thai": "mo"}
    monkeypatch.setattr(cong_kiem, "CongTuXa", Cong)
    monkeypatch.setenv("TRAM_HOME", str(tmp_path))
    assert cong_kiem.cong_mo()
    (tmp_path / "kiem-lai.dong").touch()
    assert not cong_kiem.cong_mo()
