from khe_duyet_gia import dang_ky_va_duyet
"""Trường bổ sung lát 2f (khảo sát giao diện §1.10): T1 đội ngũ `ten`/`vi_sao_tat`, T2 `cau_dao_ngat`,
T4 phê duyệt `cau_hoi`/`khe_id`/`buoc`/`bead_goc`, T6 `suc_khoe.muc`. Chỉ THÊM khoá, khoá cũ giữ nguyên."""
from datetime import timedelta

from bead_gia import bead
from kho_phieu_gia import LUC, kho_tam
from tram.cau_hinh.tram import CauHinhTram
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.phieu.trang_thai import trang_thai_khe
from tram.su_kien.kho import KhoSuKien
from tram.suy.doi_ngu import doi_ngu
from tram.suy.nhan_vat import nhan_vat
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.van_phong import GIU_TOI_DA, suc_khoe

CH = CauHinhTram()


def _khe(kho, *ten, cli="claude"):
    with kho.giao_dich():
        dang_ky_va_duyet(kho, "B", [{"ten": t, "cli": cli, "ten_goi_nho": "x", "vai_uu_tien": ["coder"]} for t in ten],
                    luc=LUC)
        for t in ten:
            ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)


def test_t1_doi_ngu_ten_nhan_vat_va_vi_sao_tat_chi_khi_tat(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "claude-1", "claude-2", "claude-3")
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=False, vi_sao="Để dành ‮hạn mức " + "x" * 200, tac_nhan="dai-ca",
                    luc=LUC)
        bat_tat_khe(kho, "B/claude-2", bat=False, vi_sao="tạm nghỉ", tac_nhan="dai-ca", luc=LUC)
        bat_tat_khe(kho, "B/claude-2", bat=True, vi_sao="làm lại", tac_nhan="dai-ca", luc=LUC)
        bat_tat_khe(kho, "B/claude-3", bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    k = {x["khe_id"]: x for x in doi_ngu(kho, bay_gio=LUC, ch=CH)["khe"]}
    assert [k[i]["ten"] for i in ("B/claude-1", "B/claude-2", "B/claude-3")] == ["Claude 1", "Claude 2", "Claude 3"]
    v = k["B/claude-1"]["vi_sao_tat"]
    assert k["B/claude-1"]["trang_thai"] == "tat" and v.startswith("Để dành hạn mức") and len(v) == 120
    assert (k["B/claude-2"]["trang_thai"], k["B/claude-2"]["vi_sao_tat"]) == ("ranh", None)
    assert (k["B/claude-3"]["trang_thai"], k["B/claude-3"]["vi_sao_tat"]) == ("tat", None)       # rỗng → None
    assert list(k["B/claude-1"])[-2:] == ["ten", "vi_sao_tat"]                                     # chỉ thêm ở cuối


def test_t2_nhan_vat_cau_dao_ngat(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "claude-1", "claude-2")
    with kho.giao_dich():
        ngat_cau_dao(kho, "B/claude-2", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    nv = {x["khe_id"]: x for x in nhan_vat(kho, trang_thai_khe(kho, bay_gio=LUC, ch=CH), ["hr-codex"])}
    assert nv["B/claude-1"]["cau_dao_ngat"] is False
    assert nv["B/claude-2"]["cau_dao_ngat"] is True and nv["B/claude-2"]["hien_thi"] == "loi"


def _ghi(kho, loai, bead_id, **d):
    kho.ghi("hr", loai, d, bead_id=bead_id, tac_nhan="tram/giao-viec")


def test_t4_escalation_co_cau_hoi_khe_buoc_bead_goc(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    mo_ta = ("ly_do: qc-tra-ve\nbead_goc: hr-1\ngiao_id: G-1\n\nCần chọn ‮hướng " + "y" * 400
             + "\n\n<!-- ma_thao_tac: m -->")
    beads = [bead("hr-9", issue_type="decision", labels=["tram:escalation"], description=mo_ta), bead("hr-1")]
    _ghi(kho, "giao.nhan", "hr-1", giao_id="G-1", khe_id="B/claude-2", buoc="qc", vai="qc", ma_giao="bí-mật")
    _ghi(kho, "giao.nhan", "hr-1", giao_id="G-0", khe_id="B/claude-1", buoc="code", vai="coder")
    _ghi(kho, "escalation.tao", "hr-1", escalation_id="hr-9", bead_goc="hr-1", giao_id="G-1", ly_do="qc-tra-ve")
    (m,) = [x for x in gom_phe_duyet(["hr"], {"hr": beads}, kho) if x["loai"] == "escalation"]
    ct = m["chi_tiet"]
    assert (ct["khe_id"], ct["buoc"], ct["bead_goc"]) == ("B/claude-2", "qc", "hr-1")
    assert ct["cau_hoi"].startswith("Cần chọn hướng") and len(ct["cau_hoi"]) == 300
    assert "ma_thao_tac" not in ct["cau_hoi"]
    assert set(ct) == {"cau_hoi", "khe_id", "buoc", "bead_goc"} and "bí-mật" not in str(m)


def test_t4_escalation_khong_su_kien_thi_none_va_decision_chi_cau_hoi(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    beads = [bead("hr-9", issue_type="decision", labels=["tram:escalation"], description="Hỏi gì?"),
             bead("hr-8", issue_type="decision", description="Chọn A hay B?"), bead("hr-7", issue_type="decision"),
             bead("hr-6", issue_type="decision", labels=["tram:escalation"], description="Không giao")]
    _ghi(kho, "escalation.tao", "hr-1", escalation_id="hr-6", bead_goc="hr-1", giao_id=None, ly_do="khac")
    ct = {m["bead_id"]: m["chi_tiet"] for m in gom_phe_duyet(["hr"], {"hr": beads}, kho)}
    assert ct["hr-9"] == {"cau_hoi": "Hỏi gì?", "khe_id": None, "buoc": None, "bead_goc": None}
    assert ct["hr-6"] == {"cau_hoi": "Không giao", "khe_id": None, "buoc": None, "bead_goc": "hr-1"}
    assert ct["hr-8"] == {"cau_hoi": "Chọn A hay B?"} and ct["hr-7"] == {"cau_hoi": ""}


def test_t4_muc_khac_khong_them_khoa(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    beads = [bead("hr-1", labels=["cot:cho-review"], description="mô tả"), bead("hr-2", labels=["cho-duyet-spec"])]
    for m in gom_phe_duyet(["hr"], {"hr": beads}, kho):
        assert not {"cau_hoi", "khe_id", "buoc", "bead_goc"} & set(m["chi_tiet"])


def test_t6_suc_khoe_muc_cung_thu_tu_va_cung_cat_voi_ly_do():
    he_dao = {"loai": "he", "du_an": "_tram", "bead_id": None,
              "chi_tiet": {"su_kien": "khe.cau_dao_ngat", "khe_id": "B/claude-2"}}
    nv = [{"khe_id": "B/claude-1", "trang_thai": "loi"}]
    r = suc_khoe(estop_bat=True, muc=[he_dao], loi_doc={}, nhan_vat=nv)
    assert r["muc"] == [{"mau": "do", "ly_do": "Estop đang bật"},
                        {"mau": "vang", "ly_do": "Cầu dao khe B/claude-2 đang ngắt"},
                        {"mau": "vang", "ly_do": "Khe B/claude-1: lỗi lần chạy cuối"}]
    assert list(r) == ["mau", "ly_do", "muc"] and r["mau"] == "do"
    r = suc_khoe(estop_bat=True, muc=[he_dao], loi_doc={f"da-{i}": "x" for i in range(GIU_TOI_DA)}, nhan_vat=nv)
    assert len(r["muc"]) == len(r["ly_do"]) == GIU_TOI_DA and [x["ly_do"] for x in r["muc"]] == r["ly_do"]
    assert {x["mau"] for x in r["muc"]} == {"do"}
    assert suc_khoe(estop_bat=False, muc=[], loi_doc={}, nhan_vat=[]) == {"mau": "xanh", "ly_do": [], "muc": []}
