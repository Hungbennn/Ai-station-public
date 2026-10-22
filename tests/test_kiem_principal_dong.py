"""`tram giao kiem` — mục principal (3C-D6, hợp đồng P1 H7), các ca KHÔNG chạy probe hoặc phải ĐÓNG cổng: danh tính
sai, thu hồi không xác nhận, đang kiểm lại (khoá), cổng đóng/dấu hạn tổng, lệnh quá hạn không dừng/không thu hồi được.
Dùng chung bộ giả của `test_kiem_principal.py` — không sudo thật."""
import pytest

from test_kiem_principal import PK, chay_gia, cong_tt, dung_lenh, kiem, muc
from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
from tram.giao_viec.cong_that import dung_cong
from tram.kiem.danh_tinh import LoiDanhTinh


def test_danh_tinh_sai_thi_khong_chay_probe_nao_va_dong_cong(tmp_path):
    goi, lenh, thu = [], [], []

    def sai(ten, boc, kill):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành")
    m = muc(kiem(tmp_path, chay=chay_gia(goi=goi), chay_lenh=dung_lenh(goi=lenh), xac_minh=sai, thu_hoi=thu.append))
    assert m["principal: danh tính (UID thực) + thu hồi trước probe"] == "do" and "principal: lượt tạm" not in m
    assert goi == [["/usr/bin/sudo", "-n", "-l"]] and lenh == thu == [] and cong_tt() == "dong"


def test_thu_hoi_khong_xac_nhan_thi_do_va_dong_cong(tmp_path):
    def thu_hoi():
        raise LoiBanChep("còn 1 tiến trình uid 777 sau kill -1")
    m = muc(kiem(tmp_path, thu_hoi=thu_hoi))
    assert m["principal: danh tính (UID thực) + thu hồi trước probe"] == "do" and cong_tt() == "dong"


def test_dang_kiem_lai_thi_khong_chay_probe_duoi_tram_kiem(tmp_path):
    goi = []
    with giu_khoa():
        m = kiem(tmp_path, chay=chay_gia(goi=goi))
    assert m[-1].muc_do == "do" and "đang có lần kiểm lại" in m[-1].chi_tiet and goi == [["/usr/bin/sudo", "-n", "-l"]]


@pytest.mark.parametrize("dong", ["cong", "dau"])
def test_cong_dong_hoac_dau_han_tong_thi_khong_chay_probe(tmp_path, tram_home_tam, dong):
    goi = []
    if dong == "cong":
        dung_cong(PK, tmp_path, cac_du_an=list).dong("lượt g-1: LoiBanChep")
    else:
        tram_home_tam.mkdir(parents=True, exist_ok=True)
        (tram_home_tam / "kiem-lai.dong").touch()
    m = kiem(tmp_path, chay=chay_gia(goi=goi))
    assert m[-1].muc_do == "do" and "không chạy probe" in m[-1].chi_tiet and goi == [["/usr/bin/sudo", "-n", "-l"]]


@pytest.mark.parametrize("het_gio, da_thu_hoi", [(False, True), (True, False)])
def test_khong_dung_hoac_khong_thu_hoi_duoc_lenh_qua_han_la_do(tmp_path, het_gio, da_thu_hoi):
    m = muc(kiem(tmp_path, chay_lenh=dung_lenh(het_gio, da_thu_hoi)))
    assert m["principal: dừng được lệnh quá hạn"] == "do" and cong_tt() == "dong"
