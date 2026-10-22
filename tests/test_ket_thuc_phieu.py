from datetime import timedelta

import pytest

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from phieu_gia import CHA
from tram.phieu.cong_viec import cong_viec_cho, danh_dau_xong_viec, doc_quyet_toan
from tram.phieu.ghi import gia_han
from tram.phieu.ket_thuc import ket_thuc_phieu, thu_hoi
from tram.su_kien.kho import KhoSuKien


def _chay(kho, p, so_bat_dau, xong_token):
    for i in range(so_bat_dau):
        kho.db.execute("INSERT INTO lan_chay VALUES (?, ?, ?, ?, ?)", (f"r{i}", p.khe_id, p.giao_id, i + 1, "x"))
    with kho.giao_dich():
        for t in xong_token:
            kho.ghi_su_kien(p.du_an, "chay.xong", {"giao_id": p.giao_id, "token_ra": t}, luc=LUC, bead_id=p.bead_id)


def test_thu_hoi_snapshot_cha_quyet_toan_thieu_chay_xong_cong_viec_va_cham_lai(tmp_path):
    kho = kho_tam(tmp_path)
    p = dat_phieu(kho)
    _chay(kho, p, 2, [5000])                                    # lần 2 chết trước khi gửi chay.xong
    with kho.giao_dich() as db:
        gia_han(db, p.giao_id, han_giu=LUC + timedelta(minutes=27), nhip=LUC + timedelta(minutes=17))
    with kho.giao_dich():
        kq = thu_hoi(kho, kho.lay(p.giao_id), ly_do="mat-nhip", luc=LUC + timedelta(minutes=28))
    assert kq["snapshot"] == CHA
    assert kq["quyet_toan"] == {"lan_chay": 2, "thieu_chay_xong": 1, "phut": 17 + 30, "token_ra": 5000 + 66667}
    assert doc_quyet_toan(kho, p.giao_id) == kq["quyet_toan"]
    sk = KhoSuKien(tmp_path / "su-kien.db")
    th = sk.gan_day("hr-codex", "giao.thu_hoi", 1)[0]
    assert th.du_lieu == {"giao_id": p.giao_id, "luot": 1, "ly_do": "mat-nhip"} and th.bead_id == "hr-6xe1"
    assert sk.gan_day("hr-codex", "giao.snapshot", 1)[0].du_lieu == {"bead_id": "hr-6xe1", "luot": 1, "commit": CHA}
    cv = cong_viec_cho(kho)
    assert [(c.giao_id, c.ket_thuc, c.su_kien_id) for c in cv] == [(p.giao_id, "thu_hoi", th.id)]
    assert sk.yeu_cau.dang_cho("hr-codex") == {"hr-6xe1": [th.id]}
    assert kho.phieu_hieu_luc("hr-codex", "hr-6xe1") is None and kho.lay(p.giao_id).ket_thuc == "thu_hoi"
    danh_dau_xong_viec(kho, cv[0].id, LUC)
    assert cong_viec_cho(kho) == []


def test_snapshot_la_sha_cong_bo_moi_nhat(tmp_path):
    kho = kho_tam(tmp_path)
    p = dat_phieu(kho)
    with kho.giao_dich():
        for c in ("1111111", "2222222"):
            kho.ghi_su_kien("hr-codex", "giao.cong_bo", {"bead_id": "hr-6xe1", "luot": 1, "commit": c,
                                                         "ref": "tram/hr-6xe1"}, luc=LUC, bead_id="hr-6xe1")
        sk = kho.ghi_su_kien("hr-codex", "bao.bi", {"giao_id": p.giao_id}, luc=LUC, bead_id="hr-6xe1")
        kq = ket_thuc_phieu(kho, kho.lay(p.giao_id), ket_thuc="bi", su_kien_id=sk, luc=LUC, moc_cuoi=LUC)
    assert kq["snapshot"] == "2222222" and kq["quyet_toan"] == {"lan_chay": 0, "thieu_chay_xong": 0, "phut": 0,
                                                                "token_ra": 0}


def test_xong_khong_snapshot_va_khong_ket_thuc_hai_lan(tmp_path):
    kho = kho_tam(tmp_path)
    p = dat_phieu(kho)
    _chay(kho, p, 1, [1200])
    with kho.giao_dich():
        kq = ket_thuc_phieu(kho, kho.lay(p.giao_id), ket_thuc="xong", su_kien_id=1, luc=LUC,
                            moc_cuoi=LUC + timedelta(seconds=61))
    assert kq["snapshot"] is None and kq["quyet_toan"]["phut"] == 2 and kq["quyet_toan"]["token_ra"] == 1200
    b = kho.lay(p.giao_id)
    with pytest.raises(ValueError), kho.giao_dich():
        ket_thuc_phieu(kho, b, ket_thuc="bi", su_kien_id=2, luc=LUC, moc_cuoi=LUC)
    assert len(cong_viec_cho(kho)) == 1
