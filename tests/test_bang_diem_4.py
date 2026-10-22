"""Bảng điểm thợ — "qua lần đầu", "bị trả về" theo spec 4 §12 + D25–D29; lọc D14, D28 (plan 2d Task 1, G2–G6)."""
from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.kho import chuoi_gio
from tram.suy.bang_diem import bang_diem
from tram.suy.diem_giao_viec import bi_tra_ve, doc_phieu_code, doc_su_kien, qua_lan_dau

DA = "hr-codex"


def phieu(kho, khe, bead, i, ket_thuc="xong", luc=LUC, **kw):
    p = dat_phieu(kho, khe, luc=luc + timedelta(minutes=i), bead_id=bead, **kw)
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, p.giao_id, ket_thuc, luc)
    return p


def ghi(kho, loai, bead, du_an=DA, **d):
    with kho.giao_dich():
        kho.ghi_su_kien(du_an, loai, d, luc=LUC, bead_id=bead)


def cong_bo(kho, p, commit):
    ghi(kho, "giao.cong_bo", p.bead_id, p.du_an, bead_id=p.bead_id, luot=p.luot, commit=commit)


def kiem(kho, bead, commit, dat=True):
    ghi(kho, "kiem.lai", bead, commit=commit, dat=dat)


def qc(kho, bead, commit, ket_luan):
    ghi(kho, "qc.ket_qua", bead, commit_code=commit, commit_qc="q" + commit, ket_luan=ket_luan)


def vao(kho, bead, giao_id, du_an=DA):
    ghi(kho, "bead.vao_cot_3", bead, du_an, bead_id=bead, giao_id_code=giao_id)


def dung_qua_lan_dau(kho):
    k = "B/claude-1"
    p1, p2, p3, _, p5 = (phieu(kho, k, f"hr-{i}", i) for i in range(1, 6))      # hr-4: chưa công bố SHA, ở mẫu
    p6 = phieu(kho, k, "hr-6", 6, can_lenh_kiem=False, lenh_kiem=[])           # spike: không xử lý riêng
    phieu(kho, k, "hr-7", 7, ket_thuc="bi")                                       # không xong: ngoài mẫu
    p8, p10, p11 = (phieu(kho, k, f"hr-{i}", i) for i in (8, 10, 11))
    phieu(kho, "B/claude-2", "hr-1", 9, buoc="qc")
    cong_bo(kho, p1, "c0")
    cong_bo(kho, p1, "c1")                                                        # D25: bản sau cùng của lượt
    kiem(kho, "hr-1", "c1")
    qc(kho, "hr-1", "c1", "dat")                                                  # qua
    for p, c in ((p2, "c2"), (p3, "c3"), (p5, "c5"), (p6, "c6"), (p8, "c8"), (p10, "c10"), (p11, "c11")):
        cong_bo(kho, p, c)
    kiem(kho, "hr-2", "c2")
    qc(kho, "hr-2", "c2", "tra_ve")                                               # QC đầu trả về
    qc(kho, "hr-2", "c2", "dat")
    kiem(kho, "hr-3", "c3", dat=False)                                            # kiểm lại đầu trượt
    kiem(kho, "hr-3", "c3")
    qc(kho, "hr-3", "c3", "dat")
    kiem(kho, "hr-5", "c5")                                                       # chờ QC: vẫn trong mẫu
    kiem(kho, "hr-6", "c6")                                                       # spike không có QC
    kiem(kho, "hr-8", "c8")
    qc(kho, "hr-9", "c8", "dat")                                                  # QC của bead khác cùng SHA
    qc(kho, "hr-10", "c10", "dat")                                                # D26: QC ghi trước kiểm lại
    kiem(kho, "hr-10", "c10")
    qc(kho, "hr-10", "c10", "tra_ve")                                             # → QC đầu sau kiểm lại trả về
    qc(kho, "hr-11", "c11", "tra_ve")                                             # D26: QC trước kiểm lại bỏ qua
    kiem(kho, "hr-11", "c11")
    qc(kho, "hr-11", "c11", "dat")                                                # → qua


def test_qua_lan_dau_qc_dau_tien_sau_kiem_lai(tmp_path):
    kho = kho_tam(tmp_path)
    dung_qua_lan_dau(kho)
    assert qua_lan_dau(doc_phieu_code(kho.db), doc_su_kien(kho.db)) == {"B/claude-1": (2, 9)}


def test_bi_tra_ve_moi_lan_vao_cot_3_mot_mau_cua_khe_trong_bang_chung(tmp_path):
    kho = kho_tam(tmp_path)
    a, b = phieu(kho, "B/claude-1", "hr-1", 0), phieu(kho, "B/claude-2", "hr-1", 1)
    c = phieu(kho, "B/claude-1", "hr-2", 2)
    phieu(kho, "B/claude-2", "hr-3", 3)                                           # code hr-3 nhưng không ở bằng chứng
    ghi(kho, "cot.tra_ve", "hr-2", gop_y="trước mọi lần vào cột 3")
    vao(kho, "hr-1", a.giao_id)
    ghi(kho, "cot.tra_ve", "hr-1", gop_y="x")
    ghi(kho, "cot.tra_ve", "hr-1", gop_y="lần hai, cùng mẫu")
    vao(kho, "hr-1", b.giao_id)                                                   # vòng mới của khe khác: không bị trả
    vao(kho, "hr-2", c.giao_id)
    vao(kho, "hr-2", c.giao_id)                                                   # vào lại trước khi bị trả về
    ghi(kho, "cot.tra_ve", "hr-2", gop_y="x")                                     # chỉ tính cho lần vào thứ hai
    vao(kho, "hr-3", "khong-co-phieu")
    ghi(kho, "cot.tra_ve", "hr-3", gop_y="x")
    assert bi_tra_ve(doc_phieu_code(kho.db), doc_su_kien(kho.db)) == {"B/claude-1": (2, 3), "B/claude-2": (0, 1)}


def test_loc_du_an_va_cua_so_theo_luc_cap_phieu(tmp_path):
    kho = kho_tam(tmp_path)
    phieu(kho, "B/claude-1", "hr-1", 1)
    p2 = phieu(kho, "B/claude-1", "hr-2", 2, luc=LUC - timedelta(days=40))
    p3 = phieu(kho, "B/claude-1", "hr-3", 3, du_an="hr-khac")
    for p in (p2, p3):
        vao(kho, p.bead_id, p.giao_id, p.du_an)
        ghi(kho, "cot.tra_ve", p.bead_id, p.du_an, gop_y="x")
    tu = chuoi_gio(LUC - timedelta(days=30))
    (h,) = bang_diem(kho.db, du_an=DA, tu=tu)
    assert (h["so_phieu"], h["so_xong"], h["qua_lan_dau_mau"], h["bi_tra_ve"], h["bi_tra_ve_mau"]) == (1, 1, 1, None, 0)
    (h,) = bang_diem(kho.db, tu=tu)
    assert (h["so_phieu"], h["bi_tra_ve"], h["bi_tra_ve_mau"]) == (2, 1.0, 1)
    (h,) = bang_diem(kho.db)
    assert (h["so_phieu"], h["qua_lan_dau_mau"], h["bi_tra_ve"], h["bi_tra_ve_mau"]) == (3, 3, 1.0, 2)


def test_bang_diem_gan_ti_le_va_mau_chi_cho_coder(tmp_path):
    kho = kho_tam(tmp_path)
    dung_qua_lan_dau(kho)
    h1, h2 = bang_diem(kho.db)
    assert (h1["khe_id"], h1["vai"], h1["so_phieu"], h1["so_xong"]) == ("B/claude-1", "coder", 10, 9)
    assert (h1["qua_lan_dau"], h1["qua_lan_dau_mau"], h1["bi_tra_ve"], h1["bi_tra_ve_mau"]) == (0.2222, 9, None, 0)
    assert (h2["vai"], h2["qua_lan_dau"], h2["qua_lan_dau_mau"], h2["bi_tra_ve"], h2["bi_tra_ve_mau"]) == (
        "qc", None, None, None, None)
