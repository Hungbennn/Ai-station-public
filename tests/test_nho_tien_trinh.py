import threading
from datetime import datetime, timezone

import pytest

from nho_gia import ClientGia, EmbedderGia, ky_uc, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.nho.dich_vu import DichVuNho
from tram.nho.khoa import khoa_dich_vu, thu_muc_nho
from tram.nho.kho import KhoKyUc
from tram.nho.luat import LuatDuAn
from tram.nho.nhat_ky import NhatKy
from tram.nho.nho_lai import BoDemDung
from tram.nho.tien_trinh import BaoTri, bao_tri_neu_den_han, chay_dich_vu, tao_ngu_canh_that, vong_nap
from tram.nho.vong import NguCanhNho
from tram.su_kien.kho import KhoSuKien

TRUA_VN = datetime(2026, 10, 13, 5, 0, tzinfo=timezone.utc)      # 12:00 giờ VN
DEM_VN = datetime(2026, 10, 13, 21, 30, tzinfo=timezone.utc)     # 04:30 giờ VN ngày 14


def mt(thu):
    e = EmbedderGia()
    kho, kho_sk = KhoKyUc(thu / "lancedb", so_chieu=e.so_chieu), KhoSuKien(thu.parent / "sk.db")
    nc = NguCanhNho(kho, e, ClientGia(), kho_sk, NhatKy(thu / "nhat-ky.db"), nap_vai("nho-tach"),
                    nap_vai("nho-gop"), luat_cua=lambda t: LuatDuAn())
    return nc, DichVuNho(kho, e, lambda: KhoSuKien(thu.parent / "sk.db"), BoDemDung(), "tk")


def test_bao_tri_mot_lan_moi_ngay_sau_3_gio_vn(tmp_path):
    nc, dv = mt(tmp_path / "nho")
    nc.kho.them(ky_uc("m-1", vector=nc.embedder.embed(["1"])[0]))
    bt, dich = BaoTri(), tmp_path / "sao-luu"
    assert not bao_tri_neu_den_han(nc, dv, bt, TRUA_VN.replace(hour=19), thu_muc=tmp_path / "nho", dich=dich)
    assert bao_tri_neu_den_han(nc, dv, bt, DEM_VN, thu_muc=tmp_path / "nho", dich=dich)
    assert not bao_tri_neu_den_han(nc, dv, bt, DEM_VN.replace(hour=23), thu_muc=tmp_path / "nho", dich=dich)
    assert [p.name for p in dich.iterdir()] == ["nho-20261013-213000"] and nc.kho.dem() == 1


def test_vong_nap_lam_luot_va_song_sot_khi_loi(tmp_path, capsys):
    nc, dv = mt(tmp_path / "nho")
    nc.kho_sk.ghi("hr", "cot.tra_ve", {"gop_y": "x"}, bead_id="hr-1")
    nc.client = ClientGia(RuntimeError("API sập"), tra_loi({"ky_uc": []}))
    dung, so_lan = threading.Event(), []

    def dong_ho():
        so_lan.append(1)
        if len(so_lan) == 2:
            dung.set()
        return TRUA_VN

    vong_nap(nc, dv, dung=dung, thu_muc=tmp_path / "nho", dich=tmp_path / "sl", chu_ky=0, dong_ho=dong_ho)
    assert "lượt nạp lỗi: RuntimeError: API sập" in capsys.readouterr().err
    assert nc.nhat_ky.moc() == 1 and len(so_lan) == 2


def test_chay_dich_vu_khoa_token_va_http_localhost(tmp_path, tram_home_tam):
    goi, (nc, dv) = [], mt(thu_muc_nho())
    nc.embedder.kiem = lambda: goi.append(threading.current_thread().name)   # Q6: luồng chính kiểm TRƯỚC khi mở HTTP
    assert chay_dich_vu(tao=lambda: (nc, dv), chay_http=lambda app, **kw: goi.append(kw)) == 0
    assert goi[0] == "MainThread" and [g for g in goi if isinstance(g, dict)] == [
        {"host": "127.0.0.1", "port": 7710, "log_level": "warning", "server_header": False}]
    assert chay_dich_vu(tao=lambda: None, chay_http=lambda *a, **k: pytest.fail("không được chạy")) == 0
    with khoa_dich_vu(thu_muc_nho()):
        assert chay_dich_vu(tao=lambda: pytest.fail("không được tạo"), chay_http=None) == 0


def test_tao_ngu_canh_that_khong_goi_mang(monkeypatch, tram_home_tam):
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: "tk")         # không đọc Keychain thật
    monkeypatch.setenv("ANTHROPIC_API_KEY", "khoa-test")
    nc, dv = tao_ngu_canh_that()
    assert dv.token == "tk" and nc.embedder.so_chieu == 1024 and (tram_home_tam / "nho" / "lancedb").is_dir()
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: None)
    assert tao_ngu_canh_that() is None


def test_khoi_dong_loi_thi_in_ly_do_thoat_0_va_embedder_chet_van_mo_http(tram_home_tam, capsys):
    def hong():
        raise ValueError("Kho ký ức 16 chiều, embedder 1024 chiều")
    assert chay_dich_vu(tao=hong, chay_http=lambda *a, **k: pytest.fail("không được chạy")) == 0
    assert "không khởi động được: ValueError: Kho ký ức 16 chiều" in capsys.readouterr().out
    nc, dv = mt(thu_muc_nho())
    nc.embedder.loi_kiem, goi = True, []
    assert chay_dich_vu(tao=lambda: (nc, dv), chay_http=lambda app, **kw: goi.append(kw)) == 0
    assert len(goi) == 1 and "embedder chưa sẵn sàng" in capsys.readouterr().err
