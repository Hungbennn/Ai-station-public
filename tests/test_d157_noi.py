"""Tích hợp D157: cổng kiểm dùng cùng bộ lọc; khe chưa đo luôn giữ tàn dư."""
from functools import partial
from types import SimpleNamespace

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import cho_het_uid
from tram.giao_viec.quan_sat_kiem import tien_trinh
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.ngoai_le_uid import con_uid
from tram.tho.don_uid import con_lai

T = TienTrinh(42, 1, 42, 503, 503, 123456)
LOC = partial(con_uid, ban="24G90", mot=lambda pid: T, duong=lambda pid: "/usr/libexec/trustd")


@pytest.mark.parametrize("ten", ["tram-kiem", "tram-quan-kiem"])
def test_don_kiem_va_quan_sat_cung_cho_qua_apple(ten):
    cho_het_uid(503, chup=lambda: [T], loc=LOC, han=0, ten=ten)
    tien_trinh(ten, chup=lambda: [T], loc=LOC, tim=lambda ten: SimpleNamespace(pw_uid=503))


def test_tho_khong_muon_moc_cua_kiem():
    assert con_lai(503, lambda: [T]) == 1


@pytest.mark.parametrize("path", ["/tmp/trustd", "/usr/libexec/trustd --apple", "/bin/sh", "/usr/bin/python3"])
def test_ca_hai_cong_chan_duong_dan_gia(path):
    loc = partial(con_uid, ban="24G90", mot=lambda pid: T, duong=lambda pid: path)
    with pytest.raises(LoiBanChep, match="còn 1"):
        cho_het_uid(503, chup=lambda: [T], loc=loc, han=0, ten="tram-kiem")
    with pytest.raises(LoiBanChep, match="còn 1"):
        tien_trinh("tram-kiem", chup=lambda: [T], loc=loc, tim=lambda ten: SimpleNamespace(pw_uid=503))


def test_quan_sat_uid_khong_ton_tai_dong_cong():
    def thieu(ten):
        raise KeyError(ten)
    with pytest.raises(LoiBanChep, match="không quan sát"):
        tien_trinh("tram-kiem", tim=thieu)


def test_quan_sat_build_khac_bao_do_lai():
    with pytest.raises(LoiBanChep, match="đo lại"):
        tien_trinh("tram-kiem", chup=lambda: [], loc=partial(con_uid, ban="25A1"),
                   tim=lambda ten: SimpleNamespace(pw_uid=503))


def test_thu_hoi_truyen_dung_ten_principal_khong_muon_moc(monkeypatch):
    from tram.giao_viec import cong_that
    from tram.giao_viec.principal_kiem import tu_cach_ly
    from tram.kiem.cong_lich import CongLich

    seen = []
    monkeypatch.setattr(cong_that, "cho_het_uid", lambda uid, **kw: seen.append((uid, kw)))
    pk = tu_cach_ly("user:tram-khe1")
    cong_that.thu_hoi_theo_uid(pk, mo_cong=lambda *a: CongLich((), 503, lambda *a, **kw: None),
                             don_he=lambda *a: None)
    assert seen == [(503, {"ten": "tram-khe1"})]


def test_cho_het_khong_co_ten_khong_tu_mien():
    with pytest.raises(LoiBanChep, match="còn 1"):
        cho_het_uid(503, chup=lambda: [T], loc=LOC, han=0)
