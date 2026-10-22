from khe_duyet_gia import dang_ky_va_duyet
from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.tram import CauHinhTram
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.phieu.trang_thai import trang_thai_khe
from tram.suy.nhan_vat import nhan_vat, ten_nhan_vat

CH = CauHinhTram()
DA = ["hr-codex", "tram"]


def _khe(kho, may, *ten, cli="claude", ten_goi_nho="Claude"):
    with kho.giao_dich():
        dang_ky_va_duyet(kho, may, [{"ten": t, "cli": cli, "ten_goi_nho": ten_goi_nho, "vai_uu_tien": ["coder"]}
                               for t in ten], luc=LUC)
        for t in ten:
            ghi_nhip(kho, f"{may}/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)


def _nv(kho, cac_du_an=DA):
    return {x["khe_id"]: x for x in nhan_vat(kho, trang_thai_khe(kho, bay_gio=LUC, ch=CH), cac_du_an)}


def test_ten_nhan_vat_theo_cli_va_so_khe_trung_thi_them_may():
    assert ten_nhan_vat([("B/claude-1", "claude"), ("B/codex-2", "codex"), ("B/rieng", "gemini")]) == {
        "B/claude-1": "Claude 1", "B/codex-2": "Codex 2", "B/rieng": "Gemini rieng"}
    assert ten_nhan_vat([("B/claude-1", "claude"), ("C/claude-1", "claude")]) == {
        "B/claude-1": "Claude 1 (B)", "C/claude-1": "Claude 1 (C)"}


def test_phong_va_hien_thi_theo_trang_thai(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "B", "lam", "ranh", "tat", "dao", "la", ten_goi_nho="dai-ca@vi-du.vn")
    with kho.giao_dich():
        dang_ky_va_duyet(kho, "B", [{"ten": "mat", "cli": "codex", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]}], luc=LUC)
        ngat_cau_dao(kho, "B/dao", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    dat_phieu(kho, "B/lam", bead_id="hr-1", tieu_de="Sửa \u202egiá", buoc="qc")
    cu = dat_phieu(kho, "B/tat", bead_id="hr-2")
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, cu.giao_id, "xong", LUC)
        bat_tat_khe(kho, "B/tat", bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    dat_phieu(kho, "B/la", bead_id="x-1", du_an="da-go")
    nv = _nv(kho)
    assert nv["B/lam"] == {"khe_id": "B/lam", "ten": "Claude lam", "cli": "claude", "trang_thai": "lam",
                           "hien_thi": "lam", "phong": "du-an:hr-codex", "cau_dao_ngat": False,
                           "bead": {"du_an": "hr-codex", "bead_id": "hr-1", "tieu_de": "Sửa giá", "buoc": "qc"}}
    assert (nv["B/ranh"]["phong"], nv["B/ranh"]["hien_thi"], nv["B/ranh"]["bead"]) == ("ca-phe", "ranh", None)
    assert (nv["B/tat"]["phong"], nv["B/tat"]["hien_thi"], nv["B/tat"]["bead"]) == ("du-an:hr-codex", "tat", None)
    assert (nv["B/mat"]["trang_thai"], nv["B/mat"]["hien_thi"], nv["B/mat"]["phong"]) == (
        "mat_ket_noi", "tat", "ca-phe")
    assert (nv["B/dao"]["hien_thi"], nv["B/dao"]["phong"]) == ("loi", "ca-phe")
    assert nv["B/la"]["phong"] == "ca-phe" and nv["B/la"]["hien_thi"] == "lam"      # dự án đã gỡ khỏi trạm
    assert "@" not in str(nv) and "ma_giao" not in str(nv)


def test_escalation_mo_cua_phieu_cuoi_thanh_can_nguoi_toi_khi_dong(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "B", "claude-1")
    p = dat_phieu(kho, "B/claude-1", bead_id="hr-7", tieu_de="Bí chỗ thuế")
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, p.giao_id, "bi", LUC)
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/claude-1", "ket_thuc": "bi"}, luc=LUC)
        kho.ghi_su_kien("hr-codex", "escalation.tao", {"escalation_id": "hr-e1", "bead_goc": "hr-7",
                                                       "giao_id": p.giao_id, "ly_do": "agent-bi"},
                        luc=LUC, bead_id="hr-7")
    x = _nv(kho)["B/claude-1"]
    assert (x["trang_thai"], x["hien_thi"], x["phong"]) == ("can_nguoi", "can_nguoi", "du-an:hr-codex")
    assert x["bead"]["bead_id"] == "hr-7" and x["bead"]["tieu_de"] == "Bí chỗ thuế"
    with kho.giao_dich():
        kho.ghi_su_kien("hr-codex", "escalation.dong", {"escalation_id": "hr-e1", "bead_goc": "hr-7",
                                                        "tra_loi": "ok"}, luc=LUC, bead_id="hr-7")
    x = _nv(kho)["B/claude-1"]
    assert (x["trang_thai"], x["phong"], x["bead"]) == ("loi", "du-an:hr-codex", None)
