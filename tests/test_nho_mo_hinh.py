import math

import pytest

from tram.nho.mo_hinh import (BuocGhi, KyUc, LoiVector, ap_san, chuan_hoa_l2, hop_nguon, id_ky_uc,
                              la_nguon_dai_ca, ma_thao_tac)

N_CHOT = {"loai": "da_chot", "du_an": "hr", "bead_id": "hr-1", "su_kien_id": 5}
N_AGENT = {"loai": "agent", "du_an": "hr", "vai": "coder"}


def ky(**ghi_de) -> KyUc:
    d = dict(id="m-1", noi_dung="Test chạy bằng `php artisan test`", pham_vi="/du-an/hr/cach-lam", nhan=("test",),
             quan_trong=0.6, nguon=(N_CHOT,), nguon_dai_ca=True, hieu_luc_tu="2026-10-13T02:00:00Z",
             tao_luc="2026-10-13T02:00:00Z", mo_hinh_embed="bge-m3@abc", vector=(0.6, 0.8))
    return KyUc(**{**d, **ghi_de})


def test_nguon_dai_ca_khi_moi_nguon_cua_dai_ca():
    assert la_nguon_dai_ca([N_CHOT, {"loai": "tra_ve"}])
    assert not la_nguon_dai_ca([N_CHOT, N_AGENT]) and not la_nguon_dai_ca([])


@pytest.mark.parametrize("q, nguon, mong", [
    (0.1, [N_CHOT], 0.8), (0.3, [{"loai": "dai_ca_sua"}], 0.6), (0.2, [{"loai": "tra_ve"}], 0.6),
    (0.9, [N_CHOT], 0.9), (0.2, [N_AGENT], 0.2), (1.7, [N_AGENT], 0.6), (-1, [N_AGENT], 0.0),
    (0.1, [{"loai": "dai_ca_ghi"}, N_AGENT], 0.8)])
def test_san_quan_trong_tat_dinh(q, nguon, mong):
    assert ap_san(q, nguon) == mong


def test_hop_nguon_bo_trung_giu_thu_tu():
    assert hop_nguon([N_CHOT], [N_AGENT, dict(N_CHOT)]) == (N_CHOT, N_AGENT)


def test_chuan_hoa_l2():
    v = chuan_hoa_l2([3.0, 4.0])
    assert v == (0.6, 0.8) and math.isclose(sum(x * x for x in v), 1.0)
    for xau in ([], [0.0, 0.0], [1.0, float("nan")], [float("inf"), 1.0]):
        with pytest.raises(LoiVector):
            chuan_hoa_l2(xau)


def test_chuan_hoa_l2_gia_tri_cuc_tri():
    v = chuan_hoa_l2([1e308, 1e308])
    assert all(math.isfinite(x) and x > 0 for x in v) and math.isclose(sum(x * x for x in v), 1.0)
    v = chuan_hoa_l2([3e-200, 4e-200])
    assert math.isclose(v[0], 0.6) and math.isclose(v[1], 0.8)


def test_id_on_dinh_theo_thao_tac_va_thu_tu():
    assert ma_thao_tac(812, 1) == "812:1"
    assert id_ky_uc(812, 1, 0) == id_ky_uc(812, 1, 0)
    assert len({id_ky_uc(812, 1, 0), id_ky_uc(812, 1, 1), id_ky_uc(812, 2, 0), id_ky_uc(813, 1, 0)}) == 4
    assert id_ky_uc(1, 1, 0).startswith("m-") and len(id_ky_uc(1, 1, 0)) == 26


def test_buoc_ghi_qua_dict_giu_nguyen():
    b = BuocGhi(ky(), xoa=("m-cu",))
    assert BuocGhi.tu_dict(b.sang_dict()) == b and ky().so_chieu == 2
