import hashlib

import pytest

from tram.nho.danh_tinh import TuChoi, xac_thuc

MA, MA_KHAC = "Abc_def-123456789012ab", "Zbc_def-123456789012ab"     # 22 ký tự base64url
GID, GID_KHAC = "g-20261013-0042", "g-20261013-0043"
MA_DAI_CA = "dai-ca-" + "x" * 40
PHIEU = {GID: {"du_an": "hr-codex", "vai": "coder", "ma_giao": MA, "con_hieu_luc": True},
         GID_KHAC: {"du_an": "erp", "vai": "qc", "ma_giao": MA_KHAC, "con_hieu_luc": True}}
TEN_H = {"giao": b"x-tram-giao-id", "ma": b"x-tram-ma-giao", "auth": b"authorization", "du_an": b"x-tram-du-an",
         "ts": b"tailscale-user-login"}


def h(*cap) -> list[tuple[bytes, bytes]]:
    return [(TEN_H[k], v.encode()) for k, v in cap]


def xt(headers, *, tra=PHIEU.get, bam=hashlib.sha256(MA_DAI_CA.encode()).hexdigest(), du_an=("hr-codex", "erp")):
    return xac_thuc(headers, tra=tra, bam_ma_dai_ca=lambda: bam, co_du_an=lambda t: t in du_an)


def test_phieu_hop_le_cap_vung_cua_phieu_va_duoc_ghi():
    dt = xt(h(("giao", GID), ("ma", MA)))
    assert dt.vung_cap == ("/du-an/hr-codex", "/vai/coder", "/chung") and dt.duoc_ghi
    assert (dt.du_an, dt.giao_id, dt.vai, dt.ma_giao) == ("hr-codex", GID, "coder", MA)
    assert MA not in repr(dt)


@pytest.mark.parametrize("cap", [
    (), (("giao", GID),), (("ma", MA),), (("giao", "g-1"), ("ma", MA)), (("giao", GID), ("ma", "ngan")),
    (("giao", GID), ("ma", MA_KHAC)),                              # ma_giao sai
    (("giao", GID_KHAC), ("ma", MA)),                              # ma_giao của phiếu khác
    (("giao", "g-20261013-9999"), ("ma", MA)),                     # không có phiếu
    (("giao", GID), ("ma", MA), ("auth", "Bearer " + MA_DAI_CA)),  # trộn hai đường
    (("giao", GID), ("ma", MA), ("du_an", "erp")),                 # cố đổi dự án của phiếu
    (("ts", "dai-ca@example.com"),),                               # danh tính Tailscale giả, không mã
    (("giao", GID), ("ma", MA), ("giao", GID_KHAC)),               # header lặp
])
def test_tu_choi_bang_chung_phieu_thieu_sai_hoac_tron(cap):
    with pytest.raises(TuChoi) as e:
        xt(h(*cap))
    assert e.value.ma == 401 and MA not in str(e.value)


def test_phieu_het_hieu_luc_tu_choi():
    for p in ({**PHIEU[GID], "ma_giao": None, "con_hieu_luc": False}, {**PHIEU[GID], "con_hieu_luc": False},
              {**PHIEU[GID], "ma_giao": None}):
        with pytest.raises(TuChoi) as e:
            xt(h(("giao", GID), ("ma", MA)), tra=lambda g: p)
        assert e.value.ma == 401


def test_khong_tra_duoc_phieu_tu_choi_503():
    def sap(g):
        raise RuntimeError(f"lỗi có {MA}")
    for tra in (sap, None, lambda g: {**PHIEU[GID], "du_an": "HR"}):
        with pytest.raises(TuChoi) as e:
            xt(h(("giao", GID), ("ma", MA)), tra=tra)
        assert e.value.ma == 503 and MA not in str(e.value)


def test_phien_tay_hop_le_chi_doc_va_bo_qua_tailscale():
    dt = xt(h(("auth", "Bearer " + MA_DAI_CA), ("du_an", "erp"), ("ts", "ai-do@example.com")))
    assert dt.vung_cap == ("/du-an/erp", "/vai/dieu-phoi", "/chung") and not dt.duoc_ghi
    assert (dt.giao_id, dt.vai, dt.ma_giao) == (None, None, None)


@pytest.mark.parametrize("cap", [
    (("auth", "Bearer " + MA_DAI_CA),), (("du_an", "erp"),), (("auth", "Bearer sai"), ("du_an", "erp")),
    (("auth", MA_DAI_CA), ("du_an", "erp")), (("auth", "Bearer " + MA_DAI_CA), ("du_an", "/du-an/erp")),
    (("auth", "Bearer " + MA_DAI_CA), ("du_an", "ERP")), (("ts", "dai-ca@example.com"), ("du_an", "erp")),
])
def test_phien_tay_thieu_hoac_sai_ma_tu_choi(cap):
    with pytest.raises(TuChoi) as e:
        xt(h(*cap))
    assert e.value.ma == 401 and MA_DAI_CA not in str(e.value)


def test_phien_tay_chua_dat_ma_hoac_khong_co_du_an():
    with pytest.raises(TuChoi, match="chưa đặt mã"):
        xt(h(("auth", "Bearer " + MA_DAI_CA), ("du_an", "erp")), bam=None)
    with pytest.raises(TuChoi) as e:
        xt(h(("auth", "Bearer " + MA_DAI_CA), ("du_an", "kho-khong-co")))
    assert e.value.ma == 403
