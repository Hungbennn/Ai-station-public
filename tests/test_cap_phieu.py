from khe_duyet_gia import dang_ky_va_duyet
import json
import threading
from datetime import timedelta

from kho_phieu_gia import LUC, kho_tam
from phieu_gia import de_xuat, khoa
from tram.cau_hinh.tram import CauHinhThoTram, CauHinhTram
from tram.chu import estop
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.cap import cap_phieu
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.kho import KhoPhieu, chuoi_gio
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.su_kien.kho import KhoSuKien

CH = CauHinhTram()


def _kho(tmp_path, *khe):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_va_duyet(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]}
                               for t in khe or ("claude-1",)], luc=LUC)
    return kho


def test_cap_ghi_phieu_luot_han_giu_va_giao_nhan_khong_ma_giao(tmp_path):
    kho = _kho(tmp_path)
    kq = cap_phieu(kho, "B/claude-1", de_xuat(), bay_gio=LUC, ch=CH)
    p = kq.phieu
    assert kq.ly_do is None and p.luot == 1 and p.han_giu == "2026-10-13T03:10:00Z" and p.khe_id == "B/claude-1"
    assert kho.phieu_hieu_luc_cua_khe("B/claude-1").phieu == p
    sk = KhoSuKien(tmp_path / "su-kien.db").gan_day("hr-codex", "giao.nhan", 5)
    assert len(sk) == 1 and sk[0].du_lieu["ref_phieu"] == p.giao_id and sk[0].du_lieu["cha"] == p.repo.cha
    assert p.ma_giao not in json.dumps(sk[0].du_lieu)
    assert kho.db.execute("SELECT so_lan_chay, phut, token_ra FROM giu_ngan_sach").fetchall() == [(3, 90, 200000)]


def test_khe_dang_giu_phieu_khong_nhan_them(tmp_path):
    kho = _kho(tmp_path)
    cap_phieu(kho, "B/claude-1", de_xuat("hr-1"), bay_gio=LUC, ch=CH)
    assert cap_phieu(kho, "B/claude-1", de_xuat("hr-2"), bay_gio=LUC, ch=CH).ly_do == "khe-dang-giu-phieu"


def test_bead_dang_co_phieu_va_trung_khoa(tmp_path):
    kho = _kho(tmp_path, "claude-1", "claude-2", "claude-3")
    cap_phieu(kho, "B/claude-1", de_xuat("hr-1"), bay_gio=LUC, ch=CH)
    assert cap_phieu(kho, "B/claude-2", de_xuat("hr-1", buoc="qc"), bay_gio=LUC, ch=CH).ly_do == "bead-dang-co-phieu"
    dx = de_xuat("hr-2", khoa_chong_trung=khoa("hr-codex", de_xuat("hr-1").repo.cha, "hr-1", "code"))
    assert cap_phieu(kho, "B/claude-3", dx, bay_gio=LUC, ch=CH).ly_do == "trung-khoa"
    assert cap_phieu(kho, "B/claude-3", de_xuat("hr-3"), bay_gio=LUC, ch=CH,
                     con_hop_le=lambda d: False).ly_do == "phan-4-tu-choi"
    assert kho.luot_hien_hanh("hr-codex", "hr-2") == 0 and kho.luot_hien_hanh("hr-codex", "hr-3") == 0


def test_dieu_kien_phan_3(tmp_path):
    kho = _kho(tmp_path)
    assert cap_phieu(kho, "B/claude-9", de_xuat(), bay_gio=LUC, ch=CH).ly_do == "khe-tat"   # chưa đăng ký
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    assert cap_phieu(kho, "B/claude-1", de_xuat(), bay_gio=LUC, ch=CH).ly_do == "khe-tat"
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=True, vi_sao="", tac_nhan="dai-ca", luc=LUC)
        ngat_cau_dao(kho, "B/claude-1", ly_do="x", toi_luc=LUC + timedelta(minutes=5), luc=LUC)
    assert cap_phieu(kho, "B/claude-1", de_xuat(), bay_gio=LUC, ch=CH).ly_do == "cau-dao"
    estop.bat("thử")
    assert cap_phieu(kho, "B/claude-1", de_xuat(), bay_gio=LUC + timedelta(minutes=6), ch=CH).ly_do == "estop"
    estop.tat()
    hm = HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[CuaSo(
        loai="5h", trang_thai="biet", phan_tram=90, reset_luc="2026-10-13T05:00:00Z", doc_luc="2026-10-13T03:05:00Z")])
    with kho.giao_dich():
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=hm)
    assert cap_phieu(kho, "B/claude-1", de_xuat(), bay_gio=LUC + timedelta(minutes=6), ch=CH).ly_do == "han-muc"
    with kho.giao_dich():
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
        for i in range(2):
            kho.db.execute("INSERT INTO lan_chay VALUES (?, 'B/claude-1', 'g', 1, ?)", (f"r{i}", chuoi_gio(LUC)))
    ch2 = CauHinhTram(tho=CauHinhThoTram(lan_chay_moi_gio=2))
    assert cap_phieu(kho, "B/claude-1", de_xuat(), bay_gio=LUC + timedelta(minutes=6), ch=ch2).ly_do == "tran-lan-chay"
    assert cap_phieu(kho, "B/claude-1", de_xuat(), bay_gio=LUC + timedelta(minutes=6), ch=CH).phieu is not None


def test_hai_khe_dong_thoi_khong_cung_nhan_mot_bead(tmp_path):
    _kho(tmp_path, *(f"claude-{i}" for i in range(8)))
    rao, ra = threading.Barrier(8), []

    def chay(i):
        kho = KhoPhieu(tmp_path / "su-kien.db")
        rao.wait()
        ra.append(cap_phieu(kho, f"B/claude-{i}", de_xuat("hr-1"), bay_gio=LUC, ch=CH))
        kho.close()

    luong = [threading.Thread(target=chay, args=(i,)) for i in range(8)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert sum(k.phieu is not None for k in ra) == 1
    assert sorted({k.ly_do for k in ra if k.phieu is None}) == ["bead-dang-co-phieu"]
    assert KhoPhieu(tmp_path / "su-kien.db").luot_hien_hanh("hr-codex", "hr-1") == 1
