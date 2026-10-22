"""Gói ngữ cảnh lát 4c (spec 4 §11): lớp 5 từ recall theo vùng cấp của phiếu, luồng gitnexus ở lớp 1, cắt sau
lớp 4; nối qua `BoGiaoViec.p4c` — mặc định tắt."""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from bead_gia import bead
from giao_viec_gia import bug, dung
from tram.cham_cot.prompt import nap_vai
from tram.giao_viec.gh import GhCli
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.goi import DauVaoGoi, GoiQuaLon, Lop4, dung_goi
from tram.giao_viec.lop_5 import Lop5
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c, luong_lien_quan, tao_phu_thuoc_4c

B = bead("hr-1", title="Sửa cắt UTF-8", issue_type="bug", acceptance_criteria="- Tên kết thúc 'ỷ'")
L5 = Lop5(ky_uc=(("/du-an/hr-codex/cach-lam", "Dùng mb_substr cho chuỗi UTF-8"),))
LUONG = "<du_lieu_khong_tin_cay>\n- Tóm tắt hoàn tiền: src/tom_tat.py\n</du_lieu_khong_tin_cay>"


def dv(**kw):
    goc = {"tai_lieu": (("AGENTS.md", "# Quy ước"),), "vai": ("coder", *nap_vai("coder")), "bead": B,
           "buoc": "code", "tieu_chi": ("Tên kết thúc 'ỷ'",), "lenh_kiem": ("sh kiem.sh",), "lop_4": Lop4(),
           "lop_5": L5, "luong": LUONG}
    return DauVaoGoi(**{**goc, **kw})


def test_luong_o_cuoi_lop_1_va_lop_5_o_cuoi_goi():
    g = dung_goi(dv())
    lop = [g.index(f"## Lớp {i}") for i in range(1, 6)]
    assert lop == sorted(lop) and lop[0] < g.index("### Luồng liên quan (gitnexus)") < lop[1]
    assert g.index("Dùng mb_substr") > lop[4] and g.count("<du_lieu_khong_tin_cay>") == 5


def test_cat_lop_4_truoc_roi_moi_bo_phan_4c():
    l4 = Lop4(diff_qc=(("a.py", "A" * 3000),))
    du = dung_goi(dv(lop_4=l4))
    cat_l4 = dung_goi(dv(lop_4=l4), toi_da_ky_tu=len(du) - 100)
    assert "A" * 3000 not in cat_l4 and "Dùng mb_substr" in cat_l4 and "Luồng liên quan" in cat_l4
    khong_diff = dung_goi(dv())
    bo_4c = dung_goi(dv(), toi_da_ky_tu=len(khong_diff) - 50)
    assert "Dùng mb_substr" not in bo_4c and "Luồng liên quan" not in bo_4c and "đã bỏ vì gói vượt" in bo_4c
    with pytest.raises(GoiQuaLon):
        dung_goi(dv(), toi_da_ky_tu=len(bo_4c) - 1)


class Nho:
    def __init__(self):
        self.goi = []

    def __call__(self, truy_van, vung):
        self.goi.append(vung)
        return [{"id": "m1", "noi_dung": "Dùng mb_substr cho chuỗi UTF-8", "pham_vi": "/du-an/hr-codex/cach-lam"}]


class Gn:
    def luong(self, truy_van, repo):
        assert repo == "hr-interview-copilot" and truy_van.startswith("Sửa cắt UTF-8")
        return [("Tóm tắt hoàn tiền", ("src/tom_tat.py",))]


def test_chon_dung_lop_5_theo_vung_cap_cua_phieu_va_luong(tmp_path):
    t = dung(tmp_path, bug())
    n = Nho()
    t.bo.p4c = PhuThuoc4c(nho_lai=n, gitnexus=Gn())
    t.bo.cac_du_an = lambda: [replace(t.da, gitnexus_repo="hr-interview-copilot")]
    fetch(t.k.kho)
    p = t.bo.chon("B/claude-1", None)
    assert n.goi == [["/du-an/hr-codex", "/vai/coder", "/chung"]]
    g = p.goi_ngu_canh
    assert g.index("Dùng mb_substr") > g.index("## Lớp 5") and "Tóm tắt hoàn tiền: src/tom_tat.py" in g
    assert g.count("<du_lieu_khong_tin_cay>") == g.count("</du_lieu_khong_tin_cay>")
    from test_de_xuat_spec import DA as DA_SPEC, F, dx
    from tram.giao_viec.chon import UngVien
    from tram.giao_viec.de_xuat_spec import dung_de_xuat_spec
    k, _, _ = dx(tmp_path / "spec")
    ps = dung_de_xuat_spec(UngVien(DA_SPEC, F, "spec", False, frozenset()), [], k.kho,
                          p4c=PhuThuoc4c(nho_lai=n), theo_id={F.id: F})
    assert n.goi[-1] == ["/du-an/hr-codex", "/vai/spec", "/chung"]
    assert ps is not None and "Dùng mb_substr" in ps.goi_ngu_canh


def test_mac_dinh_tat_khong_goi_ra_ngoai(tmp_path):
    t = dung(tmp_path, bug())
    fetch(t.k.kho)
    g = t.bo.chon("B/claude-1", None).goi_ngu_canh
    assert "memory chưa nối" in g and "Luồng liên quan" not in g


def test_luong_loi_hoac_chua_cau_hinh_thi_rong():
    from tram.giao_viec.gitnexus import LoiGitnexus
    da = SimpleNamespace(gitnexus_repo=None)
    assert luong_lien_quan(Gn(), da, B) == "" and luong_lien_quan(None, da, B) == ""
    hong = SimpleNamespace(luong=lambda *a: (_ for _ in ()).throw(LoiGitnexus("x")))
    assert luong_lien_quan(hong, SimpleNamespace(gitnexus_repo="r"), B) == ""


def test_tao_phu_thuoc_4c_chi_bat_khi_duoc_bat_va_co_lenh():
    khong_token = lambda *a, **k: SimpleNamespace(returncode=44, stdout="")
    p = tao_phu_thuoc_4c(github=False, gitnexus=True, which=lambda x: None, chay=khong_token)
    assert (p.gh, p.gitnexus, p.nho_lai) == (None, None, None)
    p = tao_phu_thuoc_4c(github=True, gitnexus=False, which=lambda x: f"/bin/{x}", chay=khong_token)
    assert isinstance(p.gh, GhCli) and p.gitnexus is None
