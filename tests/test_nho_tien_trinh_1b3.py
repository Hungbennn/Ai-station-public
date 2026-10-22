"""1b-3: thăng cấp chạy trong bảo trì đêm; `/ghi` và vòng nạp tuần tự qua `khoa_gop`; dựng dịch vụ thật đủ trường."""
import threading
from dataclasses import replace
from datetime import datetime, timezone

import anthropic
import httpx2

from nho_gia import ClientGia, EmbedderGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.dich_vu import DichVuNho
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.mo_hinh import BuocGhi
from tram.nho.nhat_ky import NhatKy
from tram.nho.nho_lai import BoDemDung
from tram.nho.thang_cap import id_thang_cap
from tram.nho.tien_trinh import BaoTri, bao_tri_neu_den_han, tao_ngu_canh_that
from tram.nho.vong import NguCanhNho, mot_luot
from tram.su_kien.kho import KhoSuKien

DEM_VN = datetime(2026, 10, 13, 21, 30, tzinfo=timezone.utc)     # 04:30 giờ VN ngày 14
V1 = (1.0,) + (0.0,) * 15
SOAN = tra_loi({"noi_dung": "Chạy toàn bộ test trước khi bàn giao.", "nhan": [], "co_ten_rieng": False})


def mt(thu, *, thang_cap=True):
    e = EmbedderGia()
    kho, kho_sk = KhoKyUc(thu / "lancedb", so_chieu=16), KhoSuKien(thu.parent / "sk.db")
    nc = NguCanhNho(kho, e, ClientGia(), kho_sk, NhatKy(thu / "nhat-ky.db"), nap_vai("nho-tach"), nap_vai("nho-gop"),
                    luat_cua=lambda t: LuatDuAn(), vai_thang_cap=nap_vai("nho-thang-cap") if thang_cap else None)
    return nc, DichVuNho(kho, e, lambda: KhoSuKien(thu.parent / "sk.db"), BoDemDung(), "tk")


def hai_ban(nc):
    for id, d in (("m-a", "hr-codex"), ("m-b", "khac")):
        nc.kho.them(ky_uc(id, f"/du-an/{d}/cach-lam", vector=V1))


def test_bao_tri_dem_thang_cap_truoc_khi_sao_luu(tmp_path, monkeypatch):
    monkeypatch.setattr("tram.nho.vong_thang_cap.liet_ke_du_an", lambda: ["hr-codex", "khac"])
    nc, dv = mt(tmp_path / "nho")
    hai_ban(nc)
    nc.client = ClientGia(SOAN)
    assert bao_tri_neu_den_han(nc, dv, BaoTri(), DEM_VN, thu_muc=tmp_path / "nho", dich=tmp_path / "sl")
    assert nc.kho.lay([id_thang_cap("m-a|m-b")])[id_thang_cap("m-a|m-b")].pham_vi == "/chung"
    ban = next((tmp_path / "sl").iterdir())
    assert KhoKyUc(ban / "lancedb", so_chieu=16).dem() == 3                       # bản chụp có ký ức thăng cấp


def test_thang_cap_loi_van_sao_luu_va_tat_thi_khong_goi_llm(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("tram.nho.vong_thang_cap.liet_ke_du_an", lambda: ["hr-codex", "khac"])
    nc, dv = mt(tmp_path / "nho")
    hai_ban(nc)
    nc.client = ClientGia(anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com")))
    bt = BaoTri()
    assert bao_tri_neu_den_han(nc, dv, bt, DEM_VN, thu_muc=tmp_path / "nho", dich=tmp_path / "sl")
    assert "thăng cấp: " in capsys.readouterr().err and bt.ngay_cuoi is not None and any((tmp_path / "sl").iterdir())
    nc2, dv2 = mt(tmp_path / "nho2", thang_cap=False)
    hai_ban(nc2)
    assert bao_tri_neu_den_han(nc2, dv2, BaoTri(), DEM_VN, thu_muc=tmp_path / "nho2", dich=tmp_path / "sl2")
    assert nc2.client.goi == [] and nc2.kho.dem() == 2


def test_vong_nap_cho_khoa_gop_cua_ghi_tay(tmp_path):
    nc, _ = mt(tmp_path / "nho")
    nc.kho_sk.ghi("hr", "cot.dai_ca_sua", {"tieu_de": "X", "cot_he": "a", "cot_moi": "b", "ly_do_he": "c"},
                  bead_id="hr-1")
    xong = threading.Event()
    with nc.kho.khoa_gop:
        t = threading.Thread(target=lambda: (mot_luot(nc), xong.set()))
        t.start()
        assert not xong.wait(0.3) and nc.kho.dem() == 0                       # đang chờ `/ghi` gộp xong
    t.join(10)
    assert xong.is_set() and nc.kho.dem() == 1


def test_lam_tiep_thao_tac_do_doc_lai_trang_thai_duoi_khoa(tmp_path, monkeypatch):
    nc, _ = mt(tmp_path / "nho")
    k = ky_uc("m-g", "/chung", vector=V1)
    tt = nc.nhat_ky.bat_dau("ghi:ma-ghi-0001", 0, {"du_an": "_tram", "bead_id": None,
                                                   "buoc": [BuocGhi(k).sang_dict()]})
    nc.nhat_ky.hoan_tat(tt.ma, 0)                                     # `/ghi` vừa làm xong ở luồng HTTP
    monkeypatch.setattr(nc.nhat_ky, "dang_do", lambda: [replace(tt, trang_thai="dang")])   # danh sách cũ
    mot_luot(nc)
    assert nc.kho.dem() == 0 and nc.kho_sk.gan_day("_tram", "nho.ghi", 9) == []


def test_loi_embedder_khong_gan_vao_thao_tac_ghi_tay(tmp_path):
    nc, _ = mt(tmp_path / "nho")
    nc.nhat_ky.bat_dau("ghi:ma-ghi-0001", 0, {"du_an": "_tram", "bead_id": None, "buoc": []})
    nc.kho_sk.ghi("hr", "cot.tra_ve", {"gop_y": "x"}, bead_id="hr-7")
    nc.embedder.loi_kiem = True
    mot_luot(nc)
    assert nc.kho_sk.gan_day("_tram", "nho.loi_embedder", 9) == []
    assert nc.kho_sk.gan_day("hr", "nho.loi_embedder", 9)[0].bead_id == "hr-7"


def test_tao_ngu_canh_that_noi_thang_cap_va_ghi_tay(monkeypatch, tram_home_tam):
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: "tk")         # không đọc Keychain thật
    monkeypatch.setenv("ANTHROPIC_API_KEY", "khoa-test")
    nc, dv = tao_ngu_canh_that()
    assert nc.vai_thang_cap == nap_vai("nho-thang-cap") and dv.vai_gop == nap_vai("nho-gop")
    assert dv.client is nc.client and isinstance(dv.mo_nhat_ky(), NhatKy)


def test_bao_tri_cho_ghi_tay_xong_truoc_chup(tmp_path, monkeypatch):
    nc, dv = mt(tmp_path / "nho", thang_cap=False)
    da_chup = threading.Event()
    monkeypatch.setattr("tram.nho.bao_tri.sao_luu_nho", lambda *a, **kw: da_chup.set())
    with nc.kho.khoa_gop:
        t = threading.Thread(target=lambda: bao_tri_neu_den_han(
            nc, dv, BaoTri(), DEM_VN, thu_muc=tmp_path / "nho", dich=tmp_path / "ban"))
        t.start()
        assert not da_chup.wait(0.2)
    t.join(5)
    assert da_chup.is_set() and not t.is_alive()
