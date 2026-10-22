"""Mã thoát thật của dseditgroup checkmember trên 24G90: yes→0, no→67 (đo 19/10)."""
from types import SimpleNamespace

import pytest

from tram.chu import quan_kiem_membership as m


@pytest.fixture(autouse=True)
def nhom_co(monkeypatch):
    monkeypatch.setattr(m.dinh_danh, 'nhom', lambda g: {'gid': 504})
    monkeypatch.setattr(m.dinh_danh, 'user', lambda u: {'uid': 501})


def chay(ma, ra):
    return lambda *a, **k: SimpleNamespace(returncode=ma, stdout=ra)


def test_khong_la_thanh_vien_thoat_67():
    assert m.quan_sat('thanh_vien', 'tram-quan-kiem/hungle',
                      chay=chay(67, 'no hungle is NOT a member of tram-quan-kiem\n')) is None


def test_la_thanh_vien_thoat_0():
    assert m.quan_sat('thanh_vien', 'g/u', chay=chay(0, 'yes u is a member of g\n')) == {
        'user': {'uid': 501}, 'nhom': {'gid': 504}}


@pytest.mark.parametrize('ma,ra', [(1, 'no x'), (0, 'no x'), (64, 'Group not found.'), (67, 'la')])
def test_ket_qua_la_khong_doan(ma, ra):
    with pytest.raises(OSError):
        m.quan_sat('thanh_vien', 'g/u', chay=chay(ma, ra))
