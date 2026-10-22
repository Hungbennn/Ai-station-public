from datetime import datetime, timezone
from pathlib import Path

import pytest

import tram
from tram.nho.cham_diem import chon, diem
from tram.nho.mo_hinh import KyUc

BAY_GIO = datetime(2026, 10, 31, tzinfo=timezone.utc)


def ky(id, tao_luc="2026-10-31T00:00:00Z", q=0.5):
    return KyUc(id, id, "/chung", (), q, (), False, tao_luc, tao_luc, "gia@1", (1.0,))


def test_cong_thuc_va_nua_doi_30_ngay():
    assert diem(1.0, "2026-10-31T00:00:00Z", 1.0, BAY_GIO) == pytest.approx(1.0)
    assert diem(0.8, "2026-10-01T00:00:00Z", 0.5, BAY_GIO) == pytest.approx(0.4 + 0.15 + 0.1)
    assert diem(-0.3, "2026-10-31T00:00:00Z", 0.0, BAY_GIO) == pytest.approx(0.3)     # nghĩa = max(0, cos)
    assert diem(0.0, "2026-11-05T00:00:00Z", 0.0, BAY_GIO) == pytest.approx(0.3)      # tương lai: không quá 1


def test_chon_theo_diem_hoa_thi_moi_hon_roi_id():
    ung = [(ky("b"), 0.5), (ky("a"), 0.5), (ky("c", "2026-10-30T00:00:00Z"), 0.5), (ky("d"), 0.9)]
    assert [k.id for k in chon(ung, 3, BAY_GIO)] == ["d", "a", "b"]
    assert chon(ung, 0, BAY_GIO) == [] and len(chon(ung, 10, BAY_GIO)) == 4


def test_do_moi_tu_tao_luc_khong_tu_dung_luc():
    cu = KyUc("cu", "x", "/chung", (), 0.5, (), False, "2026-08-01T00:00:00Z", "2026-08-01T00:00:00Z", "g", (1.0,),
              dung_luc="2026-10-31T00:00:00Z", so_lan_dung=99)
    moi = ky("moi", "2026-10-30T00:00:00Z")
    assert [k.id for k in chon([(cu, 0.6), (moi, 0.6)], 1, BAY_GIO)] == ["moi"]


def test_notice_co_ghi_chu_crewai():
    s = (Path(tram.__file__).parents[1] / "NOTICE").read_text(encoding="utf-8")
    assert "crewAI" in s and "MIT License" in s and "tram/nho/cham_diem.py" in s
