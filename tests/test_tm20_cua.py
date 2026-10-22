"""Chốt bền và thân API; thông báo không chứa output của đường deploy."""
import pytest
from pydantic import ValidationError
from tram.api.than import ThanDieuKien
from tram.api.doi_soat_deploy import ThanTiepTuc
from tram.deploy.doi_soat import chua_doi_soat
from tram.deploy.trang_thai import SK


def test_cannot_disable_ci_by_direct_api():
    with pytest.raises(ValidationError):
        ThanDieuKien(ci=False, cot=True, hang_rao=True)


def test_continue_needs_explicit_run_and_version():
    r = ThanTiepTuc(ma_thao_tac="ma-000001", expected_version="1",
                    doi_soat={"ma": "dp-1", "commit": "a" * 40})
    assert r.doi_soat.commit == "a" * 40
    with pytest.raises(ValidationError):
        ThanTiepTuc(ma_thao_tac="ma-000001", expected_version="1", doi_soat={"ma": "dp-1", "commit": "HEAD"})


def test_continue_event_cannot_clear_uncertainty():
    def s(i, loai, **d):
        return SK(i, loai, d, "2026-10-20", "tram/tu-deploy", None)
    x = s(1, "deploy.xong", ma_thao_tac="dp-1", ket_qua="khong_ro")
    ds = [x, s(2, "tu_dong.tiep_tuc")]
    assert chua_doi_soat(ds) == [x]
    ds.append(s(3, "deploy.doi_soat", ma_thao_tac="dp-khac"))
    assert chua_doi_soat(ds) == [x]
    ds.append(s(4, "deploy.doi_soat", ma_thao_tac="dp-1"))
    assert chua_doi_soat(ds) == []
