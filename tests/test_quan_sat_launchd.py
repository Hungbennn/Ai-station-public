"""3C-D6 (C01 hàng 20–22): khung quan sát launchd của `tram-kiem`. Định dạng `launchctl print` chưa đo (G3) → không có
bộ đọc → ném, cổng giữ đóng; KHÔNG có parser đoán (`dung_cong` luôn cắm: `test_cong_that.py`). Không chạy launchctl."""
from functools import partial

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import launchd

PK = tu_cach_ly("user:tram-kiem")


def test_chua_co_bo_doc_da_do_thi_nem_cong_giu_dong(tmp_path):
    with pytest.raises(LoiBanChep, match="G3"):
        launchd(PK)
    c = CongLuot(tmp_path / "cong.json", thu_hoi=lambda: None, quan_sat=[partial(launchd, PK)], ngu=lambda s: None)
    with pytest.raises(CongDong):
        c.mo_lai()
    assert c.trang_thai()["trang_thai"] == "dong" and "launchd" in c.trang_thai()["ly_do"]


def test_bo_doc_sau_g3_duoc_goi_voi_principal_va_loi_cua_no_lan_ra(tmp_path):
    goi = []
    launchd(PK, doc=goi.append)
    assert goi == [PK]

    def thay(pk):
        raise LoiBanChep("user/502: dịch vụ lạ")
    with pytest.raises(LoiBanChep, match="dịch vụ lạ"):
        launchd(PK, doc=thay)
