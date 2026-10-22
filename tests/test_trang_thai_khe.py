from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.tram import CauHinhTram
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.phieu.trang_thai import trang_thai_khe

CH = CauHinhTram()
TEN = ("tat", "mat", "loi", "can", "lam", "ranh", "dao")


def test_du_sau_gia_tri(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": f"Claude {t}", "vai_uu_tien": ["coder"]}
                               for t in TEN], luc=LUC)
        for t in TEN:
            bat_tat_khe(kho, f"B/{t}", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
            if t != "mat":
                ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
        ghi_nhip(kho, "B/mat", luc=LUC - timedelta(seconds=91), giao_id=None, luot=None, buoc_tho="ranh",
                 han_muc=None)
        bat_tat_khe(kho, "B/tat", bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)
        ngat_cau_dao(kho, "B/dao", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/loi", "ket_thuc": "loi_he"}, luc=LUC, bead_id="x")
    p_lam = dat_phieu(kho, "B/lam", bead_id="hr-1")
    p_can = dat_phieu(kho, "B/can", bead_id="hr-2")
    with kho.giao_dich():
        kho.ghi_su_kien("hr-codex", "bao.can_hoi", {"giao_id": p_can.giao_id}, luc=LUC, bead_id="hr-2")
    ds = {t.khe_id.split("/")[1]: t for t in trang_thai_khe(kho, bay_gio=LUC, ch=CH)}
    assert {k: v.trang_thai for k, v in ds.items()} == {
        "tat": "tat", "mat": "mat_ket_noi", "loi": "loi", "can": "can_nguoi", "lam": "lam", "ranh": "ranh",
        "dao": "loi"}
    assert ds["lam"].phieu == {"giao_id": p_lam.giao_id, "bead_id": "hr-1", "du_an": "hr-codex", "buoc": "code",
                               "tieu_de": p_lam.tieu_de} and ds["lam"].so_phien == 1
    assert ds["ranh"].phieu is None and ds["ranh"].so_phien == 0 and ds["ranh"].ten_goi_nho == "Claude ranh"
    assert ds["dao"].cau_dao == {"ngat": True, "ly_do": "het-han-muc", "toi_luc": "2026-10-13T04:00:00Z"}
    assert {c["loai"]: c["trang_thai"] for c in ds["ranh"].han_muc["cua_so"]} == {"5h": "chua_biet",
                                                                                  "tuan": "chua_biet"}


def test_lan_chay_cuoi_xong_thi_ranh_va_khe_chua_nhip_la_mat_ket_noi(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "a", "cli": "claude", "ten_goi_nho": "A", "vai_uu_tien": ["qc"]},
                               {"ten": "b", "cli": "claude", "ten_goi_nho": "B", "vai_uu_tien": ["qc"]}], luc=LUC)
        for t in ("a", "b"):
            bat_tat_khe(kho, f"B/{t}", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
        ghi_nhip(kho, "B/a", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/a", "ket_thuc": "loi_he"}, luc=LUC, bead_id="x")
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/a", "ket_thuc": "xong"}, luc=LUC, bead_id="x")
    assert [t.trang_thai for t in trang_thai_khe(kho, bay_gio=LUC, ch=CH)] == ["ranh", "mat_ket_noi"]


def test_lan_chay_cuoi_dung_co_y_thi_van_ranh(tmp_path):
    # 21/10: thợ báo bí/cần hỏi → trạm dừng lần chạy (ket_thuc "dung"); tính là lỗi thì cả đội kẹt, không giao được.
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]}
                               for t in ("dung", "mo")], luc=LUC)
        for t in ("dung", "mo"):
            bat_tat_khe(kho, f"B/{t}", bat=True, vi_sao="fixture", tac_nhan="dai-ca", luc=LUC)
            ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/dung", "ket_thuc": "dung"}, luc=LUC, bead_id="x")
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/mo", "ket_thuc": "mo-coi"}, luc=LUC, bead_id="y")
    ds = {t.khe_id.split("/")[1]: t.trang_thai for t in trang_thai_khe(kho, bay_gio=LUC, ch=CH)}
    assert ds == {"dung": "ranh", "mo": "loi"}
