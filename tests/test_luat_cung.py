from pathlib import Path

from tram.beads.mo_hinh import Bead, PhuThuoc
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.cham_cot.luat_cung import bi_chan_boi, kiem, quyet_dinh_da_chot

DU_AN = DuAn("hr", Path("/r"), None, {
    "tien": HangRao(tu_khoa=("hoa hồng", "giá tour"), duong_dan=("*app/Modules/Fin/*",)),
    "quyen": HangRao(nhan=("quyen",)),
})


def bead(id="hr-1", title="", description="", issue_type="task", status="open",
         labels=(), phu_thuoc=()):
    return Bead(id, title, description, "", "", "", status, issue_type,
                tuple(labels), tuple(phu_thuoc), "2026-10-12T00:00:00Z")


def test_khong_cham_gi():
    kq = kiem(bead(title="Sửa nút lưu ở trang hồ sơ"), DU_AN, {})
    assert kq.cham == () and not kq.ep_cot_2


def test_tu_khoa_khong_phan_biet_hoa_thuong_co_dau():
    kq = kiem(bead(title="Đổi cách tính HOA HỒNG sale"), DU_AN, {})
    assert kq.ep_cot_2 and "tien" in kq.cham[0]


def test_tu_khoa_phai_tron_tu():
    assert kiem(bead(title="giá tourist"), DU_AN, {}).cham == ()


def test_duong_dan_khop_glob():
    kq = kiem(bead(description="Lỗi ở erp/app/Modules/Fin/Services/X.php dòng 71"), DU_AN, {})
    assert kq.ep_cot_2 and "erp/app/Modules/Fin/Services/X.php" in kq.cham[0]


def test_nhan():
    assert kiem(bead(labels=["quyen"]), DU_AN, {}).ep_cot_2


def test_da_chot_bang_decision_dong():
    dec = bead(id="hr-d", issue_type="decision", status="closed")
    b = bead(title="hoa hồng", phu_thuoc=[PhuThuoc("hr-d", "blocks")])
    kq = kiem(b, DU_AN, {"hr-d": dec})
    assert kq.cham and kq.da_chot and not kq.ep_cot_2


def test_decision_chua_dong_khong_tinh_la_chot():
    dec = bead(id="hr-d", issue_type="decision", status="open")
    b = bead(title="hoa hồng", phu_thuoc=[PhuThuoc("hr-d", "blocks")])
    assert kiem(b, DU_AN, {"hr-d": dec}).ep_cot_2


def test_da_chot_bang_adr():
    assert not kiem(bead(title="hoa hồng theo ADR-0083"), DU_AN, {}).ep_cot_2


def test_bead_decision_mo_luon_cot_2():
    assert kiem(bead(issue_type="decision"), DU_AN, {}).ep_cot_2


def test_bi_chan_boi_bead_chua_dong():
    chan = bead(id="hr-9", status="in_progress")
    b = bead(phu_thuoc=[PhuThuoc("hr-9", "blocks"), PhuThuoc("hr-0", "parent-child")])
    assert kiem(b, DU_AN, {"hr-9": chan}).bi_chan_boi == ("hr-9",)


def test_ly_do_doc_duoc():
    assert "Chạm hàng rào" in kiem(bead(title="hoa hồng"), DU_AN, {}).ly_do()


def test_adr_phai_tron_tu():
    assert kiem(bead(title="hoa hồng ADR-00831"), DU_AN, {}).ep_cot_2
    assert kiem(bead(title="hoa hồng XADR-0083"), DU_AN, {}).ep_cot_2
    assert not kiem(bead(title="hoa hồng ADR-0083."), DU_AN, {}).ep_cot_2


def test_decision_dong_qua_parent_child_khong_tinh_chot():
    dec = bead(id="hr-d", issue_type="decision", status="closed")
    b = bead(title="hoa hồng", phu_thuoc=[PhuThuoc("hr-d", "parent-child")])
    assert kiem(b, DU_AN, {"hr-d": dec}).ep_cot_2


def test_decision_dong_qua_related_khong_tinh_chot():
    dec = bead(id="hr-d", issue_type="decision", status="closed")
    b = bead(title="hoa hồng", phu_thuoc=[PhuThuoc("hr-d", "related")])
    assert kiem(b, DU_AN, {"hr-d": dec}).ep_cot_2


# --- Lát 2a: phụ thuộc không có trong snapshot → fail-closed (spec §5.2 mục 3) ---

def test_phu_thuoc_blocks_khong_co_trong_snapshot_van_chan():
    b = bead(phu_thuoc=[PhuThuoc("hr-mat", "blocks")])
    assert kiem(b, DU_AN, {}).bi_chan_boi == ("hr-mat",)


def test_phu_thuoc_blocks_khong_co_trong_snapshot_khong_tinh_la_chot():
    kq = kiem(bead(title="hoa hồng", phu_thuoc=[PhuThuoc("hr-mat", "blocks")]), DU_AN, {})
    assert not kq.da_chot and kq.ep_cot_2


def test_phu_thuoc_khong_phai_blocks_khong_co_trong_snapshot_khong_chan():
    b = bead(phu_thuoc=[PhuThuoc("hr-mat", "parent-child"), PhuThuoc("hr-mat2", "related")])
    assert kiem(b, DU_AN, {}).bi_chan_boi == ()


def test_ham_cong_khai_quyet_dinh_va_bi_chan():
    dong = bead(id="hr-d1", issue_type="decision", status="closed")
    mo = bead(id="hr-d2", issue_type="decision", status="open")
    viec_dong = bead(id="hr-t", status="closed")
    lien_quan = bead(id="hr-d3", issue_type="decision", status="closed")
    b = bead(phu_thuoc=[PhuThuoc("hr-d1", "blocks"), PhuThuoc("hr-d2", "blocks"), PhuThuoc("hr-t", "blocks"),
                        PhuThuoc("hr-d3", "related"), PhuThuoc("hr-mat", "blocks")])
    theo_id = {x.id: x for x in (dong, mo, viec_dong, lien_quan)}
    assert [x.id for x in quyet_dinh_da_chot(b, theo_id)] == ["hr-d1"]
    assert bi_chan_boi(b, theo_id) == ("hr-d2", "hr-mat")
