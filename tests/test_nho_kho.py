import math
import random
import warnings
from collections import Counter
from datetime import timedelta

import pytest

from tram.nho.kho import KhoKyUc
from tram.nho.mo_hinh import KyUc

D = 16


def vec(seed):
    r = random.Random(seed)
    v = [r.gauss(0, 1) for _ in range(D)]
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


def ky(id, pham_vi="/du-an/x/cach-lam", v=None, **ghi_de):
    d = dict(id=id, noi_dung=f"ký ức {id}", pham_vi=pham_vi, nhan=("a",), quan_trong=0.5,
             nguon=({"loai": "dai_ca_sua", "du_an": "x"},), nguon_dai_ca=True, hieu_luc_tu="2026-10-01T00:00:00Z",
             tao_luc="2026-10-01T00:00:00Z", mo_hinh_embed="gia@1", vector=v or vec(id))
    return KyUc(**{**d, **ghi_de})


@pytest.fixture
def kho(tmp_path):
    return KhoKyUc(tmp_path / "lancedb", so_chieu=D)


def test_them_idempotent_va_doc_lai_du_truong(kho, tmp_path):
    k = ky("m-1", nhan=("test", "php"), nguon=({"loai": "da_chot", "su_kien_id": 5},))
    assert kho.them(k) and not kho.them(k)
    doc = KhoKyUc(tmp_path / "lancedb", so_chieu=D).lay(["m-1", "m-khong"])
    assert list(doc) == ["m-1"]
    d = doc["m-1"]
    assert (d.noi_dung, d.pham_vi, d.nhan, d.nguon, d.nguon_dai_ca, d.da_xoa) == (
        k.noi_dung, k.pham_vi, ("test", "php"), ({"loai": "da_chot", "su_kien_id": 5},), True, False)
    assert all(abs(a - b) < 1e-6 for a, b in zip(d.vector, k.vector)) and kho.dem() == 1


def test_sai_so_chieu_bao_loi(kho, tmp_path):
    with pytest.raises(ValueError):
        kho.them(ky("m-1", v=(1.0, 0.0)))
    with pytest.raises(ValueError):
        KhoKyUc(tmp_path / "lancedb", so_chieu=D + 1)


def test_prefilter_kho_100_du_an_y_va_3_du_an_x(kho):
    for i in range(100):
        kho.them(ky(f"y-{i:03d}", "/du-an/y/cach-lam" if i % 2 else "/du-an/y/nghiep-vu"))
    for i in range(3):
        kho.them(ky(f"x-{i}", "/du-an/x/cach-lam"))
    q = vec("y-007")                                   # truy vấn trùng hệt một ký ức của Y
    kq = kho.tim(q, ["/du-an/x/nghiep-vu", "/du-an/x/cach-lam"], mo_hinh="gia@1", gioi_han=50)
    assert sorted(k.id for k, _ in kq) == ["x-0", "x-1", "x-2"]
    top = kho.tim(q, ["/du-an/y/cach-lam"], mo_hinh="gia@1", gioi_han=1)
    assert top[0][0].id == "y-007" and abs(top[0][1] - 1.0) < 1e-5


def test_so_khop_chinh_xac_khong_tien_to(kho):
    kho.them(ky("m-1", "/du-an/hr-codex/cach-lam"))
    assert kho.tim(vec("m-1"), ["/du-an/hr/cach-lam", "/du-an/hr/nghiep-vu"], mo_hinh="gia@1", gioi_han=50) == []


def test_loc_model_xoa_mem_va_hieu_luc(kho):
    kho.them(ky("m-cu", mo_hinh_embed="bge-m3@cu"))
    kho.them(ky("m-xoa"))
    kho.them(ky("m-cho", hieu_luc_tu="2026-10-20T00:00:00Z"))
    kho.them(ky("m-ok"))
    assert kho.xoa_mem(["m-xoa", "m-khong"]) == 1 and kho.xoa_mem(["m-xoa"]) == 0
    tap = ["/du-an/x/cach-lam"]
    assert {k.id for k, _ in kho.tim(vec(1), tap, mo_hinh="gia@1", gioi_han=50,
                                     bay_gio="2026-10-13T00:00:00Z")} == {"m-ok"}
    assert {k.id for k, _ in kho.tim(vec(1), tap, mo_hinh="gia@1", gioi_han=50)} == {"m-ok", "m-cho"}
    assert kho.lay(["m-xoa"])["m-xoa"].da_xoa


def test_xoa_lan_hai_khong_tao_phien_ban(kho):
    kho.them(ky("m-1"))
    kho.xoa_mem(["m-1"])
    pb = kho.so_phien_ban()
    kho.xoa_mem(["m-1"])
    kho.them(ky("m-1"))
    assert kho.so_phien_ban() == pb


def test_cap_nhat_dung_gom_theo_so_dem(kho):
    for i in range(3):
        kho.them(ky(f"m-{i}"))
    pb = kho.so_phien_ban()
    kho.cap_nhat_dung(Counter({"m-0": 2, "m-1": 2, "m-2": 1}), "2026-10-13T05:00:00Z")
    assert kho.so_phien_ban() == pb + 2
    d = kho.lay(["m-0", "m-2"])
    assert (d["m-0"].so_lan_dung, d["m-2"].so_lan_dung, d["m-0"].dung_luc) == (2, 1, "2026-10-13T05:00:00Z")


def test_don_dep_xoa_phien_ban_cu_giu_du_lieu(kho):
    for i in range(5):
        kho.them(ky(f"m-{i}"))
    kho.xoa_mem(["m-0"])
    assert kho.so_phien_ban() > 2
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kho.don_dep(timedelta(0))
    assert kho.so_phien_ban() == 1 and kho.dem() == 5 and kho.dem("da_xoa = true") == 1


def test_chuoi_trong_dieu_kien_duoc_thoat(kho):
    kho.them(ky("m-1"))
    assert kho.lay(["x' OR '1'='1"]) == {} and kho.xoa_mem(["x' OR id != '"]) == 0
