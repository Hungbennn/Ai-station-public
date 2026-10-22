"""Công bố sau `da-push` (spec 3 §6.4, §6.6, H2) — remote là repo bare cục bộ; cả hai phương án §14 đều chạy."""
import json
from datetime import timedelta

import pytest

from cong_bo_gia import commit_tho, dung_ba_kho
from git_gia import ghi, git
from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.cong_bo import CauHinhCongBo
from tram.cong_bo import da_push as dp
from tram.cong_bo.da_push import ChuaCongBoDuoc, RefTamSai, ThanDaPush, nhan_da_push
from tram.cong_bo.git import sha_remote
from tram.cong_bo.nguon import NguonKhoTho, NguonRefTam, ref_tam_cua
from tram.cong_bo.op import op_mo
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.kho import LuotCu
from tram.phieu.khe import dang_ky_khe

KHE = {"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]}
CB = CauHinhCongBo("kho-tho", thoi_gian_cho_giay=30)


@pytest.fixture
def m(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [KHE], luc=LUC)
    p = dat_phieu(kho, cha=b.cha)
    return b, kho, p


def than(p, commit, so=1, **kw):
    return ThanDaPush(**{"khe_id": p.khe_id, "giao_id": p.giao_id, "luot": p.luot, "commit": commit,
                         "ref_tam": ref_tam_cua(p.bead_id, p.luot), "request_id": f"r-day-{so:04d}", **kw})


def day(m, t, *, nguon=None, luc=LUC, cb=CB):
    b, kho, _ = m
    return nhan_da_push(kho, "B", t, bay_gio=luc, cb=cb, nguon=nguon or NguonKhoTho({"B": b.tho.parent}),
                        kho_cua=lambda du_an: b.tram)


def cong_bo(kho):
    return [json.loads(d) for (d,) in kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'giao.cong_bo'")]


def test_chua_chot_phuong_an_hoac_chua_co_kho(m, tmp_path):
    b, kho, p = m
    with pytest.raises(ChuaCongBoDuoc, match="chua-chot"):
        nhan_da_push(kho, "B", than(p, "a" * 40), bay_gio=LUC, cb=CauHinhCongBo(), nguon=None,
                     kho_cua=lambda d: b.tram)
    with pytest.raises(ChuaCongBoDuoc, match="chua-co-kho"):
        nhan_da_push(kho, "B", than(p, "a" * 40), bay_gio=LUC, cb=CB, nguon=NguonRefTam(),
                     kho_cua=lambda d: tmp_path / "x")


def test_cong_bo_hai_moc_noi_tiep_va_gui_lai_cung_request(m):
    b, kho, p = m
    c1 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"x.txt": "1"})
    kq = day(m, than(p, c1))
    assert kq == {"cong_bo": True, "commit": c1, "ref": "tram/hr-6xe1"} and day(m, than(p, c1)) == kq
    c2 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"y.txt": "2"}, cha=c1)
    assert day(m, than(p, c2, so=2))["cong_bo"] and sha_remote(b.tram, "tram/hr-6xe1", timeout=30) == c2
    assert cong_bo(kho) == [{"bead_id": "hr-6xe1", "luot": 1, "commit": c, "ref": "tram/hr-6xe1"} for c in (c1, c2)]
    assert day(m, than(p, c2, so=3)) == {"cong_bo": True, "commit": c2, "ref": "tram/hr-6xe1"} and len(cong_bo(kho)) == 2


def test_the_chan_ref_tam_va_han_giu(m):
    b, kho, p = m
    c1 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"x.txt": "1"})
    with pytest.raises(RefTamSai):
        day(m, than(p, c1, ref_tam="tram/luot/hr-6xe1/9"))
    with pytest.raises(LuotCu):
        day(m, than(p, c1, luot=2, ref_tam="tram/luot/hr-6xe1/2"))
    assert kho.db.execute("SELECT COUNT(*) FROM su_kien WHERE loai = 'tho.tu_choi'").fetchone()[0] == 1
    assert day(m, than(p, c1), luc=LUC + timedelta(minutes=9)) == {"cong_bo": False, "ly_do": "sap-het-han-giu"}


def test_khong_thay_commit_va_khong_phai_hau_due(m):
    b, kho, p = m
    assert day(m, than(p, "b" * 40)) == {"cong_bo": False, "ly_do": "khong-thay-commit"}
    git(b.tho, "checkout", "-q", "--orphan", "la")
    git(b.tho, "rm", "-rfq", ".")
    la = ghi(b.tho, {"z.txt": "la"}, "mồ côi")
    git(b.tho, "branch", "-f", ref_tam_cua(p.bead_id, p.luot), la)
    assert day(m, than(p, la, so=2)) == {"cong_bo": False, "ly_do": "khong-phai-hau-due"}
    assert day(m, than(p, la, so=2)) == {"cong_bo": False, "ly_do": "khong-phai-hau-due"}     # đã nhớ theo request
    assert sha_remote(b.tram, "tram/hr-6xe1", timeout=30) is None and cong_bo(kho) == []


def test_nhanh_bi_day_ngoai_luong(m):
    b, kho, p = m
    khac = commit_tho(b, "ngoai-luong", {"khac.txt": "?"})
    git(b.tho, "push", "-q", "origin", f"{khac}:refs/heads/tram/hr-6xe1")       # ai đó đẩy thẳng ref công bố
    c1 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"x.txt": "1"})
    assert day(m, than(p, c1)) == {"cong_bo": False, "ly_do": "nhanh-bi-day-ngoai-luong"}
    assert cong_bo(kho) == [] and op_mo(kho, "hr-codex", "hr-6xe1") is None


def test_thu_hoi_khi_push_dang_bay_thi_hoan_tac_h2(m, monkeypatch):
    b, kho, p = m
    c1 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"x.txt": "1"})
    that = dp.day_cas

    def day_roi_thu_hoi(*a, **kw):
        kq = that(*a, **kw)
        with kho.giao_dich() as db:                                            # bộ canh/gỡ máy thu hồi giữa chừng
            danh_dau_ket_thuc(db, p.giao_id, "thu_hoi", LUC)
        return kq
    monkeypatch.setattr(dp, "day_cas", day_roi_thu_hoi)
    with pytest.raises(LuotCu):
        day(m, than(p, c1))
    assert sha_remote(b.tram, "tram/hr-6xe1", timeout=30) is None and cong_bo(kho) == []
    assert kho.db.execute("SELECT trang_thai FROM cong_bo_op").fetchone()[0] == "hoan_tac"


def test_mat_phan_hoi_remote_da_nhan_doi_soat_ghi_cong_bo_mot_lan(m, monkeypatch):
    b, kho, p = m
    c1 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"x.txt": "1"})
    that = dp.day_cas
    monkeypatch.setattr(dp, "day_cas", lambda *a, **kw: (that(*a, **kw), "khong_ro")[1])
    assert day(m, than(p, c1)) == {"cong_bo": False, "ly_do": "khong-ro"}
    assert day(m, than(p, c1), luc=LUC + timedelta(seconds=10))["cong_bo"] is True    # đối soát: remote đã nhận
    assert cong_bo(kho) == [{"bead_id": "hr-6xe1", "luot": 1, "commit": c1, "ref": "tram/hr-6xe1"}]


def test_mat_phan_hoi_push_khong_toi_cho_du_lau_moi_bo(m, monkeypatch):
    b, kho, p = m
    c1 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"x.txt": "1"})
    that = dp.day_cas
    monkeypatch.setattr(dp, "day_cas", lambda *a, **kw: "khong_ro")
    assert day(m, than(p, c1)) == {"cong_bo": False, "ly_do": "khong-ro"}
    assert day(m, than(p, c1), luc=LUC + timedelta(seconds=10)) == {"cong_bo": False, "ly_do": "dang-cong-bo"}
    monkeypatch.setattr(dp, "day_cas", that)
    assert day(m, than(p, c1), luc=LUC + timedelta(seconds=61))["cong_bo"] is True
    assert kho.db.execute("SELECT trang_thai FROM cong_bo_op ORDER BY id").fetchall() == [("bo",), ("xong",)]


def test_phuong_an_ref_tam_va_don_ref_luot_cu(m):
    b, kho, p = m
    c1 = commit_tho(b, ref_tam_cua(p.bead_id, p.luot), {"x.txt": "1"})
    git(b.tho, "push", "-q", "origin", f"{c1}:refs/heads/tram/luot/hr-6xe1/1")
    assert day(m, than(p, c1), nguon=NguonRefTam(), cb=CauHinhCongBo("ref-tam", thoi_gian_cho_giay=30))["cong_bo"]
    assert sha_remote(b.tram, "tram/hr-6xe1", timeout=30) == c1
