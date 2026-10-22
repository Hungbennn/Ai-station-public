"""`Bd.tao` cho bead con từ plan (spec 4 §7.3 bước 2): `-p`, `--acceptance`, `--parent`; lời gọi cũ không đổi."""
from bd_gia import BdGia
from bead_gia import bead
from tram.beads.bd import Bd


def _bd(ra="hr-f.1\n"):
    goi = []
    return Bd("/r", actor="tram/giao-viec", runner=lambda a: goi.append(list(a)) or ra), goi


def test_tao_con_du_co():
    bd, goi = _bd()
    i = bd.tao("Hiện hoa hồng", loai="task", mo_ta="<!-- khoa: t1 -->\nMô tả", nhan=["b2b"], uu_tien=2,
               nghiem_thu="- Hiện đúng số", cha="hr-f")
    assert i == "hr-f.1"
    assert goi == [["-C", "/r", "create", "Hiện hoa hồng", "-t", "task", "-d", "<!-- khoa: t1 -->\nMô tả",
                    "--silent", "--actor", "tram/giao-viec", "-l", "b2b", "-p", "2", "--acceptance", "- Hiện đúng số",
                    "--parent", "hr-f"]]


def test_loi_goi_cu_khong_doi_va_uu_tien_0_van_truyen():
    bd, goi = _bd("hr-9")
    bd.tao("Bí: x", loai="decision", mo_ta="m", nhan=["tram:escalation"])
    bd.tao("x", loai="task", mo_ta="m", uu_tien=0)
    assert goi[0][-2:] == ["-l", "tram:escalation"] and goi[1][-2:] == ["-p", "0"]


def test_bd_gia_tao_con_co_cha_uu_tien_tieu_chi():
    g = BdGia([bead("hr-f", issue_type="feature")])
    i = g.tao("Con", loai="task", mo_ta="m", uu_tien=1, nghiem_thu="Đạt", cha="hr-f")
    b = g.beads[i]
    assert (i, b.parent, b.priority, b.acceptance_criteria) == ("hr-f.1", "hr-f", 1, "Đạt")
    assert [(p.depends_on_id, p.loai) for p in b.phu_thuoc] == [("hr-f", "parent-child")]
    assert g.tao("Con 2", loai="task", mo_ta="m", cha="hr-f") == "hr-f.2" and g.so_lan("tao") == 2
