from nho_gia import ClientGia, EmbedderGia, tra_loi
from tram.cham_cot.prompt import nap_vai
from tram.cli import main, tao_parser
from tram.nho.do_tre import do_tre, sinh_kho
from tram.nho.khach import LoiNhoKhach
from tram.nho.khoa import khoa_dich_vu
from tram.nho.lenh_kho import dat_moc_hien_tai
from tram.nho.luat import LuatDuAn
from tram.nho.nhat_ky import NhatKy
from tram.nho.thu import chay_thu
from tram.su_kien.kho import KhoSuKien


def test_dang_ky_lenh_nho():
    p = tao_parser()
    for argv in (["nho", "chay"], ["nho", "tim", "q", "--du-an", "hr"], ["nho", "xoa", "m-1"], ["nho", "thu"],
                 ["nho", "khoi-phuc", "/x"], ["nho", "do-tre", "--so-ban", "10"], ["nho", "dat-moc", "--hien-tai"],
                 ["nho", "tim", "q", "--vung-cap", '["/"]']):
        assert callable(p.parse_args(argv).ham)
    assert p.parse_args(["nho", "chay"]).cong == 7710 and p.parse_args(["nho", "tim", "q", "--du-an", "x"]).vai == \
        "dieu-phoi"


def test_tim_va_xoa_qua_http(monkeypatch, capsys):
    goi = []
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: "tk")
    monkeypatch.setattr("tram.nho.khach.nho_lai_http", lambda q, v, **kw: goi.append((q, v, kw)) or
                        [{"id": "m-1", "noi_dung": "A", "pham_vi": "/chung"}])
    assert main(["nho", "tim", "hoa hồng", "--du-an", "hr-codex"]) == 0
    assert goi[0][:2] == ("hoa hồng", ["/du-an/hr-codex", "/vai/dieu-phoi", "/chung"]) and goi[0][2]["token"] == "tk"
    monkeypatch.setattr("tram.nho.khach.goi_nho", lambda d, t, **kw: {"da_xoa": True} if d == "/xoa" else {})
    assert main(["nho", "xoa", "m-1"]) == 0
    assert "- [/chung] A  (m-1)" in capsys.readouterr().out


def test_tim_vung_cap_tho_gui_nguyen_van(monkeypatch, capsys):
    goi = []
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: "tk")
    monkeypatch.setattr("tram.nho.khach.nho_lai_http", lambda q, v, **kw: goi.append(v) or [])
    assert main(["nho", "tim", "q", "--vung-cap", '["/", "/du-an/hr"]']) == 0 and goi == [["/", "/du-an/hr"]]
    assert main(["nho", "tim", "q", "--vung-cap", "khong-phai-json"]) == 1 and len(goi) == 1
    assert "phải là JSON" in capsys.readouterr().err


def test_dat_moc_hien_tai_chi_khi_dich_vu_dung(tmp_path):
    k, thu = KhoSuKien(tmp_path / "sk.db"), tmp_path / "nho"
    for i in range(3):
        k.ghi("hr", "cot.tra_ve", {"gop_y": f"x{i}"}, bead_id="hr-1")
    with khoa_dich_vu(thu):
        assert dat_moc_hien_tai(thu, k) is None and not (thu / "nhat-ky.db").exists()
    assert dat_moc_hien_tai(thu, k) == 3 and NhatKy(thu / "nhat-ky.db").moc() == 3
    nk = NhatKy(thu / "nhat-ky.db")
    nk.dat_moc(9)
    nk.close()
    assert dat_moc_hien_tai(thu, k) == 9                                  # mốc không lùi


def test_khong_token_hoac_service_tat_thi_ma_1(monkeypatch):
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: None)
    assert main(["nho", "tim", "q", "--du-an", "hr"]) == 1
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: "tk")

    def tat(*a, **kw):
        raise LoiNhoKhach("không gọi được memory service: ConnectionRefusedError")
    monkeypatch.setattr("tram.nho.khach.goi_nho", tat)
    assert main(["nho", "xoa", "m-1"]) == 1


def test_khoi_phuc_can_dong_y(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda *a: "khong")
    assert main(["nho", "khoi-phuc", "/khong-co"]) == 1


def test_chay_thu_khong_ghi_bao_pham_vi_va_luat_cung(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "cot.dai_ca_sua", {"tieu_de": "Sửa module Fin", "cot_he": "cot:ai-lam", "cot_moi": "cot:can-chot",
                                    "ly_do_he": "Rõ"}, bead_id="hr-1")
    k.ghi("khac", "cot.tra_ve", {"gop_y": "x"}, bead_id="kh-1")
    k.ghi("hr", "cot.tra_ve", {"gop_y": "Thiếu test"}, bead_id="hr-2")
    xau = tra_loi({"ky_uc": "x"})
    md = chay_thu(k, ClientGia(xau, xau, xau), nap_vai("nho-tach"), lambda t: LuatDuAn(("Fin",)), du_an="hr")
    assert "[/du-an/hr/nghiep-vu] q=0.60" in md and "luật cứng: tên module (Fin)" in md
    assert "sự kiện 3 (cot.tra_ve, hr-2): LỖI TÁCH" in md and "kh-1" not in md
    assert "Tổng: 1 ký ức dự kiến; đọc tới sự kiện 3." in md and k.id_moi_nhat() == 3


def test_do_tre_kho_gia(tmp_path):
    e = EmbedderGia()
    kho = sinh_kho(tmp_path / "do", e, 230, lo=100)
    assert kho.dem() == 230 and kho.dem("pham_vi = '/chung'") == 5
    kq = do_tre(kho, e, ["q1", "q2"], so_lan=5)
    assert set(kq) == {"p50", "p95", "max"} and 0 < kq["p50"] <= kq["p95"] <= kq["max"]
