"""Định danh cho sổ cài đặt (lát 3c R2; R5/Q02 review đợt 5): user UID + GeneratedUID qua `dscl`, nhà/thư mục thuộc
đúng UID; `dscl` lỗi khác "không có bản ghi" không bị hiểu là "không còn". Không dscl thật — `chay` giả."""
from types import SimpleNamespace

import pytest

from tram.chu.dinh_danh import _doc_dscl, cung, khop, user


def test_dinh_danh_user_doc_dscl_va_ten_tai_su_dung():
    hien = _doc_dscl("GeneratedUID: AB-12\nRealName:\n tram tram-kiem a1\nUniqueID: 502\n")
    assert hien == {"uid": 502, "guid": "AB-12", "ten_day_du": "tram tram-kiem a1"}
    assert khop("user", {"ten_day_du": "tram tram-kiem a1"}, hien) and cung("user", hien, dict(hien))
    assert not cung("user", hien, {**hien, "guid": "CD-34"})           # xoá rồi tạo lại cùng tên: khác GeneratedUID
    assert khop("nha", {"uid": 502}, {"ino": 9, "uid": 502}) and not khop("nha", {"uid": 502}, {"ino": 9, "uid": 7})
    assert not khop("nha", {"uid": 502}, {"loai": "khac", "uid": 502}) and not khop("nha", {"uid": None}, {"ino": 9})
    with pytest.raises(ValueError):
        _doc_dscl("RealName: x\n")


@pytest.mark.parametrize("ma, ra, mong", [(56, "DS Error: -14136 (eDSRecordNotFound)", None), (1, "lỗi", OSError)])
def test_dscl_khong_co_ban_ghi_khac_dscl_loi(ma, ra, mong):
    chay = lambda *a, **kw: SimpleNamespace(returncode=ma, stdout="", stderr=ra)   # noqa: E731
    if mong is None:
        assert user("tram-kiem", chay=chay) is None
    else:
        with pytest.raises(OSError):
            user("tram-kiem", chay=chay)
