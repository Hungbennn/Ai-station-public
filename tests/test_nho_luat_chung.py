"""1b-3: luật cứng xét với danh sách của MỌI dự án cho /vai, /chung; câu gộp ở /chung, /vai cũng qua luật."""
import pytest

from nho_gia import ClientGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.gop import KetQuaGop, gop
from tram.nho.luat import LuatDuAn, ly_do_nghiep_vu
from tram.nho.luat_chung import luat_moi_du_an, ten_du_an_trong

LUAT = {"hr-codex": LuatDuAn(("Pay", "Book"), ("Công ty Sao Mai",)), "ke-toan": LuatDuAn(("Ledger", "Pay"), ()),
        "rong": LuatDuAn()}


def test_hop_luat_moi_du_an_bo_trung_giu_thu_tu():
    l = luat_moi_du_an(["hr-codex", "ke-toan", "rong"], LUAT.__getitem__)
    assert l == LuatDuAn(("Pay", "Book", "Ledger"), ("Công ty Sao Mai",))
    assert luat_moi_du_an([], LUAT.__getitem__) == LuatDuAn()


@pytest.mark.parametrize("cau, cham", [
    ("Sửa Ledger phải chạy lại báo cáo", True),          # module của dự án KHÁC hr-codex vẫn chặn
    ("Gửi công ty sao mai bản nháp trước", True),        # tên khách, không phân biệt hoa thường
    ("Phí 100k mỗi lần", True),
    ("Chạy test trước khi bàn giao", False)])
def test_luat_hop_bat_moi_du_an(cau, cham):
    assert bool(ly_do_nghiep_vu(cau, luat_moi_du_an(LUAT, LUAT.__getitem__))) is cham


def test_yaml_hong_thi_loi_noi_len():
    def hong(ten):
        raise ValueError(f"{ten}.yaml hỏng")
    with pytest.raises(ValueError):
        luat_moi_du_an(["a"], hong)


@pytest.mark.parametrize("cau, ra", [
    ("Repo hr-codex dùng artisan", ["tên dự án (hr-codex)"]),
    ("HR-CODEX: chạy test", ["tên dự án (hr-codex)"]),
    ("hr-codex-2 là repo khác", []),                     # trọn từ, kể cả dấu '-'
    ("Không nhắc dự án nào", [])])
def test_ten_du_an_trong_noi_dung(cau, ra):
    assert ten_du_an_trong(cau, ["hr-codex", "ke-toan"]) == ra


@pytest.mark.parametrize("pv", ["/chung", "/vai/coder"])
def test_cau_gop_ngoai_du_an_cham_luat_thi_bo_gop(pv):
    def cu(i):
        return ky_uc(i, pv, vector=(1.0, 0.0), noi_dung=f"cũ {i}", nguon=({"loai": "thang_cap", "id_goc": i},))
    c = ClientGia(tra_loi({"quyet_dinh": [{"id": "a", "hanh_dong": "gop"}, {"id": "b", "hanh_dong": "thay"}],
                           "noi_dung_gop": "Module Ledger cần chạy lại", "co_ten_rieng": False}))
    kq = gop(c, nap_vai("nho-gop"), noi_dung_moi="mới", moi_dai_ca=False, pham_vi=pv, ung_vien=[cu("a"), cu("b")],
             luat=luat_moi_du_an(LUAT, LUAT.__getitem__))
    assert kq == KetQuaGop("mới", ("b",), ())
