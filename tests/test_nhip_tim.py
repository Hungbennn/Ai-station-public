from khe_duyet_gia import dang_ky_va_duyet
from datetime import timedelta

import pytest
from pydantic import ValidationError

from kho_phieu_gia import LUC, kho_tam
from phieu_gia import de_xuat
from tram.cau_hinh.tram import CauHinhTram
from tram.chu import estop
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.ghi import dat_dung_mem
from tram.phieu.kho import chuoi_gio
from tram.phieu.ket_thuc import thu_hoi
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.nhip import ThanNhip, xu_ly_nhip
from tram.phieu.yeu_cau_tho import KhongThuocMay
from tram.su_kien.kho import KhoSuKien

CH = CauHinhTram()
K = "B/claude-1"


@pytest.fixture
def kho(tmp_path):
    k = kho_tam(tmp_path)
    with k.giao_dich():
        dang_ky_va_duyet(k, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "1", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
    return k


def nhip(kho, luc=LUC, chon=None, **kw):
    return xu_ly_nhip(kho, "B", ThanNhip(**{"khe_id": K, "buoc_tho": "ranh", **kw}), bay_gio=luc, ch=CH, chon=chon)


def hm(pt5h, doc="2026-10-13T02:59:00Z"):
    return HanMuc(khe_id=K, nguon="stream", cua_so=[
        CuaSo(loai="5h", trang_thai="biet", phan_tram=pt5h, reset_luc="2026-10-13T05:00:00Z", doc_luc=doc),
        CuaSo(loai="tuan", trang_thai="biet", phan_tram=10, reset_luc="2026-10-18T00:00:00Z", doc_luc=doc)])


def test_ranh_khong_co_phan_4_thi_khong_phieu_va_ghi_de_nhip(kho):
    assert nhip(kho) == {"tiep_tuc": True, "phieu": None}
    assert nhip(kho, LUC + timedelta(seconds=30)) == {"tiep_tuc": True, "phieu": None}
    assert kho.db.execute("SELECT COUNT(*), MAX(luc) FROM nhip_tim").fetchone() == (1, "2026-10-13T03:00:30Z")


def test_ranh_nhan_phieu_ngay_nhip_dau_roi_khong_nhan_them(kho):
    goi = []
    ra = nhip(kho, chon=lambda khe, h: goi.append((khe, h)) or de_xuat())
    p = ra["phieu"]
    assert ra["tiep_tuc"] and p["khe_id"] == K and p["luot"] == 1 and len(p["ma_giao"]) == 22
    assert goi[0][0] == K and {c.loai for c in goi[0][1].cua_so} == {"5h", "tuan"}
    assert nhip(kho, chon=lambda *_: de_xuat("hr-2")) == {"tiep_tuc": True, "phieu": None}
    assert len(goi) == 1


def test_giu_phieu_gia_han_va_dung_mem(kho):
    p = nhip(kho, chon=lambda *_: de_xuat())["phieu"]
    giu = {"giao_id": p["giao_id"], "luot": 1, "buoc_tho": "chay"}
    ra = nhip(kho, LUC + timedelta(minutes=3), **giu)
    assert ra == {"tiep_tuc": True, "han_giu": "2026-10-13T03:13:00Z"}
    assert kho.lay(p["giao_id"]).phieu.han_giu == "2026-10-13T03:13:00Z"
    estop.bat("thử")
    assert nhip(kho, **giu)["ly_do"] == "estop"
    estop.tat()
    with kho.giao_dich():
        ngat_cau_dao(kho, K, ly_do="x", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    r = nhip(kho, **giu)
    assert r["tiep_tuc"] is False and r["ly_do"] == "cau-dao" and "han_giu" in r
    with kho.giao_dich() as db:
        bat_tat_khe(kho, K, bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    assert nhip(kho, **giu)["ly_do"] == "khe-tat"
    with kho.giao_dich() as db:
        bat_tat_khe(kho, K, bat=True, vi_sao="", tac_nhan="dai-ca", luc=LUC)
        db.execute("DELETE FROM su_kien WHERE loai LIKE 'khe.cau_dao%'")
        dat_dung_mem(db, p["giao_id"], "can-hoi")
    assert nhip(kho, **giu)["ly_do"] == "can-hoi"


def test_luot_cu_va_thu_hoi_la_dung_cung(kho, tmp_path):
    p = nhip(kho, chon=lambda *_: de_xuat())["phieu"]
    assert nhip(kho, giao_id=p["giao_id"], luot=2, buoc_tho="chay") == {"tiep_tuc": False, "ly_do": "luot-cu"}
    with kho.giao_dich():
        thu_hoi(kho, kho.lay(p["giao_id"]), ly_do="mat-nhip", luc=LUC)
    assert nhip(kho, giao_id=p["giao_id"], luot=1, buoc_tho="chay") == {"tiep_tuc": False, "ly_do": "thu-hoi"}
    assert len(KhoSuKien(tmp_path / "su-kien.db").gan_day("hr-codex", "tho.tu_choi", 5)) == 2


def test_ket_noi_lai_va_su_kien_han_muc(kho, tmp_path):
    with kho.giao_dich():
        kho.ghi_su_kien("_tram", "khe.mat_ket_noi", {"khe_id": K}, luc=LUC)
    nhip(kho, han_muc=hm(60))
    nhip(kho, han_muc=hm(64.9))                       # đổi < 5 điểm so với lần ghi trước: không ghi
    nhip(kho, han_muc=hm(65))                         # trôi chậm: so với 60 đã ghi → ghi
    sk = KhoSuKien(tmp_path / "su-kien.db")
    assert len(sk.gan_day("_tram", "khe.ket_noi", 5)) == 1
    assert [s.du_lieu["cua_so"][0]["phan_tram"] for s in sk.gan_day("_tram", "khe.han_muc", 5)] == [65, 60]


def test_han_muc_khong_ro_mot_lan_sau_khi_da_chay(kho, tmp_path):
    sk = KhoSuKien(tmp_path / "su-kien.db")
    nhip(kho)
    assert sk.gan_day("_tram", "khe.han_muc_khong_ro", 5) == []          # chưa chạy lần nào
    with kho.giao_dich() as db:
        db.execute("INSERT INTO lan_chay VALUES ('r1', ?, 'g', 1, ?)", (K, chuoi_gio(LUC)))
    nhip(kho)
    nhip(kho)
    assert len(sk.gan_day("_tram", "khe.han_muc_khong_ro", 5)) == 1
    nhip(kho, han_muc=hm(10))                                           # biết đủ cửa sổ
    nhip(kho, LUC + timedelta(hours=7), han_muc=hm(10))                  # quá tuổi → chưa biết lại
    assert len(sk.gan_day("_tram", "khe.han_muc_khong_ro", 5)) == 2


def test_quyen_va_cau_truc(kho):
    with pytest.raises(KhongThuocMay):
        xu_ly_nhip(kho, "C", ThanNhip(khe_id=K, buoc_tho="ranh"), bay_gio=LUC, ch=CH)
    with pytest.raises(KhongThuocMay):
        xu_ly_nhip(kho, "B", ThanNhip(khe_id="B/claude-9", buoc_tho="ranh"), bay_gio=LUC, ch=CH)
    for sai in ({"giao_id": "g-20261013-0001"}, {"luot": 1}, {"buoc_tho": "ngu"},
                {"han_muc": HanMuc(khe_id="B/claude-2").model_dump()}):
        with pytest.raises(ValidationError):
            ThanNhip(**{"khe_id": K, "buoc_tho": "ranh", **sai})
