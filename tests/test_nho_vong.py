from datetime import datetime, timezone

import pytest

from nho_gia import ClientGia, EmbedderGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.ap_dung import luu_ke_hoach
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.mo_hinh import BuocGhi, id_ky_uc
from tram.nho.nhat_ky import NhatKy
from tram.nho.nho_lai import nho_lai
from tram.nho.vong import NguCanhNho, mot_luot
from tram.su_kien.kho import KhoSuKien

CHOT = {"ky_uc": [{"noi_dung": "HR Codex: hoa hồng sale tính trên giá sau giảm giá (Đại ca chốt 13/10).",
                   "nhanh": "cach-lam", "nhan": ["hoa-hong"], "quan_trong": 0.9, "co_ten_rieng": False}]}
TRA_VE = {"ky_uc": [{"noi_dung": "Bàn giao phải kèm test biên cho tên tiếng Việt có dấu.", "nhanh": "cach-lam",
                     "nhan": [], "quan_trong": 0.5, "co_ten_rieng": False}]}


LUC_SK = "2026-10-01T00:00:00Z"                     # giờ ghi sự kiện nguồn (cố định trong test)


@pytest.fixture
def nc(tmp_path, monkeypatch):
    monkeypatch.setattr("tram.su_kien.kho.bay_gio", lambda: LUC_SK)
    e = EmbedderGia()
    return NguCanhNho(kho=KhoKyUc(tmp_path / "lancedb", so_chieu=e.so_chieu), embedder=e, client=ClientGia(),
                      kho_sk=KhoSuKien(tmp_path / "sk.db"), nhat_ky=NhatKy(tmp_path / "nk.db"),
                      vai_tach=nap_vai("nho-tach"), vai_gop=nap_vai("nho-gop"), luat_cua=lambda ten: LuatDuAn(),
                      luc=lambda: "2026-10-13T02:00:00Z")


def su_kien_mau(k: KhoSuKien):
    k.ghi("hr-codex", "quet.xong", {"da_cham": 1})
    k.ghi("hr-codex", "cot.dai_ca_sua", {"tieu_de": "Xuất PDF", "cot_he": "cot:ai-lam", "cot_moi": "cot:can-chot",
                                          "ly_do_he": "Rõ", "da_ghi": True}, bead_id="hr-3", tac_nhan="dai-ca")
    k.ghi("hr-codex", "cot.da_chot", {"decision_id": "hr-d1", "cau_hoi": ["Hoa hồng tính trên giá nào?"],
                                       "tra_loi": ["Giá sau giảm giá"], "ma_thao_tac": "m1"}, bead_id="hr-12")
    k.ghi("_tram", "estop.bat", {"ly_do": "x"})
    k.ghi("hr-codex", "cot.tra_ve", {"gop_y": "Thiếu test biên", "ma_thao_tac": "m2"}, bead_id="hr-7")


def dem(nc, loai, du_an="hr-codex"):
    return len(nc.kho_sk.gan_day(du_an, loai, 99))


def test_vi_du_dau_cuoi_da_chot_vao_nghiep_vu_va_recall_duoc(nc):
    su_kien_mau(nc.kho_sk)
    nc.client = ClientGia(tra_loi(CHOT), tra_loi(TRA_VE))
    bc = mot_luot(nc)
    assert (bc.su_kien, bc.ky_uc_moi, bc.bo, bc.loi) == (3, 3, 0, None)
    assert nc.nhat_ky.moc() == 5 and dem(nc, "nho.ghi") == 3          # 5 = cot.tra_ve; nho.ghi đọc ở lượt sau
    assert nc.kho.dem("pham_vi = '/du-an/hr-codex/nghiep-vu'") == 1
    ds = nc.kho.lay([id_ky_uc(i, 1, 0) for i in (2, 3, 5)]).values()
    assert {(k.tao_luc, k.hieu_luc_tu) for k in ds} == {(LUC_SK, LUC_SK)}   # giờ sự kiện nguồn, không phải giờ nạp
    kq = nho_lai(nc.kho, nc.embedder, CHOT["ky_uc"][0]["noi_dung"], ["/du-an/hr-codex", "/vai/cham-cot", "/chung"],
                 bay_gio=datetime(2026, 10, 20, tzinfo=timezone.utc))
    assert kq[0].noi_dung.startswith("HR Codex: hoa hồng") and len(kq) == 3
    assert mot_luot(nc).su_kien == 0 and nc.kho.dem() == 3                 # lượt sau: không lặp


def test_loi_tach_bo_su_kien_moc_tien(nc):
    nc.kho_sk.ghi("hr-codex", "cot.tra_ve", {"gop_y": "x"}, bead_id="hr-7")
    nc.kho_sk.ghi("hr-codex", "cot.tra_ve", {"gop_y": "y"}, bead_id="hr-8")
    xau = tra_loi({"ky_uc": "x"})
    nc.client = ClientGia(xau, xau, xau, tra_loi(TRA_VE))
    bc = mot_luot(nc)
    assert (bc.bo, bc.su_kien) == (1, 1) and nc.nhat_ky.moc() == 2
    ev = nc.kho_sk.gan_day("hr-codex", "nho.loi_tach", 1)[0]
    assert ev.du_lieu["su_kien_id"] == 1 and ev.bead_id == "hr-7" and nc.nhat_ky.lay("1:1").trang_thai == "bo"


def test_doi_soat_thao_tac_do_dau_luot(nc):
    nc.kho_sk.ghi("hr-codex", "cot.tra_ve", {"gop_y": "x"}, bead_id="hr-7")
    k = ky_uc("m-do", "/du-an/hr-codex/cach-lam", vector=nc.embedder.embed(["a"])[0])
    luu_ke_hoach(nc.nhat_ky, su_kien_id=1, phien_ban=1, du_an="hr-codex", bead_id="hr-7", buoc=[BuocGhi(k)])
    bc = mot_luot(nc)                                # không gọi LLM lại cho sự kiện 1
    assert bc.ky_uc_moi == 1 and nc.client.goi == [] and nc.kho.lay(["m-do"])
    assert nc.nhat_ky.lay("1:1").trang_thai == "xong" and nc.nhat_ky.moc() == nc.kho_sk.id_moi_nhat()


def test_gioi_han_moi_luot(nc):
    for i in range(3):
        nc.kho_sk.ghi("hr-codex", "quet.xong", {})
    mot_luot(nc, gioi_han=2)
    assert nc.nhat_ky.moc() == 2
    mot_luot(nc, gioi_han=2)
    assert nc.nhat_ky.moc() == 3
