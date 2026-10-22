"""1b-3: xoá cứng (dịch vụ dừng, chỉ bản đã xoá mềm, khớp chính xác) và xoá mềm theo phạm vi qua dịch vụ."""
import pytest

from nho_gia import EmbedderGia, ky_uc
from tram.cli import main, tao_parser
from tram.nho.khoa import khoa_dich_vu, thu_muc_nho
from tram.nho.kho import KhoKyUc
from tram.nho.lenh_xoa import xoa_pham_vi
from tram.nho.nhat_ky import NhatKy
from tram.nho.pham_vi import LoiVungCap
from tram.nho.xoa_cung import ConThaoTacDo, DichVuDangChay, xoa_cung
from tram.su_kien.kho import KhoSuKien

E = EmbedderGia()


def dung(thu, *ds, so_chieu=16):
    kho = KhoKyUc(thu / "lancedb", so_chieu=so_chieu)
    e = EmbedderGia(so_chieu)
    for id, pv, xoa, *nguon in ds:
        kho.them(ky_uc(id, pv, vector=e.embed([id])[0], nguon=tuple(nguon) or None))
        if xoa:
            kho.xoa_mem([id])
    return kho


def test_chi_xoa_ban_da_xoa_mem_theo_id_va_don_phien_ban(tmp_path):
    thu, sk = tmp_path / "nho", KhoSuKien(tmp_path / "sk.db")
    dung(thu, ("m-1", "/du-an/a/cach-lam", True), ("m-2", "/du-an/a/cach-lam", False))
    nk = NhatKy(thu / "nhat-ky.db")
    nk.bat_dau("1:1", 1, {"buoc": [{"ky_uc": {"id": "m-1", "noi_dung": "bí mật"}}]})
    nk.hoan_tat("1:1", 1)
    assert xoa_cung(thu, sk, id="m-2", that=True, so_chieu=16).hang == ()
    xem = xoa_cung(thu, sk, id="m-1", so_chieu=16)
    assert xem.hang == ({"id": "m-1", "pham_vi": "/du-an/a/cach-lam"},) and not xem.da_xoa
    assert KhoKyUc(thu / "lancedb", so_chieu=16).dem() == 2
    assert xoa_cung(thu, sk, id="m-1", that=True, so_chieu=16).da_xoa
    kho = KhoKyUc(thu / "lancedb", so_chieu=16)
    assert sorted(kho.lay(["m-1", "m-2"])) == ["m-2"] and kho.so_phien_ban() == 1
    assert "noi_dung" not in nk.lay("1:1").ke_hoach["buoc"][0]["ky_uc"]
    assert [s.du_lieu for s in sk.gan_day("a", "nho.xoa_cung", 9)] == [{"id": "m-1", "pham_vi": "/du-an/a/cach-lam"}]


def test_theo_pham_vi_khop_chinh_xac(tmp_path):
    thu, sk = tmp_path / "nho", KhoSuKien(tmp_path / "sk.db")
    dung(thu, ("m-a", "/du-an/hr/cach-lam", True), ("m-b", "/du-an/hr-codex/cach-lam", True),
         ("m-c", "/chung", True))
    assert [h["id"] for h in xoa_cung(thu, sk, pham_vi="/du-an/hr/cach-lam", that=True, so_chieu=16).hang] == ["m-a"]
    assert sorted(KhoKyUc(thu / "lancedb", so_chieu=16).lay(["m-a", "m-b", "m-c"])) == ["m-b", "m-c"]
    assert [s.du_lieu["id"] for s in sk.gan_day("_tram", "nho.xoa_cung", 9)] == []
    for pv in ("/du-an/hr", "/du-an", "/", "/vai"):
        with pytest.raises(LoiVungCap):
            xoa_cung(thu, sk, pham_vi=pv, that=True, so_chieu=16)
    with pytest.raises(ValueError):
        xoa_cung(thu, sk, id="m-b", pham_vi="/chung", so_chieu=16)


def test_ky_uc_thang_cap_ghi_so_cap_truoc_khi_xoa(tmp_path):
    thu, sk = tmp_path / "nho", KhoSuKien(tmp_path / "sk.db")
    dung(thu, ("m-t", "/chung", True, {"loai": "thang_cap", "id_goc": "m-b", "du_an": "b"},
               {"loai": "thang_cap", "id_goc": "m-a", "du_an": "a"}))
    xoa_cung(thu, sk, id="m-t", that=True, so_chieu=16)
    assert NhatKy(thu / "nhat-ky.db").cac_cap() == {"m-a|m-b": "xoa_cung"}
    assert sk.gan_day("_tram", "nho.xoa_cung", 9)[0].du_lieu == {"id": "m-t", "pham_vi": "/chung"}


def test_tu_choi_khi_dich_vu_chay_hoac_con_thao_tac_do(tmp_path):
    thu, sk = tmp_path / "nho", KhoSuKien(tmp_path / "sk.db")
    dung(thu, ("m-1", "/chung", True))
    with khoa_dich_vu(thu):
        with pytest.raises(DichVuDangChay):
            xoa_cung(thu, sk, id="m-1", so_chieu=16)
    NhatKy(thu / "nhat-ky.db").bat_dau("9:1", 9, {"buoc": []})
    with pytest.raises(ConThaoTacDo):
        xoa_cung(thu, sk, id="m-1", that=True, so_chieu=16)
    assert KhoKyUc(thu / "lancedb", so_chieu=16).dem() == 1


def test_xoa_pham_vi_liet_ke_hoi_roi_xoa_tung_id():
    goi, trang = [], [{"tong": 2, "ky_uc": [{"id": "m-1"}, {"id": "m-2"}]}, {"tong": 0, "ky_uc": []}]

    def g(d, than):
        goi.append((d, than))
        return trang.pop(0) if d == "/danh-sach" else {"da_xoa": True}
    assert xoa_pham_vi("/chung", g, lambda cau: "2 ký ức" in cau) == 2
    assert goi == [("/danh-sach", {"pham_vi": "/chung", "gioi_han": 1000}), ("/xoa", {"id": "m-1"}),
                   ("/xoa", {"id": "m-2"}), ("/danh-sach", {"pham_vi": "/chung", "gioi_han": 1000})]
    goi.clear()
    trang.append({"tong": 1, "ky_uc": [{"id": "m-3"}]})
    assert xoa_pham_vi("/chung", g, lambda cau: False) == 0 and [d for d, _ in goi] == ["/danh-sach"]


def test_lenh_dang_ky_va_tu_choi_pham_vi_tien_to(monkeypatch, capsys):
    p = tao_parser()
    for argv in (["nho", "xoa-pham-vi", "/chung"], ["nho", "xoa-cung", "--id", "m-1"],
                 ["nho", "xoa-cung", "--pham-vi", "/chung", "--dong-y"]):
        assert callable(p.parse_args(argv).ham)
    monkeypatch.setattr("tram.nho.khach.doc_token", lambda **kw: pytest.fail("không được đọc token"))
    assert main(["nho", "xoa-pham-vi", "/du-an/hr", "--dong-y"]) == 1
    assert "phạm vi phải đầy đủ" in capsys.readouterr().err


def test_lenh_xoa_cung_hoi_roi_xoa(tram_home_tam, monkeypatch, capsys):
    dung(thu_muc_nho(), ("m-1", "/chung", True), so_chieu=1024)
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    assert main(["nho", "xoa-cung", "--id", "m-1"]) == 1
    assert main(["nho", "xoa-cung", "--id", "m-1", "--dong-y"]) == 0
    out = capsys.readouterr().out
    assert "- m-1  [/chung]" in out and "Đã xoá cứng 1 ký ức." in out
    assert main(["nho", "xoa-cung", "--pham-vi", "/chung", "--dong-y"]) == 0
    assert "Không có ký ức đã xoá mềm nào khớp" in capsys.readouterr().out
