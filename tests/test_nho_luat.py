import pytest

from tram.nho.luat import LuatDuAn, ly_do_nghiep_vu

HR = LuatDuAn(module=("Fin", "Comp", "Plan", "Book", "Hr"), tu_khoa_khach=("Vietravel", "Saigontourist"))


@pytest.mark.parametrize("cau", [
    "Phụ thu 100₫ cho mỗi khách", "Giảm 10k mỗi vé", "Cọc 500.000đ trước 3 ngày", "Giá 1,5 triệu",
    "Hoàn 200 usd khi huỷ", "Phí 2 tỷ", "Thưởng 5 tr/tháng", "Giá $15 mỗi vé", "Trả 30 nghìn tiền ship",
    "Phí 100 VNĐ", "Phí 100 vnd", "Hạn mức 3 tỉ", "Giá 1 000 000 đ", "ngưỡng 2 ngàn"])
def test_so_tien_khop(cau):
    assert any(l.startswith("số tiền") for l in ly_do_nghiep_vu(cau, LuatDuAn()))


@pytest.mark.parametrize("cau", [
    "Kiểm 3 điểm kiểm trước khi merge", "Có 2 đường dẫn cần sửa", "Sửa 10 địa chỉ email mẫu",
    "Chạy 5 km test", "Lệnh `php artisan test --filter Tour`", "Đợi 2 tuần",
    "Bản 1.2.3 lỗi", "Có 4 khách", "Chạy 10 test", "Ghi 3 dòng", "So 2 tỉ lệ chuyển đổi", "Giữ 2 tỷ lệ"])
def test_so_tien_khong_khop(cau):
    assert not any(l.startswith("số tiền") for l in ly_do_nghiep_vu(cau, LuatDuAn()))


def test_module_tron_tu_phan_biet_hoa_thuong():
    assert ly_do_nghiep_vu("Sửa form trong module Fin", HR) == ["tên module (Fin)"]
    assert ly_do_nghiep_vu("lập plan rồi book vé", HR) == []           # tiếng Anh thường không khớp
    assert ly_do_nghiep_vu("Finance team", HR) == []                     # không trọn từ
    assert ly_do_nghiep_vu("HR Codex dùng Laravel", HR) == []            # "HR" ≠ "Hr"


def test_module_dang_duong_dan_va_controller():
    assert ly_do_nghiep_vu("Sửa erp/app/Modules/Toacap/x.php", LuatDuAn()) == ["tên module (Modules/Toacap)"]
    assert ly_do_nghiep_vu("Thêm hàm vào InvoiceController", LuatDuAn()) == ["tên module (InvoiceController)"]


def test_ten_khach_tu_danh_sach_hoac_co_ten_rieng():
    assert ly_do_nghiep_vu("Đoàn của vietravel đi Huế", HR) == ["tên khách (Vietravel)"]
    assert ly_do_nghiep_vu("Đoàn đi Huế", HR) == []
    assert ly_do_nghiep_vu("Đoàn đi Huế", HR, co_ten_rieng=True) == ["tên khách (LLM báo có tên riêng)"]
    assert ly_do_nghiep_vu("Đoàn đi Huế", LuatDuAn(tu_khoa_khach=("", "  "))) == []


def test_nhieu_ly_do_va_nfc():
    to_hop = "Giá 50k cho module Fin"  # dấu sắc tổ hợp → NFC
    assert ly_do_nghiep_vu(to_hop, HR) == ["số tiền (50k)", "tên module (Fin)"]


def test_luat_tu_cau_hinh_du_an(tmp_path):
    from tram.cau_hinh.du_an import nap_du_an
    from tram.nho.luat import luat_cua_du_an
    (tmp_path / "demo.yaml").write_text("ten: demo\nduong_dan: /tmp/demo\nmodule: [Fin, Book]\n"
                                        "tu_khoa_khach: [Vietravel]\n", encoding="utf-8")
    assert luat_cua_du_an("demo", thu_muc=tmp_path) == LuatDuAn(("Fin", "Book"), ("Vietravel",))
    assert luat_cua_du_an("da-go", thu_muc=tmp_path) == LuatDuAn()
    (tmp_path / "xau.yaml").write_text("ten: xau\nduong_dan: /tmp/x\nmodule: Fin\n", encoding="utf-8")
    with pytest.raises(ValueError):
        nap_du_an("xau", thu_muc=tmp_path)


def test_du_an_mau_co_module_tu_boi_canh():
    from tram.nho.luat import luat_cua_du_an
    luat = luat_cua_du_an("vi-du")
    assert {"Auth", "Cart", "Catalog", "Order", "Pay", "Report"} <= set(luat.module) and luat.tu_khoa_khach == ()
