import pytest

from tram.giao_viec.tieu_chi import digest_tieu_chi, khoa_chong_trung, lenh_bat_buoc, tach_tieu_chi

MAU = ["php artisan test --filter *", "npm run test:unit"]


def test_tach_va_chuan_hoa():
    s = "  - Tên kết thúc 'ỷ'   không mất byte \n\n* Có test\n1. Một\n2) Hai\n   \n3.Ba"
    assert tach_tieu_chi(s) == ["Tên kết thúc 'ỷ' không mất byte", "Có test", "Một", "Hai", "Ba"]


@pytest.mark.parametrize("s", ["", "   \n  \n", "- \n* "])
def test_tieu_chi_rong(s):
    assert tach_tieu_chi(s) == []


def test_digest_on_dinh_va_doi_theo_noi_dung():
    a = digest_tieu_chi(["x", "y"])
    assert a.startswith("sha256:") and a == digest_tieu_chi(["x", "y"])
    assert a != digest_tieu_chi(["y", "x"]) and a != digest_tieu_chi(["x"])


def test_lenh_bat_buoc_gom_mac_dinh_va_lenh_khop_trong_design():
    design = ("Chạy `php artisan test --filter TomTat` sau khi sửa.\n- $ npm run test:unit\n"
              "npm run build\n`php artisan test --filter 'X;rm'`\nphp artisan migrate")
    assert lenh_bat_buoc(["npm run test:unit"], design, MAU) == ["npm run test:unit",
                                                                 "php artisan test --filter TomTat"]


def test_lenh_bat_buoc_khong_co_gi():
    assert lenh_bat_buoc([], "", MAU) == [] and lenh_bat_buoc([], "npm run test:unit", []) == []


def test_khoa_chong_trung_doi_theo_moi_thanh_phan():
    goc = ("hr-codex", "a1b2c3d", "hr-1", "code", "1", "0")
    k = khoa_chong_trung(*goc)
    assert len(k) == 71 and k.startswith("sha256:")
    for i in range(len(goc)):
        doi = list(goc)
        doi[i] = doi[i] + "x"
        assert khoa_chong_trung(*doi) != k
