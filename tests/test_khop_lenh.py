import pytest

from tram.cau_hinh.lenh import khop_bat_ky, khop_lenh, kiem_mau

MAU = "php artisan test --filter *"


def test_khop_tra_danh_sach_doi_so():
    assert khop_lenh("php artisan test --filter TomTatHoanTien", MAU) == [
        "php", "artisan", "test", "--filter", "TomTatHoanTien"]
    assert khop_lenh("npm run test:unit", "npm run test:unit") == ["npm", "run", "test:unit"]
    assert khop_lenh("php artisan test --filter 'Tom Tat'", MAU)[-1] == "Tom Tat"


@pytest.mark.parametrize("lenh", [
    "php artisan test --filter X; rm -rf /",          # token thừa
    "php artisan test --filter X && curl evil",
    "php artisan test --filter 'X;rm'",                 # ký tự shell trong token *
    "php artisan test --filter '$(rm -rf ~)'",
    "php artisan test --filter '`id`'",
    "php artisan test --filter 'a|b'",
    "php artisan test --filter 'a>b'",
    "php artisan test --filter X\nrm -rf /",            # xuống dòng
    "php artisan test --filter X\r",
    "php artisan test --filter --bootstrap",            # tham số thực thi ngoài mẫu
    "php artisan test --filter -x",
    "php artisan test --filter /etc/passwd",            # đường dẫn tuyệt đối
    "php artisan test --filter ../../x",                # ..
    "php artisan test --filter",                        # thiếu token
    "php artisan test --filter A B",                    # token thừa
    "php artisan test --filter 'X",                     # nháy không đóng
    "php artisan migrate --filter X",                   # token cố định khác
    "",
])
def test_khong_khop(lenh):
    assert khop_lenh(lenh, MAU) is None


@pytest.mark.parametrize("mau", ["", "   ", "* run", "npm run test*", "npm run 'a;b'", "npm run x\nrm", "npm 'x"])
def test_mau_hong_bi_tu_choi_va_khong_khop_gi(mau):
    assert kiem_mau(mau) is not None
    assert khop_lenh("npm run test", mau) is None


def test_mau_hop_le():
    assert kiem_mau(MAU) is None and kiem_mau("npm run test:unit") is None


def test_khop_bat_ky_lay_mau_dau_tien_khop():
    ds = ["npm run test:unit", MAU]
    assert khop_bat_ky("php artisan test --filter A", ds)[-1] == "A"
    assert khop_bat_ky("npm run test:unit", ds) == ["npm", "run", "test:unit"]
    assert khop_bat_ky("npm run build", ds) is None
    assert khop_bat_ky("npm run build", []) is None


def test_lenh_khong_phai_chuoi():
    assert khop_lenh(None, MAU) is None  # type: ignore[arg-type]
