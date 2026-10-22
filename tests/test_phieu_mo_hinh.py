import json

import pytest
from pydantic import ValidationError

from phieu_gia import de_xuat
from tram.phieu.mo_hinh import Phieu, che_ma_giao, sinh_ma_giao


def phieu(**ghi_de) -> Phieu:
    return Phieu(**{**de_xuat().model_dump(), "giao_id": "g-20261013-0042", "luot": 3, "khe_id": "B/claude-1",
                    "han_giu": "2026-10-13T03:10:00Z", "ma_giao": sinh_ma_giao(), **ghi_de})


def test_mau_spec_hop_le_va_an_toan_bo_ma_giao():
    p = phieu()
    assert p.repo.nhanh == "tram/hr-6xe1" and p.repo.ref_tam is None and len(p.ma_giao) == 22
    assert "ma_giao" not in p.an_toan() and p.ma_giao not in json.dumps(p.an_toan(), ensure_ascii=False)
    assert Phieu.model_validate_json(p.model_dump_json()) == p


def test_phieu_spec_va_qc_hop_le():
    assert de_xuat(buoc="spec").repo.nhanh == "tram/spec-hr-6xe1"
    assert de_xuat(buoc="qc").can_lenh_kiem is False


@pytest.mark.parametrize("ghi_de", [
    {"vai": "qc"},                                                       # bước code do coder
    {"repo": {"kho": "k", "nhanh": "main", "cha": "a1b2c3d", "nhanh_chinh": "main"}},
    {"repo": {"kho": "k", "nhanh": "tram/khac", "cha": "a1b2c3d", "nhanh_chinh": "main"}},
    {"repo": {"kho": "k", "nhanh": "tram/hr-6xe1", "cha": "HEAD", "nhanh_chinh": "main"}},
    {"lenh_kiem": []},                                                   # can_lenh_kiem mà không có lệnh
    {"lenh_kiem": ["php artisan test --bootstrap x"]},                  # lệnh bắt buộc ngoài allowlist
    {"lenh_cho_phep": ["* x"], "lenh_kiem": []},
    {"ngan_sach": {"so_lan_chay": 4, "phut": 90, "token_ra": 1}},        # #13: tối đa 3
    {"tieu_chi": []}, {"tieu_chi": ["  "]}, {"khoa_chong_trung": "abc"}, {"du_an": "HR"}, {"la": 1},
])
def test_de_xuat_sai(ghi_de):
    with pytest.raises(ValidationError):
        de_xuat(**ghi_de)


@pytest.mark.parametrize("ghi_de", [{"lenh_cho_phep": ["npm run test:unit"]}, {"can_moi_truong_kiem": True}])
def test_phieu_spec_khong_chay_ma_du_an(ghi_de):
    with pytest.raises(ValidationError):
        de_xuat(buoc="spec", **ghi_de)


@pytest.mark.parametrize("ghi_de", [{"giao_id": "g-1"}, {"luot": 0}, {"khe_id": "B claude"},
                                    {"han_giu": "2026-10-13 03:10"}, {"ma_giao": "ngan"}])
def test_phieu_truong_tram_cap_sai(ghi_de):
    with pytest.raises(ValidationError):
        phieu(**ghi_de)


def test_ma_giao_ngau_nhien_va_che():
    a, b = sinh_ma_giao(), sinh_ma_giao()
    assert a != b and len(a) == len(b) == 22
    assert che_ma_giao(f"lỗi gọi với {a} hai lần {a}", a) == "lỗi gọi với *** hai lần ***"
    assert che_ma_giao("x", None) == "x"
