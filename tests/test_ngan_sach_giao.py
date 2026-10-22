import json

from kho_phieu_gia import LUC, kho_tam
from su_kien_gia import DA, ds, nhan, qc
from tram.cau_hinh.du_an_giao import NganSachBead, NganSachGiao, NganSachMuc
from tram.giao_viec.ngan_sach import DaDung, da_dung, du_mot_phieu, mo_chu_ky, ngan_sach_phieu
from tram.phieu.mo_hinh import NganSach

NS = NganSachGiao()
CODE, QC = ngan_sach_phieu("code", NS), ngan_sach_phieu("qc", NS)


def quyet_toan(kho, giao_id, lan, phut):
    kho.db.execute("INSERT INTO giu_ngan_sach (giao_id, so_lan_chay, phut, token_ra, quyet_toan) VALUES (?,3,90,1,?)",
                   (giao_id, json.dumps({"lan_chay": lan, "thieu_chay_xong": 0, "phut": phut, "token_ra": 0})))


def test_ngan_sach_phieu_theo_buoc_va_ghi_de():
    assert CODE == NganSach(so_lan_chay=3, phut=90, token_ra=200000)
    assert QC == NganSach(so_lan_chay=2, phut=45, token_ra=100000)
    ns = NganSachGiao(code=NganSachMuc(2, 30, 5))
    assert ngan_sach_phieu("code", ns) == NganSach(so_lan_chay=2, phut=30, token_ra=5)


def test_da_dung_quyet_toan_va_giu_truoc(tmp_path):
    kho = kho_tam(tmp_path)
    nhan(kho, "g-1", 1)
    quyet_toan(kho, "g-1", 2, 50)
    nhan(kho, "g-2", 2, buoc="qc", ngan_sach={"so_lan_chay": 2, "phut": 45, "token_ra": 1})   # đang chạy
    qc(kho, "g-2", "c1", "q1", ket_luan="tra_ve")
    assert da_dung(kho, ds(kho)) == DaDung(1, 4, 95)


def test_du_mot_phieu_lan_chay_phut_vong(tmp_path):
    kho = kho_tam(tmp_path)
    assert du_mot_phieu(kho, ds(kho), CODE, NS.bead)
    for i in range(2):
        nhan(kho, f"g-{i}", i + 1)
        quyet_toan(kho, f"g-{i}", 3, 60)                     # 6 lần, 120 phút
    assert du_mot_phieu(kho, ds(kho), CODE, NS.bead)        # còn 3 lần
    assert not du_mot_phieu(kho, ds(kho), CODE, NganSachBead(3, 8, 360))
    assert not du_mot_phieu(kho, ds(kho), CODE, NganSachBead(3, 9, 200))
    for _ in range(3):
        qc(kho, "g-x", "c", "q", ket_luan="tra_ve")
    assert not du_mot_phieu(kho, ds(kho), QC, NS.bead)      # đủ 3 vòng QC trả về


def test_chu_ky_moi_reset_va_khong_mo_hai_lan(tmp_path):
    kho = kho_tam(tmp_path)
    for i in range(3):
        nhan(kho, f"g-{i}", i + 1)
        quyet_toan(kho, f"g-{i}", 3, 90)
    assert not du_mot_phieu(kho, ds(kho), CODE, NS.bead)
    assert mo_chu_ky(kho, DA, "hr-1", 77, LUC) and not mo_chu_ky(kho, DA, "hr-1", 77, LUC)
    assert du_mot_phieu(kho, ds(kho), CODE, NS.bead) and da_dung(kho, ds(kho)) == DaDung(0, 0, 0)
    assert mo_chu_ky(kho, DA, "hr-1", 78, LUC)
