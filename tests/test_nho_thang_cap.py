"""1b-3: tìm cặp thăng cấp — chỉ cach-lam của hai dự án khác nhau, ≥ 0,85, không lặp cặp đã có (kể cả đã xoá mềm)."""
import math

import pytest

from nho_gia import ky_uc
from tram.nho.kho import KhoKyUc
from tram.nho.nhat_ky import NhatKy
from tram.nho.thang_cap import (CapThangCap, cac_cap_da_co, dich_thang_cap, id_thang_cap, khoa_cap,
                                tim_cap)

MO = "gia@1"


def vec(cos: float, truc: int = 0, phu: int = 15) -> tuple[float, ...]:
    """Vector 16 chiều có cosine = `cos` với trục `truc` (phần còn lại nằm trên trục `phu`)."""
    v = [0.0] * 16
    v[truc], v[phu] = cos, math.sqrt(max(0.0, 1 - cos * cos))
    return tuple(v)


@pytest.fixture
def kho(tmp_path):
    return KhoKyUc(tmp_path / "lancedb", so_chieu=16)


def them(kho, id, pv, v, **kw):
    kho.them(ky_uc(id, pv, vector=v, **kw))


def test_chi_cap_cach_lam_hai_du_an_khac_nhau(kho, tmp_path):
    them(kho, "m-a", "/du-an/a/cach-lam", vec(1.0))
    them(kho, "m-b", "/du-an/b/cach-lam", vec(1.0))
    them(kho, "m-c", "/du-an/c/cach-lam", vec(1.0))
    them(kho, "m-a2", "/du-an/a/cach-lam", vec(1.0, 1))           # cùng dự án a với m-a3 → không cặp
    them(kho, "m-a3", "/du-an/a/cach-lam", vec(1.0, 1))
    them(kho, "m-n", "/du-an/d/nghiep-vu", vec(1.0))              # nghiep-vu không bao giờ thăng cấp
    them(kho, "m-v", "/chung", vec(1.0))
    ds = tim_cap(kho, MO, bo_qua=set(), toi_da=10)
    assert [c.khoa for c in ds] == ["m-a|m-b"]                      # m-c chỉ còn cặp với a/b đã dùng trong lượt
    assert ds[0].a.id == "m-a" and ds[0].cosine == pytest.approx(1.0)


def test_nguong_085(kho):
    them(kho, "m-1", "/du-an/a/cach-lam", vec(1.0))
    them(kho, "m-2", "/du-an/b/cach-lam", vec(0.84, phu=14))
    assert tim_cap(kho, MO, bo_qua=set(), toi_da=10) == []
    them(kho, "m-3", "/du-an/c/cach-lam", vec(0.86))
    assert [c.khoa for c in tim_cap(kho, MO, bo_qua=set(), toi_da=10)] == ["m-1|m-3"]


def test_bo_ban_da_xoa_khac_model_va_gioi_han(kho):
    them(kho, "m-1", "/du-an/a/cach-lam", vec(1.0))
    them(kho, "m-2", "/du-an/b/cach-lam", vec(1.0), da_xoa=True)
    them(kho, "m-3", "/du-an/c/cach-lam", vec(1.0), mo_hinh="gia@cu")
    assert tim_cap(kho, MO, bo_qua=set(), toi_da=10) == []
    them(kho, "m-4", "/du-an/b/cach-lam", vec(1.0, 2))
    them(kho, "m-5", "/du-an/c/cach-lam", vec(1.0, 2))
    them(kho, "m-6", "/du-an/c/cach-lam", vec(0.99))
    assert [c.khoa for c in tim_cap(kho, MO, bo_qua=set(), toi_da=1)] == ["m-4|m-5"]
    assert len(tim_cap(kho, MO, bo_qua=set(), toi_da=10)) == 2


def test_cap_da_thang_cap_ke_ca_da_xoa_mem_va_so_cap(kho, tmp_path):
    them(kho, "m-a", "/du-an/a/cach-lam", vec(1.0))
    them(kho, "m-b", "/du-an/b/cach-lam", vec(1.0))
    them(kho, "m-c", "/du-an/c/cach-lam", vec(1.0))
    them(kho, "m-t", "/chung", vec(1.0), da_xoa=True, nguon=(
        {"loai": "thang_cap", "id_goc": "m-b", "du_an": "b"}, {"loai": "thang_cap", "id_goc": "m-a", "du_an": "a"}))
    nk = NhatKy(tmp_path / "nk.db")
    nk.ghi_cap("m-b|m-c", "tu_choi")
    da_co = cac_cap_da_co(kho, nk)
    assert da_co == {"m-a|m-b", "m-b|m-c"}
    assert [c.khoa for c in tim_cap(kho, MO, bo_qua=da_co, toi_da=10)] == ["m-a|m-c"]


def test_dich_do_tram_tinh_theo_vai():
    def k(i, *vai):
        return ky_uc(i, vector=vec(1.0), nguon=tuple({"loai": "ban_giao", "du_an": "x", "vai": v} for v in vai)
                     or ({"loai": "dai_ca_sua"},))
    assert dich_thang_cap(k("a", "coder"), k("b", "coder", "coder")) == "/vai/coder"
    assert dich_thang_cap(k("a", "coder"), k("b", "qc")) == "/chung"
    assert dich_thang_cap(k("a", "coder", "qc"), k("b", "coder")) == "/chung"
    assert dich_thang_cap(k("a"), k("b")) == "/chung"                       # 1b-1: cot.* không mang vai
    assert dich_thang_cap(k("a", "Coder!"), k("b", "Coder!")) == "/chung"


def test_khoa_va_id_on_dinh():
    assert khoa_cap("m-b", "m-a") == "m-a|m-b"
    assert id_thang_cap("m-a|m-b") == id_thang_cap(khoa_cap("m-b", "m-a")) != id_thang_cap("m-a|m-c")
    assert id_thang_cap("m-a|m-b").startswith("m-") and len(id_thang_cap("m-a|m-b")) == 26
    assert CapThangCap(ky_uc("m-a", vector=vec(1)), ky_uc("m-b", vector=vec(1)), 1.0).khoa == "m-a|m-b"
