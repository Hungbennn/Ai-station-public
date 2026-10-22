import sqlite3

import pytest

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.phieu.ghi import danh_dau_ket_thuc, dat_dung_mem, giao_id_moi
from tram.phieu.kho import KhoPhieu, LuotCu
from tram.su_kien.kho import KhoSuKien


def test_cap_luot_va_giao_id_tang_dan(tmp_path):
    kho = kho_tam(tmp_path)
    a = dat_phieu(kho, "B/claude-1", bead_id="hr-1")
    danh = kho.lay(a.giao_id)
    assert a.giao_id == "g-20261013-0001" and a.luot == 1 and danh.trang_thai == "hieu_luc"
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, a.giao_id, "thu_hoi", LUC)
    b = dat_phieu(kho, "B/claude-2", bead_id="hr-1")
    assert b.giao_id == "g-20261013-0002" and b.luot == 2 and kho.luot_hien_hanh("hr-codex", "hr-1") == 2


def test_mot_phieu_hieu_luc_moi_bead_moi_khe_moi_khoa(tmp_path):
    kho = kho_tam(tmp_path)
    dat_phieu(kho, "B/claude-1", bead_id="hr-1")
    with pytest.raises(sqlite3.IntegrityError):
        dat_phieu(kho, "B/claude-2", bead_id="hr-1")                    # cùng bead
    with pytest.raises(sqlite3.IntegrityError):
        dat_phieu(kho, "B/claude-1", bead_id="hr-2")                    # cùng khe
    with pytest.raises(sqlite3.IntegrityError):
        dat_phieu(kho, "B/claude-2", bead_id="hr-3", khoa_chong_trung=kho.phieu_hieu_luc_cua_khe(
            "B/claude-1").phieu.khoa_chong_trung)                         # cùng khoá chống trùng
    assert kho.luot_hien_hanh("hr-codex", "hr-2") == 0                   # giao dịch hỏng không để lại gì
    assert [b.phieu.bead_id for b in kho.cac_phieu_hieu_luc()] == ["hr-1"]


def test_giao_dich_loi_thi_lui_ca_su_kien(tmp_path):
    kho = kho_tam(tmp_path)
    with pytest.raises(RuntimeError):
        with kho.giao_dich() as db:
            kho.ghi_su_kien("hr-codex", "giao.nhan", {"x": 1}, luc=LUC, bead_id="hr-1")
            giao_id_moi(db, LUC)
            raise RuntimeError("crash")
    assert KhoSuKien(tmp_path / "su-kien.db").id_moi_nhat() == 0
    assert giao_id_moi(kho.db, LUC) == "g-20261013-0001"


def test_khoi_dong_lai_doc_lai_phieu_va_ma_giao(tmp_path):
    kho = kho_tam(tmp_path)
    p = dat_phieu(kho)
    kho.close()
    lai = KhoPhieu(tmp_path / "su-kien.db")
    b = lai.phieu_hieu_luc("hr-codex", "hr-6xe1")
    assert b.phieu == p and b.phieu.ma_giao == p.ma_giao and lai.phieu_hieu_luc_cua_khe("B/claude-1") == b


def test_the_chan(tmp_path):
    kho = kho_tam(tmp_path)
    p = dat_phieu(kho)
    assert kho.kiem_the_chan("B/claude-1", p.giao_id, p.luot).phieu == p
    for khe, giao, luot in (("B/claude-1", p.giao_id, 2), ("B/claude-2", p.giao_id, 1),
                            ("B/claude-1", "g-20261013-9999", 1), ("B/claude-1", None, None)):
        with pytest.raises(LuotCu) as e:
            kho.kiem_the_chan(khe, giao, luot)
        assert e.value.thu_hoi is False
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, p.giao_id, "thu_hoi", LUC)
    with pytest.raises(LuotCu) as e:
        kho.kiem_the_chan("B/claude-1", p.giao_id, 1)
    assert e.value.thu_hoi and e.value.bead_id == "hr-6xe1" and e.value.luot_dung == 1
    with kho.giao_dich():
        kho.ghi_tu_choi(e.value, khe_id="B/claude-1", giao_id=p.giao_id, luot=1, luc=LUC)
    sk = KhoSuKien(tmp_path / "su-kien.db").gan_day("hr-codex", "tho.tu_choi", 5)
    assert sk[0].du_lieu == {"khe_id": "B/claude-1", "giao_id": p.giao_id, "bead_id": "hr-6xe1", "luot_gui": 1,
                             "luot_dung": 1} and sk[0].bead_id == "hr-6xe1"


def test_luot_moi_hon_chan_phieu_cu_ke_ca_khi_phieu_cu_con_trong_kho(tmp_path):
    kho = kho_tam(tmp_path)
    p = dat_phieu(kho)
    kho.db.execute("UPDATE luot_bead SET luot = 5")
    with pytest.raises(LuotCu):
        kho.kiem_the_chan("B/claude-1", p.giao_id, p.luot)


def test_phieu_theo_giao_id_chi_tra_ma_giao_khi_con_hieu_luc(tmp_path):
    kho = kho_tam(tmp_path)
    p = dat_phieu(kho, buoc="qc")
    assert kho.phieu_theo_giao_id(p.giao_id) == {"du_an": "hr-codex", "vai": "qc", "ma_giao": p.ma_giao,
                                                 "con_hieu_luc": True}
    with kho.giao_dich() as db:
        dat_dung_mem(db, p.giao_id, "can-hoi")
        danh_dau_ket_thuc(db, p.giao_id, "xong", LUC)
    assert kho.lay(p.giao_id).dung_mem == "can-hoi"
    assert kho.phieu_theo_giao_id(p.giao_id)["ma_giao"] is None and kho.phieu_theo_giao_id("g-x") is None
    with pytest.raises(ValueError), kho.giao_dich() as db:
        danh_dau_ket_thuc(db, p.giao_id, "xong", LUC)                   # báo kết thúc thứ hai
