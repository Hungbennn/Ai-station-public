"""Lỗi hệ của vòng nạp (G9, G10, Q1): embedder chết, Claude API lỗi, cấu hình dự án hỏng."""
import anthropic
import httpx2
import pytest
import yaml

from nho_gia import ClientGia, EmbedderGia, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.nhat_ky import NhatKy
from tram.nho.vong import NguCanhNho, dang_loi, mot_luot
from tram.su_kien.kho import KhoSuKien

def tach(noi_dung):
    return tra_loi({"ky_uc": [{"noi_dung": noi_dung, "nhanh": "cach-lam", "nhan": [], "quan_trong": 0.5,
                               "co_ten_rieng": False}]})


HAI = (tach("Bàn giao kèm test biên."), tach("Ghi log khi gọi API ngoài."))


def api_sap():
    return anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com"))


@pytest.fixture
def nc(tmp_path):
    e = EmbedderGia()
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr-codex", "quet.xong", {})
    k.ghi("hr-codex", "cot.tra_ve", {"gop_y": "Thiếu test biên"}, bead_id="hr-7")
    k.ghi("hr-codex", "cot.tra_ve", {"gop_y": "Thiếu log"}, bead_id="hr-8")
    return NguCanhNho(kho=KhoKyUc(tmp_path / "lancedb", so_chieu=e.so_chieu), embedder=e, client=ClientGia(),
                      kho_sk=k, nhat_ky=NhatKy(tmp_path / "nk.db"), vai_tach=nap_vai("nho-tach"),
                      vai_gop=nap_vai("nho-gop"), luat_cua=lambda ten: LuatDuAn())


def su_kien(nc, loai, du_an="hr-codex"):
    return nc.kho_sk.gan_day(du_an, loai, 99)


def test_embedder_chet_bao_mot_lan_vao_du_an_cua_su_kien_ket_roi_phuc_hoi(nc):
    nc.embedder.loi_kiem = True
    assert mot_luot(nc).loi.startswith("embedder") and mot_luot(nc).loi
    assert nc.nhat_ky.moc() == 0 and nc.kho.dem() == 0 and nc.client.goi == []
    [ev] = su_kien(nc, "nho.loi_embedder")
    assert (ev.bead_id, ev.du_lieu["su_kien_id"], ev.tac_nhan) == ("hr-7", 2, "tram/nho")
    assert su_kien(nc, "nho.loi_embedder", "_tram") == [] and dang_loi(nc.kho_sk, "hr-codex", "embedder")
    nc.embedder.loi_kiem, nc.client = False, ClientGia(*HAI)
    assert mot_luot(nc).su_kien == 2 and dang_loi(nc.kho_sk, "hr-codex", "embedder") is None
    [ph] = su_kien(nc, "nho.phuc_hoi")
    assert ph.du_lieu == {"loai": "embedder"} and ph.bead_id == "hr-7"


def test_embedder_loi_giua_luot_su_kien_truoc_giu_su_kien_sau_chua_ghi(nc):
    nc.embedder.loi_tu_lan = 2                       # embed của hr-7 OK, của hr-8 lỗi
    nc.client = ClientGia(*HAI)
    bc = mot_luot(nc)
    assert bc.su_kien == 1 and bc.loi and nc.kho.dem() == 1 and nc.nhat_ky.moc() == 2
    assert su_kien(nc, "nho.loi_embedder")[0].bead_id == "hr-8" and nc.nhat_ky.dang_do() == []


def test_loi_api_claude_bao_mot_lan_moc_khong_tien_khong_ghi_kho(nc):
    nc.client = ClientGia(api_sap())
    bc = mot_luot(nc)
    assert bc.loi == "llm: APIConnectionError: Connection error." and (bc.su_kien, bc.bo) == (0, 0)
    assert nc.nhat_ky.moc() == 1 and nc.kho.dem() == 0 and su_kien(nc, "nho.loi_tach") == []
    [ev] = su_kien(nc, "nho.loi_llm")
    assert (ev.bead_id, ev.du_lieu["su_kien_id"], ev.tac_nhan) == ("hr-7", 2, "tram/nho")
    nc.client = ClientGia(api_sap())
    assert mot_luot(nc).loi and len(su_kien(nc, "nho.loi_llm")) == 1          # đợt lỗi tiếp: không ghi lần hai


def test_loi_api_het_thi_phuc_hoi_mot_lan(nc):
    nc.client = ClientGia(api_sap())
    mot_luot(nc)
    nc.client = ClientGia(*HAI)
    assert mot_luot(nc).su_kien == 2 and nc.nhat_ky.moc() == 4          # 4 = chính nho.loi_llm (không phải nguồn)
    [ph] = su_kien(nc, "nho.phuc_hoi")
    assert ph.du_lieu == {"loai": "llm"} and ph.bead_id == "hr-7" and dang_loi(nc.kho_sk, "hr-codex", "llm") is None


def test_cau_hinh_du_an_hong_thi_bo_su_kien_khong_ket(nc):
    def luat(ten):
        if ten == "hong":
            raise yaml.YAMLError("mapping values are not allowed here")
        return LuatDuAn()
    nc.luat_cua = luat
    nc.kho_sk.ghi("hong", "cot.tra_ve", {"gop_y": "x"}, bead_id="ho-1")
    nc.client = ClientGia(*HAI)
    bc = mot_luot(nc)
    assert (bc.su_kien, bc.bo, bc.loi) == (2, 1, None) and nc.nhat_ky.moc() == 4
    [ev] = su_kien(nc, "nho.loi_tach", "hong")
    assert ev.du_lieu == {"su_kien_id": 4, "loi": "YAMLError: mapping values are not allowed here"}


def test_du_lieu_sai_kieu_la_su_kien_doc_bo_va_moc_tien(nc):
    """bs-hpc.12: `cau_hoi: 5` làm đọc đầu vào ném TypeError — không được kẹt vòng nạp."""
    nc.kho_sk.ghi("hr-codex", "cot.da_chot", {"cau_hoi": 5, "tra_loi": ["a"]}, bead_id="hr-9")
    nc.client = ClientGia(*HAI)
    bc = mot_luot(nc)
    assert (bc.su_kien, bc.bo, bc.loi) == (2, 1, None) and nc.nhat_ky.moc() == 4
    [ev] = su_kien(nc, "nho.loi_tach")
    assert ev.bead_id == "hr-9" and ev.du_lieu["su_kien_id"] == 4 and ev.du_lieu["loi"].startswith("TypeError")


def test_embedder_chet_va_co_su_kien_doc_van_bao_loi_binh_thuong(nc):
    nc.kho_sk.ghi("hr-codex", "cot.da_chot", {"cau_hoi": 5, "tra_loi": ["a"]}, bead_id="hr-9")
    nc.embedder.loi_kiem = True
    assert mot_luot(nc).loi.startswith("embedder") and len(su_kien(nc, "nho.loi_embedder")) == 1


def test_dang_loi_khong_bi_che_boi_nhieu_phuc_hoi_loai_khac(nc):
    nc.kho_sk.ghi("hr-codex", "nho.loi_llm", {"su_kien_id": 2, "loi": "x"}, bead_id="hr-7")
    nc.kho_sk.ghi("hr-codex", "nho.phuc_hoi", {"loai": "llm"}, bead_id="hr-7")
    for _ in range(25):
        nc.kho_sk.ghi("hr-codex", "nho.phuc_hoi", {"loai": "embedder"}, bead_id="hr-7")
    assert dang_loi(nc.kho_sk, "hr-codex", "llm") is None
