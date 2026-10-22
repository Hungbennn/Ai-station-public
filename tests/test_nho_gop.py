import pytest

from nho_gia import ClientGia, ky_uc, tra_loi
from tram.cham_cot.prompt import THE, nap_vai
from tram.nho.gop import KetQuaGop, bao_ve, gop, loc_ung_vien
from tram.nho.luat import LuatDuAn

VAI = nap_vai("nho-gop")
PV = "/du-an/x/cach-lam"
AGENT = ({"loai": "agent", "du_an": "x", "vai": "coder"},)
V = (1.0, 0.0)


def cu(id, **kw):
    return ky_uc(id, kw.pop("pham_vi", PV), vector=V, noi_dung=f"cũ {id}", **kw)


def chay(qd, ung, *, gop_txt="", ten_rieng=False, moi_dai_ca=True, luat=LuatDuAn()):
    c = ClientGia(tra_loi({"quyet_dinh": [{"id": i, "hanh_dong": h} for i, h in qd.items()],
                           "noi_dung_gop": gop_txt, "co_ten_rieng": ten_rieng}))
    return gop(c, VAI, noi_dung_moi="mới", moi_dai_ca=moi_dai_ca, pham_vi=PV, ung_vien=ung, luat=luat), c


def test_loc_ung_vien_nguong_085_toi_da_3_cung_pham_vi():
    ds = [(cu("a"), 0.99), (cu("b", pham_vi="/du-an/x/nghiep-vu"), 0.98), (cu("c"), 0.9), (cu("d"), 0.86),
          (cu("e"), 0.851), (cu("f"), 0.84)]
    assert [k.id for k in loc_ung_vien(ds, PV)] == ["a", "c", "d"]
    assert loc_ung_vien([(cu("g", da_xoa=True), 0.99)], PV) == []


def test_khong_ung_vien_ghi_moi_khong_goi_llm():
    c = ClientGia()
    assert gop(c, VAI, noi_dung_moi="mới", moi_dai_ca=True, pham_vi=PV, ung_vien=[], luat=LuatDuAn()) == \
        KetQuaGop("mới") and c.goi == []


def test_thay_gop_giu_ca_hai():
    kq, c = chay({"a": "thay", "b": "gop", "c": "giu_ca_hai"}, [cu("a"), cu("b"), cu("c")], gop_txt=" Câu gộp. ")
    assert kq.noi_dung == "Câu gộp." and kq.xoa == ("a", "b") and [k.id for k in kq.gop_tu] == ["b"]
    nd = c.goi[0]["messages"][0]["content"]
    assert nd.startswith(f"<{THE}>") and '"id": "a"' in nd and '"moi": "mới"' in nd
    kq, _ = chay({"a": "thay"}, [cu("a")])
    assert kq == KetQuaGop("mới", ("a",), ())


def test_ky_uc_dai_ca_khong_bi_agent_thay_hay_gop():
    dai_ca = cu("a")                                          # nguồn dai_ca_sua → nguon_dai_ca True
    agent = cu("b", nguon=AGENT)
    kq, _ = chay({"a": "thay", "b": "thay"}, [dai_ca, agent], moi_dai_ca=False)
    assert kq.xoa == ("b",)
    kq, _ = chay({"a": "gop"}, [dai_ca], gop_txt="gộp", moi_dai_ca=False)
    assert kq == KetQuaGop("mới")
    assert bao_ve(dai_ca, True, "thay") == "thay" and bao_ve(agent, False, "gop") == "gop"


@pytest.mark.parametrize("cau, ten_rieng, luat", [
    ("Phụ thu 50k mỗi khách", False, LuatDuAn()), ("Sửa trong module Fin", False, LuatDuAn(("Fin",))),
    ("Đoàn ông Nam", True, LuatDuAn())])
def test_cau_gop_cham_nghiep_vu_trong_cach_lam_thi_bo_gop(cau, ten_rieng, luat):
    kq, _ = chay({"a": "gop", "b": "thay"}, [cu("a"), cu("b")], gop_txt=cau, ten_rieng=ten_rieng, luat=luat)
    assert kq == KetQuaGop("mới", ("b",), ())


def test_llm_sai_id_ba_lan_thi_giu_nguyen():
    xau = tra_loi({"quyet_dinh": [{"id": "khac", "hanh_dong": "thay"}], "noi_dung_gop": "", "co_ten_rieng": False})
    c = ClientGia(xau, xau, xau)
    assert gop(c, VAI, noi_dung_moi="mới", moi_dai_ca=True, pham_vi=PV, ung_vien=[cu("a")],
               luat=LuatDuAn()) == KetQuaGop("mới") and len(c.goi) == 3


def test_gop_thieu_cau_gop_bi_guardrail():
    xau = tra_loi({"quyet_dinh": [{"id": "a", "hanh_dong": "gop"}], "noi_dung_gop": " ", "co_ten_rieng": False})
    tot = tra_loi({"quyet_dinh": [{"id": "a", "hanh_dong": "gop"}], "noi_dung_gop": "Gộp", "co_ten_rieng": False})
    kq = gop(ClientGia(xau, tot), VAI, noi_dung_moi="mới", moi_dai_ca=True, pham_vi=PV, ung_vien=[cu("a")],
             luat=LuatDuAn())
    assert kq.noi_dung == "Gộp" and kq.xoa == ("a",)


def test_gop_tu_bo_ung_vien_khac_pham_vi_hoac_da_xoa():
    """bs-hpc.10: truyền nhầm bản dự án khác vào cũng không được xoá mềm nó."""
    la = cu("y", pham_vi="/du-an/y/cach-lam")
    da_xoa = cu("z", da_xoa=True)
    kq, c = chay({"a": "thay"}, [cu("a"), la, da_xoa])
    assert kq.xoa == ("a",) and '"id": "y"' not in c.goi[0]["messages"][0]["content"]
    c = ClientGia()
    assert gop(c, VAI, noi_dung_moi="mới", moi_dai_ca=True, pham_vi=PV, ung_vien=[la, da_xoa],
               luat=LuatDuAn()) == KetQuaGop("mới") and c.goi == []


@pytest.mark.parametrize("xau", [
    {"quyet_dinh": "thay hết", "noi_dung_gop": "", "co_ten_rieng": False},
    {"quyet_dinh": [{"hanh_dong": "thay"}], "noi_dung_gop": "", "co_ten_rieng": False},
    {"quyet_dinh": ["a"], "noi_dung_gop": "", "co_ten_rieng": False},
    {"quyet_dinh": [{"id": ["a"], "hanh_dong": "thay"}], "noi_dung_gop": "", "co_ten_rieng": False},
    {"quyet_dinh": [{"id": None, "hanh_dong": "thay"}, {"id": "a", "hanh_dong": "thay"}], "noi_dung_gop": ""},
    {"quyet_dinh": [{"id": "a", "hanh_dong": "gop"}], "noi_dung_gop": 5, "co_ten_rieng": False},
    {"quyet_dinh": [{"id": "a", "hanh_dong": "gop"}], "noi_dung_gop": "Gộp"},
    {"quyet_dinh": None}])
def test_dau_ra_llm_sai_kieu_thi_giu_nguyen(xau):
    c = ClientGia(*(tra_loi(xau) for _ in range(3)))
    assert gop(c, VAI, noi_dung_moi="mới", moi_dai_ca=True, pham_vi=PV, ung_vien=[cu("a")],
               luat=LuatDuAn()) == KetQuaGop("mới") and len(c.goi) == 3
