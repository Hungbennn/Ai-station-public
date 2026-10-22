"""TM-2 (spec `tu-merge` "Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao", "Đại ca merge tay"): khoá `cho_dai_ca`
của `GET /api/du-an/{ten}/tu-dong` — tính lúc đọc từ sự kiện, lý do bằng lời thường, tiêu đề bead ghép lúc đọc (không
nằm trong sự kiện); công tắc tắt → rỗng."""
from dataclasses import replace

from api_gia import tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC
from tram.phieu.kho import KhoPhieu
from tram.suy.tu_merge import cho_dai_ca
from tram.tu_dong.luu import doi_cai_dat


def _sk(kho, loai, du_lieu, bead_id, du_an="repo-nhap"):
    with kho.giao_dich():
        kho.ghi_su_kien(du_an, loai, du_lieu, luc=LUC, bead_id=bead_id, tac_nhan="tram/tu-merge")


def test_cho_dai_ca_tu_su_kien(tmp_path):
    kho = KhoPhieu(tmp_path / "sk.db")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_dang_chay"], "commit": "c" * 40}, "rn-1")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_do", "hang_rao_khach_thay"], "commit": "c" * 40}, "rn-1")
    _sk(kho, "tu_merge.cho", {"ly_do": ["schema_duong_dan"], "commit": "d" * 40}, "rn-2")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_do"], "commit": "e" * 40}, "rn-3")
    _sk(kho, "tu_merge.bat_dau", {"ma_thao_tac": "tm-1", "commit": "e" * 40, "pr": 3, "loai": "code"}, "rn-3")
    _sk(kho, "tu_merge.loi", {"ma_thao_tac": "tm-4", "ma_loi": "gh-loi-3-lan"}, "rn-4")
    _sk(kho, "tu_merge.cho", {"ly_do": ["cot"], "commit": "f" * 40}, "rn-5")
    _sk(kho, "pr.da_merge", {"bead_id": "rn-5"}, "rn-5")                                # Đại ca merge tay
    _sk(kho, "tu_merge.cho", {"ly_do": ["qc"], "commit": "f" * 40}, "rn-6", du_an="khac")
    cho = {c["bead_id"]: c["ly_do"] for c in cho_dai_ca(kho.db, "repo-nhap")}
    assert set(cho) == {"rn-1", "rn-2", "rn-4"}
    assert [(l["nhan"], l["muc"]) for l in cho["rn-1"]] == [("CI chưa xanh", "can_nguoi"),
                                                            ("Chạm hàng rào: thứ khách thấy", "can_nguoi")]
    assert cho["rn-2"] == [{"ma": "schema_duong_dan", "nhan": "Cấu trúc DB — luôn chờ Đại ca", "muc": "loi"}]
    assert cho["rn-4"][0]["nhan"] == "Tự merge lỗi — cần Đại ca"
    goi = []
    ds = cho_dai_ca(kho.db, "repo-nhap", lambda: goi.append(1) or {"rn-2": "Thêm cột ghi chú"})
    assert {c["bead_id"]: c["tieu_de"] for c in ds} == {"rn-1": "", "rn-2": "Thêm cột ghi chú", "rn-4": ""}
    assert goi == [1] and cho_dai_ca(kho.db, "rong", lambda: goi.append(2) or {}) == [] and goi == [1]


def test_api_cho_dai_ca_chi_khi_bat(tmp_path):
    app, _ = tao_app_gia(tmp_path, {"repo-nhap": BdGia([bead("rn-1", title="Sửa định dạng ngày")])})
    kho = KhoPhieu(tmp_path / "sk.db")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_do"], "commit": "c" * 40}, "rn-1")
    assert goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()["cho_dai_ca"] == []
    doi_cai_dat(kho.db, "repo-nhap", lambda c: replace(c, tu_merge=True), tac_nhan="dai-ca/dashboard")
    [c] = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()["cho_dai_ca"]
    assert (c["bead_id"], c["tieu_de"], c["ly_do"][0]["nhan"]) == ("rn-1", "Sửa định dạng ngày", "CI chưa xanh")
    assert "commit" not in c
    sk_tieu_de = kho.db.execute("SELECT count(*) FROM su_kien WHERE du_lieu LIKE '%Sửa định dạng%'").fetchone()[0]
    assert sk_tieu_de == 0                                                     # tiêu đề không vào sự kiện
