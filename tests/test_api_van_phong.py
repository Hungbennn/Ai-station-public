from dataclasses import replace

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC, dat_phieu
from tram.api.app import tao_app
from tram.chu import estop
from tram.phieu.khe import dang_ky_khe, bat_tat_khe
from tram.phieu.kho import KhoPhieu
from tram.phieu.nhip_tim import ghi_nhip

BDS = {"hr-codex": BdGia([bead("hr-1", labels=["cot:cho-review"]), bead("hr-2", labels=["cot:ai-lam"])])}


def _app(tmp_path, bds=BDS, *, kho_phieu=True):
    db = tmp_path / "sk.db"
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
        bat_tat_khe(kho, "B/claude-1", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="chay", han_muc=None)
    dat_phieu(kho, "B/claude-1", bead_id="hr-2", tieu_de="Sửa thuế")
    kho.close()
    pt = replace(tao_pt(tmp_path, bds), mo_kho_phieu=(lambda: KhoPhieu(db)) if kho_phieu else None,
                 dong_ho=lambda: LUC)
    return tao_app(pt)


def test_van_phong_phong_nhan_vat_va_badge(tmp_path):
    r = goi(_app(tmp_path), "GET", "/api/van-phong")
    assert r.status == 200 and "unsafe-eval" not in r.headers["content-security-policy"]
    d = r.json()
    phong = {p["ma"]: p for p in d["phong"]}
    assert phong["giam-doc"]["so_cho"] == 1 and phong["may-chu"]["suc_khoe"] == {"mau": "xanh", "ly_do": [], "muc": []}
    assert phong["dieu-phoi"]["sang"] is None and "du-an:hr-codex" in phong
    (nv,) = d["nhan_vat"]
    assert (nv["ten"], nv["hien_thi"], nv["phong"], nv["bead"]["bead_id"]) == ("Claude 1", "lam", "du-an:hr-codex", "hr-2")
    assert d["kho_phieu"] is True and "a@b.vn" not in r.body.decode() and "ma_giao" not in r.body.decode()


def test_van_phong_khi_kho_phieu_tat_va_tram_loi(tmp_path, tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    estop.bat("thử")
    bds = {**BDS, "tram": BdGia([], ra_loi_truoc={"tat_ca": 1})}
    d = goi(_app(tmp_path, bds, kho_phieu=False), "GET", "/api/van-phong").json()
    assert d["kho_phieu"] is False and d["nhan_vat"] == []
    sk = {p["ma"]: p for p in d["phong"]}["may-chu"]["suc_khoe"]
    assert (sk["mau"], sk["ly_do"]) == ("do", ["Estop đang bật", "Không đọc được beads của dự án tram"])
