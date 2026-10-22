"""Lát 2f (D17, D38 Q12): GET /api/tong-quan gom các route có sẵn. Chỉ đọc. `GET /api/su-kien/gan-day` đã bỏ
(bs-2bd.1.6): không màn nào gọi; Tổng quan lấy sự kiện qua `/api/tong-quan`."""
from dataclasses import replace

import pytest

from api_gia import DAI_CA, tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC, dat_phieu
from tram.api.app import tao_app
from tram.phieu.khe import dang_ky_khe
from tram.phieu.kho import KhoPhieu
from tram.suy import he_thong

BDS = {"hr": BdGia([bead("hr-1", labels=["cot:cho-review"]), bead("hr-2", labels=["cot:can-chot"]),
                    bead("hr-5", title="Sửa ngày", status="closed", closed_at="2026-10-13T02:00:00Z"),
                    bead("hr-4", status="closed", closed_at="2026-10-12T02:00:00Z")])}


@pytest.fixture
def app(tmp_path, monkeypatch):
    def chay(argv):
        return (0, "state = running\nPATH=/bi/mat") if argv[0] == "launchctl" else (44, "")
    monkeypatch.setattr(he_thong, "_CHUNG", he_thong.DocHeThong(chay=chay, home=tmp_path, uid=501))
    db = tmp_path / "sk.db"
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
    dat_phieu(kho, "B/claude-1", bead_id="hr-2", tieu_de="Sửa thuế")
    kho.close()
    pt = replace(tao_pt(tmp_path, BDS), mo_kho_phieu=lambda: KhoPhieu(db), dong_ho=lambda: LUC)
    pt.mo_kho().ghi("hr", "giao.nhan", {"khe_id": "B/claude-1", "buoc": "code"}, bead_id="hr-2", tac_nhan="tram/api")
    return tao_app(pt)


def test_tong_quan_gom_du_lieu_cac_trang(app):
    r = goi(app, "GET", "/api/tong-quan")
    assert r.status == 200 and "unsafe-eval" not in r.headers["content-security-policy"]
    d = r.json()
    assert set(d) == {"phe_duyet", "du_an", "tram", "doi_ngu", "usage", "dich_vu", "su_kien", "doc_luc"}
    assert d["phe_duyet"]["so"] == len(d["phe_duyet"]["muc"]) == 1
    (da,) = d["du_an"]
    assert da["so_bead"]["can-chot"] == 1 and da["moi_xong"] == {"id": "hr-5", "tieu_de": "Sửa ngày",
                                                                 "luc": "2026-10-13T02:00:00Z"}
    assert d["tram"] == {"estop": False, "la_dai_ca": False}
    assert d["doi_ngu"]["bat"] is True and [k["khe_id"] for k in d["doi_ngu"]["khe"]] == ["B/claude-1"]
    assert set(d["doi_ngu"]) == {"bat", "khe"} and set(d["usage"]) == {"theo_nguon", "theo_ngay"}
    assert d["dich_vu"][0] == {"nhan": "vn.tram.api", "viec": "dashboard + API", "da_cai": False, "dang_chay": True}
    assert d["su_kien"][0]["mo_ta"] == "→ B/claude-1 · code"
    assert "/bi/mat" not in r.body.decode() and "a@b.vn" not in r.body.decode()


def test_route_su_kien_gan_day_da_bo(app):
    assert goi(app, "GET", "/api/su-kien/gan-day?gioi_han=1").status == 404
    assert goi(app, "GET", "/api/su-kien/gan-day", headers=DAI_CA).status == 404
    assert goi(app, "GET", "/api/tong-quan", headers={"Host": "la.example"}).status == 421
