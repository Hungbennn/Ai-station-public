"""3C-D2 (C01, D45): cổng lượt kiểm lại bền trên đĩa — chỉ `ra()` thành công (thu hồi + hai lượt quan sát sạch) mới mở
cho lượt sau. Quan sát thấy gì, quan sát lỗi, tái sinh trễ, crash giữa lượt, tệp trạng thái hỏng → cổng đóng; lượt
N+1 bị từ chối TRƯỚC khi chép/nhận môi trường kiểm. Quan sát/thu hồi giả, không chạy lệnh hệ thống."""
import subprocess

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot


def cong(tmp_path, *quan_sat, thu_hoi=lambda: None, ngu=lambda s: None):
    return CongLuot(tmp_path / "cong.json", thu_hoi=thu_hoi, quan_sat=list(quan_sat), ngu=ngu)


def thay(*lan_co):
    """Quan sát giả: lần gọi thứ i (đếm từ 1) nằm trong `lan_co` thì thấy tàn dư."""
    dem = [0]

    def q():
        dem[0] += 1
        if dem[0] in lan_co:
            raise LoiBanChep(f"tram-kiem còn tàn dư (lần quan sát {dem[0]})")
    return q


def test_chua_mo_lan_nao_thi_dong(tmp_path):
    with pytest.raises(CongDong, match="chua-mo"):
        cong(tmp_path).vao("g-1")


def test_mo_vao_ra_roi_lai_vao_duoc(tmp_path):
    c = cong(tmp_path)
    c.mo_lai()
    c.vao("g-1")
    assert c.trang_thai() == {"trang_thai": "dang-chay", "luot": "g-1"}
    c.ra("g-1")
    c.vao("g-2")


@pytest.mark.parametrize("loi", [LoiBanChep("thư mục cha khác owner còn tệp"), OSError("pgrep mã 3"),
                                 subprocess.TimeoutExpired(["find"], 30), RuntimeError("định dạng lạ")])
def test_quan_sat_thay_hoac_loi_khi_ra_thi_dong_va_chan_luot_sau(tmp_path, loi):
    lan = [0]

    def q():
        lan[0] += 1
        if lan[0] > 3:                                             # 1–2: mo_lai, 3: vào lượt N — sạch
            raise loi
    c = cong(tmp_path, q)
    c.mo_lai()
    c.vao("g-1")
    with pytest.raises(CongDong):
        c.ra("g-1")
    assert c.trang_thai()["trang_thai"] == "dong"
    with pytest.raises(CongDong):
        cong(tmp_path).vao("g-2")                                  # tiến trình trạm mới cũng thấy đóng


def test_tai_sinh_tre_giua_hai_lan_quan_sat(tmp_path):
    ngu = []
    c = cong(tmp_path, thay(2), ngu=ngu.append)                    # lần 1 sạch; tàn dư hiện ra sau khi chờ
    with pytest.raises(CongDong):
        c.mo_lai()
    assert ngu == [c.cho] and c.trang_thai()["trang_thai"] == "dong"


def test_tai_sinh_sau_khi_mo_bi_bat_luc_vao_luot_sau(tmp_path):
    c = cong(tmp_path, thay(3))                                    # mo_lai sạch 2 lần; lần 3 (vào g-2) thấy
    c.mo_lai()
    with pytest.raises(CongDong, match="trước lượt g-2"):
        c.vao("g-2")
    assert c.trang_thai()["trang_thai"] == "dong"


def test_crash_giua_luot_thi_lan_khoi_dong_sau_van_dong(tmp_path):
    c = cong(tmp_path)
    c.mo_lai()
    c.vao("g-1")                                                   # trạm chết trước `ra()`
    with pytest.raises(CongDong, match="dang-chay"):
        cong(tmp_path).vao("g-2")


@pytest.mark.parametrize("noi_dung", ["{hỏng", '{"trang_thai": "MO"}', "[]"])
def test_tep_trang_thai_hong_thi_dong(tmp_path, noi_dung):
    (tmp_path / "cong.json").write_text(noi_dung, encoding="utf-8")
    with pytest.raises(CongDong):
        cong(tmp_path).vao("g-1")


def test_thu_hoi_loi_hoac_dong_chu_dong_thi_dong(tmp_path):
    def hong():
        raise OSError("kill -1 dưới tram-kiem lỗi")
    c = cong(tmp_path, thu_hoi=hong)
    with pytest.raises(CongDong, match="kill -1"):
        c.mo_lai()
    c2 = cong(tmp_path)
    c2.mo_lai()
    c2.vao("g-1")
    c2.dong("lượt g-1 lỗi: LoiBanChep")
    assert c2.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1 lỗi: LoiBanChep"}


def test_ra_cua_luot_khac_hoac_khi_khong_dang_chay_thi_dong(tmp_path):
    c = cong(tmp_path)
    c.mo_lai()
    with pytest.raises(CongDong, match="đổi giữa lượt"):
        c.ra("g-1")                                                # chưa `vao` mà đã `ra`
    c.mo_lai()
    c.vao("g-1")
    with pytest.raises(CongDong):
        c.ra("g-2")
    assert c.trang_thai()["trang_thai"] == "dong"
