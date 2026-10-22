from khe_duyet_gia import dang_ky_va_duyet
from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhTram
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.khe import dang_ky_khe, phien_ban_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.suy.bang_diem import bang_diem
from tram.suy.doi_ngu import doi_ngu, muc_han_muc

NG = CauHinhHanMuc()


def cs(loai, pt):
    return CuaSo(loai=loai, trang_thai="biet", phan_tram=pt, reset_luc="2026-10-13T05:00:00Z",
                 doc_luc="2026-10-13T02:59:00Z")


def hm(*c):
    return HanMuc(khe_id="B/a", nguon="stream", cua_so=list(c))


def test_muc_han_muc_theo_luat_nhan_viec():
    assert muc_han_muc(hm(cs("5h", 90), cs("tuan", 1)), NG) == "ngung"
    assert muc_han_muc(hm(cs("5h", 10), cs("tuan", 80)), NG) == "chi_p0_p1"
    assert muc_han_muc(hm(cs("5h", 10), CuaSo(loai="tuan", trang_thai="chua_biet")), NG) == "chua_biet"
    assert muc_han_muc(hm(cs("5h", 10), cs("tuan", 10)), NG) == "ok"


def test_doi_ngu_the_khe_ten_goi_nho_khong_email_va_phien_ban(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_va_duyet(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]},
                               {"ten": "claude-2", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["qc"]}],
                    luc=LUC)
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="chay",
                 han_muc=HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[cs("5h", 40), cs("tuan", 85)]))
    p = dat_phieu(kho, "B/claude-1", bead_id="hr-1", tieu_de="Sửa ‮giá")
    r = doi_ngu(kho, bay_gio=LUC, ch=CauHinhTram())
    k1, k2 = r["khe"]
    assert (k1["khe_id"], k1["may"], k1["ten_goi_nho"], k1["trang_thai"], k1["so_phien"]) == (
        "B/claude-1", "B", "Claude 1", "lam", 1)
    assert k1["phieu"] == {"giao_id": p.giao_id, "bead_id": "hr-1", "du_an": "hr-codex", "buoc": "code",
                           "tieu_de": "Sửa giá"}
    assert k1["muc_han_muc"] == "chi_p0_p1" and k1["phien_ban"] == phien_ban_khe(kho, "B/claude-1")
    assert (k2["ten_goi_nho"], k2["trang_thai"], k2["muc_han_muc"]) == ("B/claude-2", "mat_ket_noi", "chua_biet")
    assert "a@b.vn" not in str(r) and "ma_giao" not in str(r)
    assert r["luat_vai"]["vai_cua_buoc"] == {"code": "coder", "qc": "qc", "spec": "spec"}
    assert r["bang_diem"][0]["khe_id"] == "B/claude-1"


def test_bang_diem_lan_chay_trung_binh_tren_phieu_da_ket_thuc(tmp_path):
    kho = kho_tam(tmp_path)
    for i, (bead, kt, lan) in enumerate([("hr-1", "xong", 1), ("hr-2", "bi", 3), ("hr-3", None, 2)]):
        p = dat_phieu(kho, "B/claude-1", luc=LUC + timedelta(minutes=i), bead_id=bead)
        with kho.giao_dich() as db:
            for j in range(lan):
                db.execute("INSERT INTO lan_chay VALUES (?, 'B/claude-1', ?, ?, ?)",
                           (f"r-{bead}-{j}", p.giao_id, j + 1, "2026-10-13T03:00:00Z"))
            if kt:
                danh_dau_ket_thuc(db, p.giao_id, kt, LUC)
    dat_phieu(kho, "B/claude-2", bead_id="hr-9", buoc="qc")
    assert bang_diem(kho.db) == [
        {"khe_id": "B/claude-1", "vai": "coder", "so_phieu": 3, "so_xong": 1, "lan_chay_tb": 2.0,
         "qua_lan_dau": 0.0, "qua_lan_dau_mau": 1, "bi_tra_ve": None, "bi_tra_ve_mau": 0},
        {"khe_id": "B/claude-2", "vai": "qc", "so_phieu": 1, "so_xong": 0, "lan_chay_tb": None,
         "qua_lan_dau": None, "qua_lan_dau_mau": None, "bi_tra_ve": None, "bi_tra_ve_mau": None}]
