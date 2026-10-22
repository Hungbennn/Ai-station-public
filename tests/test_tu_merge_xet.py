"""TM-2 mốc 2.1 (spec `tu-merge`, design D-2): hàm thuần xét tự merge — một dòng cho mỗi Scenario; thứ tự lý do cố
định; QC/kiểm lại tính lại từ sự kiện (QC khác khe — INV-006). Không kho, không Git, không `gh`."""
from dataclasses import replace

import pytest

from tram.giao_viec.su_kien import SK
from tram.giao_viec.tu_merge_xet import (MUC, NHAN, DuKien, kiem_lai_qc, ly_do_chua_merge,
                                         ly_do_chua_merge_spec)
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import TamDung, TrangThaiTuDong

BAT = TrangThaiTuDong(replace(MAC_DINH, tu_merge=True), "7", None, None)
DU = DuKien(qc_dat=True, kiem_lai_dat=True, dung_pr=True, dau_pr_dung=True, ci="xanh")
TD = TamDung("dai-ca/dashboard", "2026-10-18T03:00:00Z", "")


def _ly(tt=BAT, *, bat_ghi=True, estop_bat=False, **dk):
    return ly_do_chua_merge(tt, replace(DU, **dk), bat_ghi=bat_ghi, estop_bat=estop_bat)


def _nut(**nut):
    return replace(BAT, cai_dat=replace(BAT.cai_dat, **nut))


@pytest.mark.parametrize("canh, ly_do", [
    ("Dự án mới thêm vào trạm (công tắc tắt)", _ly(TrangThaiTuDong(MAC_DINH, "0", None, None))),
    ("Bật cho một dự án: đủ điều kiện", _ly()),
    ("Đầu PR đổi sau khi kiểm", _ly(dau_pr_dung=False)),
    ("PR không do trạm mở", _ly(dung_pr=False)),
    ("QC trả về", _ly(qc_dat=False)),
    ("Kiểm lại không đạt / bằng chứng hết hiệu lực", _ly(kiem_lai_dat=False)),
    ("CI đang chạy", _ly(ci="dang_chay")),
    ("CI đỏ", _ly(ci="do")),
    ("Repo chưa có CI, nút CI bật (D93)", _ly(ci="rong")),
    ("Dự án tắt nút CI", _ly(_nut(dk_ci=False), ci="rong")),
    ("Đại ca đã tự gán cột", _ly(cot_ai=False)),
    ("Tắt nút cột", _ly(_nut(dk_cot=False), cot_ai=False)),
    ("Diff chạm đường dẫn tiền", _ly(hang_rao=("hang_rao_tien",))),
    ("Việc chỉ nhắc từ khoá, code không chạm", _ly(hang_rao=())),
    ("Tắt nút hàng rào vẫn chặn migration", _ly(_nut(dk_hang_rao=False), schema=("schema_duong_dan",),
                                               hang_rao=("hang_rao_co_do",))),
    ("Việc nói tới xoá dữ liệu", _ly(schema=("schema_tu_khoa",))),
    ("Agent sửa file lệnh deploy dùng, tắt nút hàng rào (D89)", _ly(_nut(dk_hang_rao=False), file_lenh=("file_lenh",))),
    ("Thiếu hai điều kiện", _ly(ci="do", hang_rao=("hang_rao_khach_thay",))),
    ("Con của feature đã duyệt", _ly()),
    ("Estop bật", _ly(estop_bat=True)),
    ("Dự án chỉ quét thử", _ly(bat_ghi=False)),
    ("Tạm dừng dự án", _ly(replace(BAT, tam_dung_du_an=TD))),
    ("Toàn trạm tạm dừng", _ly(replace(BAT, tam_dung_tram=TD))),
])
def test_moi_scenario_mot_dong(canh, ly_do):
    ky_vong = {"Dự án mới thêm vào trạm (công tắc tắt)": ["tu_merge_tat"], "Đầu PR đổi sau khi kiểm": ["dau_pr_khac"],
               "PR không do trạm mở": ["pr_khac"], "QC trả về": ["qc"],
               "Kiểm lại không đạt / bằng chứng hết hiệu lực": ["kiem_lai"], "CI đang chạy": ["ci_dang_chay"],
               "CI đỏ": ["ci_do"], "Repo chưa có CI, nút CI bật (D93)": ["ci_rong"], "Đại ca đã tự gán cột": ["cot"],
               "Dự án tắt nút CI": ["ci_rong"], "Diff chạm đường dẫn tiền": ["hang_rao_tien"],
               "Tắt nút hàng rào vẫn chặn migration": ["schema_duong_dan"],
               "Việc nói tới xoá dữ liệu": ["schema_tu_khoa"],
               "Agent sửa file lệnh deploy dùng, tắt nút hàng rào (D89)": ["file_lenh"],
               "Thiếu hai điều kiện": ["ci_do", "hang_rao_khach_thay"], "Estop bật": ["estop"],
               "Dự án chỉ quét thử": ["bat_ghi"], "Tạm dừng dự án": ["tam_dung_du_an"],
               "Toàn trạm tạm dừng": ["tam_dung_tram"]}.get(canh, [])
    assert ly_do == ky_vong


def test_nhan_loi_thuong_theo_spec():
    assert NHAN["dau_pr_khac"] == "Đầu PR khác commit đã kiểm" and NHAN["ci_do"] == "CI chưa xanh"
    assert NHAN["hang_rao_tien"] == "Chạm hàng rào: tiền/giá"
    assert NHAN["hang_rao_khach_thay"] == "Chạm hàng rào: thứ khách thấy"
    assert NHAN["schema_duong_dan"] == "Cấu trúc DB — luôn chờ Đại ca"
    assert NHAN["schema_tu_khoa"].endswith("xoá dữ liệu — luôn chờ Đại ca") and NHAN["estop"] == "Estop đang bật"
    assert MUC["schema_duong_dan"] == MUC["schema_tu_khoa"] == "loi" and MUC["ci_dang_chay"] == "tat"
    assert NHAN["file_lenh"].endswith("— luôn chờ Đại ca") and MUC["file_lenh"] == MUC["file_lenh_loi"] == "loi"


def test_thu_tu_ly_do_co_dinh():
    """Design D-2: khoá chung → QC → kiểm lại → đúng PR → đầu PR → cấu trúc DB → file lệnh (D89) → CI → cột → hàng
    rào; tắt cả ba nút vẫn còn cấu trúc DB và file lệnh."""
    het = DuKien(False, False, False, False, ("schema_duong_dan", "schema_tu_khoa"), "do", False,
                 ("hang_rao_tien", "hang_rao_co_do"), ("file_lenh",))
    tt = TrangThaiTuDong(MAC_DINH, "0", TD, TD)
    assert ly_do_chua_merge(tt, het, bat_ghi=False, estop_bat=True) == [
        "estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_merge_tat", "qc", "kiem_lai", "pr_khac",
        "dau_pr_khac", "schema_duong_dan", "schema_tu_khoa", "file_lenh", "ci_do", "cot", "hang_rao_tien",
        "hang_rao_co_do"]
    tat_nut = replace(tt, cai_dat=replace(MAC_DINH, dk_ci=False, dk_cot=False, dk_hang_rao=False))
    assert ly_do_chua_merge(tat_nut, het, bat_ghi=True, estop_bat=False)[-4:] == [
        "schema_duong_dan", "schema_tu_khoa", "file_lenh", "ci_do"]
    assert all(m in NHAN for m in ly_do_chua_merge(tt, het, bat_ghi=False, estop_bat=True))


def test_pr_spec_chi_khoa_chung_va_dau_pr():
    """D95, design D-11 — Scenario "Duyệt spec xong", "Nhánh spec đổi sau khi duyệt", "Công tắc tắt"."""
    kw = {"bat_ghi": True, "estop_bat": False}
    assert ly_do_chua_merge_spec(BAT, dung_pr=True, dau_pr_dung=True, **kw) == []
    assert ly_do_chua_merge_spec(BAT, dung_pr=True, dau_pr_dung=False, **kw) == ["dau_pr_khac"]
    assert ly_do_chua_merge_spec(TrangThaiTuDong(MAC_DINH, "0", None, None), dung_pr=True, dau_pr_dung=True,
                                 **kw) == ["tu_merge_tat"]
    assert ly_do_chua_merge_spec(replace(BAT, tam_dung_du_an=TD), dung_pr=False, dau_pr_dung=True,
                                 bat_ghi=True, estop_bat=True) == ["estop", "tam_dung_du_an", "pr_khac"]
    assert ly_do_chua_merge_spec(BAT, dung_pr=True, dau_pr_dung=True, file_lenh=("file_lenh",), **kw) == ["file_lenh"]


C, Q = "a" * 40, "b" * 40


def _ds(*them, khe_qc="B/claude-2", ket_luan="dat", dat=True):
    goc = [("giao.nhan", {"giao_id": "g-1", "luot": 1, "buoc": "code", "khe_id": "B/claude-1"}),
           ("giao.ket_thuc", {"giao_id": "g-1", "ket_thuc": "xong", "ly_do": None, "commit": C}),
           ("kiem.lai", {"giao_id": "g-1", "bead_id": "hr-1", "luot": 1, "commit": C, "digest_tieu_chi": "d",
                         "dat": dat, "nguon_kiem": "uq"}),
           ("giao.nhan", {"giao_id": "g-2", "luot": 2, "buoc": "qc", "khe_id": khe_qc}),
           ("qc.ket_qua", {"giao_id": "g-2", "commit_code": C, "commit_qc": Q, "ket_luan": ket_luan}),
           ("bead.vao_cot_3", {"commit_code": C, "commit_ban_giao": Q, "giao_id_code": "g-1", "luot_code": 1,
                              "digest_tieu_chi": "d"}),
           *them]
    return [SK(i, l, d, "2026-10-18T03:00:00Z") for i, (l, d) in enumerate(goc, 1)]


def test_kiem_lai_qc_tinh_lai_tu_su_kien():
    ds = _ds()
    v = ds[5]
    assert kiem_lai_qc(ds, v) == (True, True)
    assert kiem_lai_qc(_ds(ket_luan="tra_ve"), v) == (False, True)                 # Scenario "QC trả về"
    assert kiem_lai_qc(_ds(khe_qc="B/claude-1"), v) == (False, True)               # QC cùng khe code (INV-006)
    assert kiem_lai_qc(_ds(khe_qc=None), v) == (False, True)                       # không biết khe QC → không đạt
    assert kiem_lai_qc(_ds(dat=False), v) == (False, False)                        # Scenario "Kiểm lại không đạt"
    moi = _ds(("giao.nhan", {"giao_id": "g-3", "luot": 3, "buoc": "code", "khe_id": "B/claude-1"}))
    assert kiem_lai_qc(moi, v) == (False, False)                                   # lượt code mới chưa kiểm lại
