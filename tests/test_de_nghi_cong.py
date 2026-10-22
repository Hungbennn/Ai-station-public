"""TC Task 5 (design D-7, D84, D103): cổng việc mới là hàm thuần đọc sự kiện — từng dòng của D-7 và Scenario "QC đạt",
"Kiểm lại không đạt", "Việc spike"; lượt không nằm trong bằng chứng thì bỏ; việc gốc đóng thì bỏ."""
import pytest

from tram.de_nghi.cong import cong_viec_moi, luot_trong_bang_chung
from tram.giao_viec.su_kien import SK

C1, C2, Q1 = "c" * 40, "d" * 40, "e" * 40


def ds_tu(*dong) -> list[SK]:
    return [SK(i + 1, loai, d, "2026-10-18T03:00:00Z") for i, (loai, d) in enumerate(dong)]


DN = ("bao.viec_moi", {"giao_id": "g-1", "luot": 1})
KT1 = ("giao.ket_thuc", {"giao_id": "g-1", "luot": 1, "buoc": "code", "ket_thuc": "xong", "ly_do": None})
KL1 = ("kiem.lai", {"giao_id": "g-1", "luot": 1, "commit": C1, "dat": True})
DN_QC = ("bao.viec_moi", {"giao_id": "g-2", "luot": 2})
QC_DAT = ("qc.ket_qua", {"giao_id": "g-2", "commit_code": C1, "commit_qc": Q1, "ket_luan": "dat", "ly_do": None})
VC3 = ("bead.vao_cot_3", {"giao_id_code": "g-1", "luot_code": 1, "commit_code": C1, "commit_ban_giao": Q1})


def test_qc_dat_ca_luot_code_lan_luot_qc_duoc_ghi():
    """Scenario "QC đạt" — lượt code 1 và lượt QC 2 đều trong bằng chứng; ghi SAU `bead.vao_cot_3`."""
    ds = ds_tu(DN, KT1, KL1, DN_QC, QC_DAT, VC3)
    assert luot_trong_bang_chung(ds, ds[5]) == {"g-1", "g-2"}
    assert cong_viec_moi(ds, "g-1", 1, viec_dong=False) == ("ghi", 6)
    assert cong_viec_moi(ds, "g-2", 4, viec_dong=False) == ("ghi", 6)
    assert cong_viec_moi(ds[:5], "g-1", 1, viec_dong=False) == ("cho", None)        # QC đạt nhưng chưa vào cột 3


def test_viec_spike_khong_qc():
    """Scenario "Việc spike": kiểm tài liệu đạt, vào cột 3 với commit_ban_giao = commit_code."""
    ds = ds_tu(DN, KT1, ("kiem.lai", {"giao_id": "g-1", "luot": 1, "commit": C1, "dat": True, "ket_qua": []}),
               ("bead.vao_cot_3", {"giao_id_code": "g-1", "luot_code": 1, "commit_code": C1, "commit_ban_giao": C1}))
    assert cong_viec_moi(ds, "g-1", 1, viec_dong=False) == ("ghi", 4)


@pytest.mark.parametrize("dong", [
    [("giao.ket_thuc", {**KT1[1], "ket_thuc": "bi", "ly_do": "agent"})],                   # phiếu không xong
    [("giao.ket_thuc", {**KT1[1], "ket_thuc": "thu_hoi", "ly_do": "khe-tat"})],
    [("giao.ket_thuc", {**KT1[1], "ly_do": "thieu-ban-giao"})],                            # bao.xong không hợp lệ
    [KT1, ("kiem.lai", {**KL1[1], "dat": False})],                                          # "Kiểm lại không đạt"
    [KT1, KL1, ("qc.ket_qua", {**QC_DAT[1], "ket_luan": "tra_ve"})],                        # QC sau kiểm lại trả về
    [KT1, KL1, ("qc.ket_qua", {**QC_DAT[1], "ket_luan": "khong_cong_nhan", "ly_do": "qc-doi-ma"})],
])
def test_luot_code_khong_dat_bi_bo(dong):
    assert cong_viec_moi(ds_tu(DN, *dong), "g-1", 1, viec_dong=False) == ("bo", "luot-khong-dat")


@pytest.mark.parametrize("qc", [{**QC_DAT[1], "ket_luan": "tra_ve"}, {**QC_DAT[1], "ket_luan": "khong_cong_nhan"}])
def test_luot_qc_khong_dat_bi_bo(qc):
    assert cong_viec_moi(ds_tu(KT1, KL1, DN_QC, ("qc.ket_qua", qc)), "g-2", 3, viec_dong=False) == (
        "bo", "luot-khong-dat")


def test_luot_khong_trong_bang_chung_bi_bo():
    """Lượt code 1 kiểm lại đạt nhưng QC trả về; lượt code 3 mới là bằng chứng → đề nghị của lượt 1 không được ghi,
    dù dòng QC trả về đã bị "cửa sổ" sau `cot.tra_ve` che (dòng cuối của D-7)."""
    c3 = ("bead.vao_cot_3", {"giao_id_code": "g-3", "luot_code": 3, "commit_code": C2, "commit_ban_giao": Q1})
    ds = ds_tu(DN, KT1, KL1, c3)
    assert cong_viec_moi(ds, "g-1", 1, viec_dong=False) == ("bo", "luot-khong-dat")
    ds2 = ds_tu(DN, KT1, KL1, ("qc.ket_qua", {**QC_DAT[1], "commit_qc": C2}), VC3)          # QC đạt ở commit khác
    assert cong_viec_moi(ds2, "g-2", 1, viec_dong=False) == ("bo", "luot-khong-dat")


def test_viec_goc_dong_thi_bo_va_vao_cot_3_truoc_de_nghi_khong_tinh():
    assert cong_viec_moi(ds_tu(DN, KT1, KL1), "g-1", 1, viec_dong=True) == ("bo", "viec-da-dong")
    assert cong_viec_moi(ds_tu(DN, KT1, KL1, QC_DAT, VC3), "g-1", 1, viec_dong=True) == ("bo", "viec-da-dong")
    ds = ds_tu(VC3, DN)                                                                     # cột 3 của vòng trước
    assert cong_viec_moi(ds, "g-1", 2, viec_dong=False) == ("cho", None)
