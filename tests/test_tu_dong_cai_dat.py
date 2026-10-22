"""TM-1 (change tu-merge-tu-deploy, dieu-khien-tu-dong): mô hình cài đặt tự động, mặc định, dạng API/sự kiện, kiểm khi
lưu (D69, D71, D73–D76, D88, D97 luật 4 "lệnh có vẻ chứa bí mật bị từ chối"). Hàm thuần — không kho, không mạng."""
from dataclasses import fields, replace

import pytest

from tram.tu_dong.cai_dat import (KHOA_CUNG, MAC_DINH, CaiDatTuDong, loi_cai_dat, loi_lenh, sang_api, truong_doi,
                                  tu_api, tu_phang)

LENH = {"deploy": "/Users/Shared/tram-deploy/repo-nhap/deploy.sh",
        "kiem_song": "curl -fsS --max-time 20 https://repo-nhap.example.vn/suc-khoe",
        "lui": "sh scripts/lui.sh --ve 'ban truoc'"}
DU = tu_api({"tu_merge": True, "tu_deploy": True, "dieu_kien": {"ci": True, "cot": True, "hang_rao": True},
             "lenh": LENH})


def test_gia_tri_mac_dinh_theo_spec():
    """Scenario "Giá trị mặc định": tự merge tắt, tự deploy tắt, ba nút điều kiện bật, ba lệnh trống."""
    assert MAC_DINH == CaiDatTuDong()
    assert (MAC_DINH.tu_merge, MAC_DINH.tu_deploy) == (False, False)
    assert (MAC_DINH.dk_ci, MAC_DINH.dk_cot, MAC_DINH.dk_hang_rao) == (True, True, True)
    assert (MAC_DINH.lenh_deploy, MAC_DINH.lenh_kiem_song, MAC_DINH.lenh_lui) == ("", "", "") and not MAC_DINH.du_lenh


def test_khoa_cung_khong_co_truong_nao():
    """D71, D76: QC, kiểm lại, hàng rào cấu trúc DB luôn bật — mô hình không có chỗ để tắt."""
    ten = {f.name for f in fields(CaiDatTuDong)}
    assert KHOA_CUNG == ("qc", "kiem_lai", "schema")
    assert not set(KHOA_CUNG) & {t.removeprefix("dk_") for t in ten}


def test_dang_api_va_dang_su_kien_qua_lai():
    assert sang_api(DU) == {"tu_merge": True, "tu_deploy": True,
                            "dieu_kien": {"ci": True, "cot": True, "hang_rao": True}, "lenh": LENH}
    assert tu_api(sang_api(DU)) == DU and DU.du_lenh
    assert tu_phang(DU.phang()) == DU
    assert tu_phang({"tu_merge": True, "khoa_tuong_lai": 1}) == replace(MAC_DINH, tu_merge=True)   # mã cũ/mới đọc nhau
    assert tu_api({**sang_api(MAC_DINH), "lenh": {"deploy": "  a.sh  ", "kiem_song": "", "lui": ""}}).lenh_deploy == "a.sh"


def test_truong_doi_theo_thu_tu_mo_hinh():
    assert truong_doi(MAC_DINH, MAC_DINH) == []
    assert truong_doi(MAC_DINH, DU) == ["tu_merge", "tu_deploy", "lenh_deploy", "lenh_kiem_song", "lenh_lui"]


@pytest.mark.parametrize("lenh", ["", *LENH.values(), "make deploy", "./scripts/kiem-song.sh"])
def test_lenh_hop_le(lenh):
    assert loi_lenh(lenh) is None


@pytest.mark.parametrize("lenh, loi", [
    ("a" * 501, "dài quá 500"),
    ("deploy.sh\nrm -rf /", "ký tự điều khiển"),
    ("deploy.sh\tx", "ký tự điều khiển"),
    ("sh 'thieu nhay", "không tách được"),
    ('""', "Lệnh rỗng"),
    ("curl -H 'Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789' https://x.vn", "có vẻ chứa bí mật"),
    ("deploy.sh --token ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8", "có vẻ chứa bí mật"),
    ("API_KEY=sk-ant-" + "x" * 30 + " ./deploy.sh", "có vẻ chứa bí mật"),
    ("psql postgres://tram:matkhau123@db.local/app -c 'select 1'", "có vẻ chứa bí mật"),
])
def test_lenh_bi_tu_choi_bang_cau_hang(lenh, loi):
    ly_do = loi_lenh(lenh)
    assert ly_do is not None and loi in ly_do
    assert lenh not in ly_do and "matkhau123" not in ly_do and "ghp_" not in ly_do      # không chép lệnh vào lỗi


def test_loi_cai_dat_luat_bat_ghi_va_du_lenh():
    assert loi_cai_dat(DU, bat_ghi=True) is None
    assert loi_cai_dat(MAC_DINH, bat_ghi=False) is None                 # dự án chỉ quét thử vẫn lưu lệnh, công tắc tắt
    assert "chỉ quét thử" in loi_cai_dat(replace(MAC_DINH, tu_merge=True), bat_ghi=False)
    assert "chỉ quét thử" in loi_cai_dat(replace(DU, tu_merge=False), bat_ghi=False)
    assert "Chưa khai đủ 3 lệnh" in loi_cai_dat(replace(DU, lenh_lui=""), bat_ghi=True)
    assert loi_cai_dat(replace(DU, tu_deploy=False, lenh_lui=""), bat_ghi=True) is None
    bi_mat = replace(MAC_DINH, lenh_kiem_song="curl -H 'X-Api-Key: " + "Zx9" * 12 + "' https://x.vn")
    assert loi_cai_dat(bi_mat, bat_ghi=True) == "Lệnh kiểm còn sống: Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"
