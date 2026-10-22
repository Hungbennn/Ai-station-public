"""`GET /api/doi-ngu?du_an=&so_ngay=` — lọc bảng điểm theo dự án và số ngày, mặc định mọi dự án, 30 ngày (D14;
plan 2d Task 6, G5, D28, D29); mọi khe đã khai có hàng theo vai ưu tiên, kể cả khi chưa có phiếu (D41, G22)."""
from contextlib import closing
from dataclasses import replace
from datetime import timedelta

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from kho_phieu_gia import LUC, dat_phieu
from tram.api.app import tao_app
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.khe import dang_ky_khe
from tram.phieu.kho import KhoPhieu

KHE = [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["qc"]},
       {"ten": "codex-2", "cli": "codex", "ten_goi_nho": "Codex 2", "vai_uu_tien": ["coder", "qc"]}]


def _app(tmp_path):
    kho = KhoPhieu(tmp_path / "sk.db")
    for i, (du_an, luc) in enumerate([("hr-codex", LUC), ("hr-codex", LUC - timedelta(days=40)), ("hr-khac", LUC)]):
        p = dat_phieu(kho, "B/claude-1", luc=luc + timedelta(minutes=i), bead_id=f"hr-{i}", du_an=du_an)
        with kho.giao_dich() as db:
            danh_dau_ket_thuc(db, p.giao_id, "xong", luc)
    kho.close()
    pt = replace(tao_pt(tmp_path, {"hr-codex": BdGia([]), "hr-khac": BdGia([])}),
                 mo_kho_phieu=lambda: KhoPhieu(tmp_path / "sk.db"), dong_ho=lambda: LUC)
    return tao_app(pt)


def so_phieu(app, q=""):
    r = goi(app, "GET", f"/api/doi-ngu{q}")
    assert r.status == 200
    return [h["so_phieu"] for h in r.json()["bang_diem"]]


def test_mac_dinh_moi_du_an_30_ngay_va_loc(tmp_path):
    app = _app(tmp_path)
    assert so_phieu(app) == [2]                                    # phiếu 40 ngày trước nằm ngoài
    assert so_phieu(app, "?so_ngay=92") == [3]
    assert so_phieu(app, "?du_an=hr-codex") == [1]
    assert so_phieu(app, "?du_an=hr-khac&so_ngay=7") == [1]
    assert so_phieu(app, "?du_an=&so_ngay=30") == [2]


def test_tham_so_sai(tmp_path):
    app = _app(tmp_path)
    assert goi(app, "GET", "/api/doi-ngu?du_an=khong-co").status == 404
    assert goi(app, "GET", "/api/doi-ngu?so_ngay=0").status == 422
    assert goi(app, "GET", "/api/doi-ngu?so_ngay=93").status == 422
    assert goi(app, "GET", "/api/doi-ngu?so_ngay=x").status == 422


def test_moi_khe_da_khai_co_hang_ke_ca_khi_bo_loc_khong_con_phieu(tmp_path):
    app = _app(tmp_path)
    with closing(KhoPhieu(tmp_path / "sk.db")) as kho:
        with kho.giao_dich():
            dang_ky_khe(kho, "B", KHE, luc=LUC)
        dat_phieu(kho, "B/codex-2", luc=LUC - timedelta(days=40), bead_id="hr-9")

    def hang(q=""):
        return [(h["khe_id"], h["vai"], h["so_phieu"], h["qua_lan_dau_mau"], h["bi_tra_ve_mau"])
                for h in goi(app, "GET", f"/api/doi-ngu{q}").json()["bang_diem"]]
    assert hang() == [("B/claude-1", "coder", 2, 2, 0),            # có phiếu, ngoài vai ưu tiên: vẫn giữ
                      ("B/claude-1", "qc", 0, None, None),          # vai ưu tiên chưa có phiếu: "—"
                      ("B/codex-2", "coder", 0, 0, 0),              # phiếu 40 ngày trước ở ngoài, hàng vẫn còn
                      ("B/codex-2", "qc", 0, None, None)]
    assert hang("?so_ngay=92")[2] == ("B/codex-2", "coder", 1, 0, 0)
    assert [h[:3] for h in hang("?du_an=hr-khac&so_ngay=7")] == [
        ("B/claude-1", "coder", 1), ("B/claude-1", "qc", 0), ("B/codex-2", "coder", 0), ("B/codex-2", "qc", 0)]
