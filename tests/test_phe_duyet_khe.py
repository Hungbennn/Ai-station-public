from dataclasses import replace
from datetime import timedelta

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC
from tram.api.app import tao_app
from tram.api.bo_dem import BoDemBeads
from tram.api.luong import TrangThaiLuong, mot_nhip
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import dang_ky_khe
from tram.phieu.kho import KhoPhieu
from tram.suy.phe_duyet_khe import muc_cau_dao
from tram.su_kien.kho import KhoSuKien

KHE = [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]} for t in ("claude-1", "claude-2")]


def _kho(tmp_path) -> KhoPhieu:
    kho = KhoPhieu(tmp_path / "sk.db")
    with kho.giao_dich():
        dang_ky_khe(kho, "B", KHE, luc=LUC)
        ngat_cau_dao(kho, "B/claude-2", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    return kho


def test_muc_cau_dao_chi_khe_dang_ngat_va_het_khi_toi_gio(tmp_path):
    kho = _kho(tmp_path)
    ds = muc_cau_dao(kho, LUC)
    assert len(ds) == 1 and ds[0]["loai"] == "he" and ds[0]["du_an"] == "_tram" and ds[0]["bead_id"] is None
    assert ds[0]["chi_tiet"] == {"su_kien": "khe.cau_dao_ngat", "luc": "2026-10-13T03:00:00Z", "khe_id": "B/claude-2",
                                 "toi_luc": "2026-10-13T04:00:00Z",
                                 "loi": "Cầu dao khe B/claude-2 ngắt tới 2026-10-13T04:00:00Z — hết hạn mức"}
    assert muc_cau_dao(kho, LUC + timedelta(hours=1)) == []


def test_api_phe_duyet_co_muc_cau_dao_khi_bat_kho_phieu(tmp_path):
    _kho(tmp_path).close()
    bds = {"hr": BdGia([bead("hr-1", labels=["cot:cho-review"])])}
    pt = replace(tao_pt(tmp_path, bds), mo_kho_phieu=lambda: KhoPhieu(tmp_path / "sk.db"), dong_ho=lambda: LUC)
    r = goi(tao_app(pt), "GET", "/api/phe-duyet").json()
    assert r["so"] == 2 and [m["loai"] for m in r["muc"]] == ["he", "cho-review"]
    assert goi(tao_app(tao_pt(tmp_path, bds)), "GET", "/api/phe-duyet").json()["so"] == 1   # kho phiếu tắt


def test_luong_bao_doi_ngu_va_phe_duyet_khi_cau_dao(tmp_path):
    k, bo = KhoSuKien(tmp_path / "sk.db"), BoDemBeads(lambda ten: BdGia([]))
    tt = TrangThaiLuong(moc=0)
    k.ghi("hr", "chay.xong", {"khe_id": "B/claude-1"}, bead_id="hr-1")
    ra = mot_nhip(k, bo, [], tt)
    assert [x.split("\n")[0] for x in ra] == ["event: su_kien", "event: doi_ngu_doi"]
    k.ghi("_tram", "khe.cau_dao_ngat", {"khe_id": "B/claude-1"})
    ra = mot_nhip(k, bo, [], tt)
    assert [x.split("\n")[0] for x in ra] == ["event: su_kien", "event: phe_duyet_doi", "event: doi_ngu_doi"]
    k.ghi("hr", "quet.xong", {})
    assert "event: doi_ngu_doi" not in "".join(mot_nhip(k, bo, [], tt))
