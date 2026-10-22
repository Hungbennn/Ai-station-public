import pytest

from nho_gia import ClientGia, EmbedderGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.ap_dung import TAC_NHAN
from tram.nho.ke_hoach import lap_ke_hoach
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.nguon import TAC_NHAN_NHO, doc_dau_vao
from tram.nho.nhat_ky import NhatKy
from tram.nho.vong import NguCanhNho, mot_luot
from tram.su_kien.kho import KhoSuKien, SuKien

LUC = "2026-10-13T02:00:00Z"
DL = {"noi_dung": "  Chạy test bằng `php artisan test --filter <Ten>`  ", "nhan": ["test", "php"],
      "giao_id": "g-20261013-0042", "vai": "coder"}


def sk(du_lieu=DL, tac_nhan="tram/nho", du_an="hr-codex"):
    return SuKien(LUC, du_an, None, "nho.agent_ghi", tac_nhan, du_lieu, 900)


def test_agent_ghi_la_nguon_khong_tach_mang_vai_va_nhan():
    dv = doc_dau_vao(sk())
    assert (dv.loai_nguon, dv.tat_dinh, dv.van_ban, dv.ep_nghiep_vu, dv.luc) == (
        "agent", "Chạy test bằng `php artisan test --filter <Ten>`", None, False, LUC)
    assert dv.nhan == ("test", "php") and dv.nguon == {"loai": "agent", "du_an": "hr-codex", "bead_id": None,
                                                       "su_kien_id": 900, "vai": "coder"}
    assert TAC_NHAN_NHO == TAC_NHAN


@pytest.mark.parametrize("tac_nhan", ["tho/B/claude-1", "dai-ca", "tram/api"])
def test_agent_ghi_khong_do_memory_service_ghi_thi_khong_phai_nguon(tac_nhan):
    assert doc_dau_vao(sk(tac_nhan=tac_nhan)) is None


@pytest.mark.parametrize("sua", [{"noi_dung": None}, {"noi_dung": "  "}, {"noi_dung": "x" * 601}, {"noi_dung": 5},
                                 {"nhan": "test"}, {"nhan": ["Test"]}, {"nhan": ["a"] * 9}, {"vai": None},
                                 {"vai": "Coder"}])
def test_agent_ghi_du_lieu_sai_la_su_kien_doc(sua):
    with pytest.raises(ValueError):
        doc_dau_vao(sk({**DL, **sua}))


@pytest.mark.parametrize("noi_dung, nhanh", [("Chạy test bằng php artisan test", "cach-lam"),
                                             ("Phụ thu cuối tuần 50k mỗi khách", "nghiep-vu"),
                                             ("Sửa form trong Modules/Fin", "nghiep-vu")])
def test_luat_cung_quyet_nhanh_khong_goi_llm(tmp_path, noi_dung, nhanh):
    c = ClientGia()
    [b] = lap_ke_hoach(doc_dau_vao(sk({**DL, "noi_dung": noi_dung})), kho=KhoKyUc(tmp_path / "l", so_chieu=16),
                       embedder=EmbedderGia(), client=c, vai_tach=nap_vai("nho-tach"), vai_gop=nap_vai("nho-gop"),
                       luat=LuatDuAn(), luc="2026-10-14T00:00:00Z")
    k = b.ky_uc
    assert c.goi == [] and k.pham_vi == f"/du-an/hr-codex/{nhanh}" and k.nhan == ("test", "php")
    assert (k.nguon_dai_ca, k.quan_trong, k.tao_luc, k.nguon[0]["vai"]) == (False, 0.5, LUC, "coder")


def test_vong_nap_ghi_ky_uc_agent_nhung_khong_thay_ky_uc_dai_ca(tmp_path):
    nd = "Chạy test bằng php artisan test"
    e = EmbedderGia(vector={nd: [1] + [0] * 15})
    nc = NguCanhNho(KhoKyUc(tmp_path / "l", so_chieu=16), e, None, KhoSuKien(tmp_path / "sk.db"),
                    NhatKy(tmp_path / "nk.db"), nap_vai("nho-tach"), nap_vai("nho-gop"), luat_cua=lambda t: LuatDuAn())
    nc.kho.them(ky_uc("m-dc", "/du-an/hr-codex/cach-lam", vector=e.embed([nd])[0], noi_dung="Đại ca: test artisan"))
    nc.client = ClientGia(tra_loi({"quyet_dinh": [{"id": "m-dc", "hanh_dong": "thay"}], "noi_dung_gop": "",
                                   "co_ten_rieng": False}))
    nc.kho_sk.ghi("hr-codex", "nho.agent_ghi", {**DL, "noi_dung": nd}, tac_nhan="tram/nho")
    bc = mot_luot(nc)
    assert (bc.su_kien, bc.ky_uc_moi, bc.loi) == (1, 1, None)
    assert nc.kho.dem("da_xoa = false") == 2                       # #18: agent không thay ký ức của Đại ca
    [g] = nc.kho_sk.gan_day("hr-codex", "nho.ghi", 9)
    assert g.du_lieu["pham_vi"] == "/du-an/hr-codex/cach-lam" and g.du_lieu["nguon"][0]["loai"] == "agent"
