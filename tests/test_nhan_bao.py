import json
from datetime import timedelta

import pytest
from pydantic import ValidationError

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.tram import CauHinhTram
from tram.chu import estop
from tram.phieu.bao import ThanBao, nhan_bao
from tram.phieu.cau_dao import trang_thai_cau_dao
from tram.phieu.cong_viec import cong_viec_cho, doc_quyet_toan
from tram.phieu.kho import LuotCu
from tram.phieu.khe import dang_ky_khe
from tram.phieu.su_kien_chay import LoaiLa, ThanSuKien, nhan_su_kien_chay
from tram.phieu.yeu_cau_tho import KhongThuocMay, TrungRequest
from tram.su_kien.kho import KhoSuKien

CH = CauHinhTram()
BG = {"phien_ban": 1, "loai": "chinh-thuc", "luot": 1, "file_ban_giao": "docs/handovers/x.md", "nhanh": "tram/hr-6xe1",
      "commit": "abcdef1", "doi_chieu_nghiem_thu": [], "lenh_kiem": [], "quyet_dinh": [], "huong_da_bo": [],
      "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [], "thay_doi_vung_nhay_cam": []}


@pytest.fixture
def ds(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]}
                               for t in ("claude-1", "claude-2")], luc=LUC)
        dang_ky_khe(kho, "C", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "c", "vai_uu_tien": ["qc"]}],
                    luc=LUC)
    return kho, dat_phieu(kho), KhoSuKien(tmp_path / "su-kien.db")


def bao(p, loai="moc", request_id="r-00000001", **kw):
    return ThanBao(**{"khe_id": p.khe_id, "giao_id": p.giao_id, "luot": p.luot, "loai": loai,
                      "request_id": request_id, **kw})


def chay(p, loai, du_lieu, request_id="r-c0000001", **kw):
    return ThanSuKien(**{"khe_id": p.khe_id, "giao_id": p.giao_id, "luot": p.luot, "loai": loai,
                         "du_lieu": du_lieu, "request_id": request_id, **kw})


def test_moc_ghi_su_kien_gui_lai_cung_noi_dung_tra_ket_qua_cu_khac_noi_dung_409(ds):
    kho, p, sk = ds
    kq = nhan_bao(kho, "B", bao(p, noi_dung="mốc 1"), bay_gio=LUC, ch=CH)
    assert nhan_bao(kho, "B", bao(p, noi_dung="mốc 1"), bay_gio=LUC, ch=CH) == kq
    with pytest.raises(TrungRequest):
        nhan_bao(kho, "B", bao(p, noi_dung="mốc khác"), bay_gio=LUC, ch=CH)
    ds_moc = sk.gan_day("hr-codex", "bao.moc", 5)
    assert len(ds_moc) == 1 and ds_moc[0].tac_nhan == "tho/B/claude-1" and ds_moc[0].du_lieu["noi_dung"] == "mốc 1"
    assert p.ma_giao not in json.dumps(ds_moc[0].du_lieu)


def test_xong_ket_thuc_mot_lan_va_gui_lai_sau_khi_mat_phan_hoi(ds):
    kho, p, sk = ds
    than = bao(p, "xong", "r-xong0001", ban_giao=BG, commit="abcdef1", loi_ban_giao=["Thiếu đối chiếu"])
    kq = nhan_bao(kho, "B", than, bay_gio=LUC + timedelta(minutes=5), ch=CH)
    assert nhan_bao(kho, "B", than, bay_gio=LUC + timedelta(minutes=6), ch=CH) == kq     # HTTP gửi lại
    with pytest.raises(LuotCu):
        nhan_bao(kho, "B", bao(p, "bi", "r-bi000001", ly_do="agent"), bay_gio=LUC, ch=CH)  # kết thúc thứ hai
    assert kho.lay(p.giao_id).ket_thuc == "xong" and len(cong_viec_cho(kho)) == 1
    assert doc_quyet_toan(kho, p.giao_id)["phut"] == 5
    x = sk.gan_day("hr-codex", "bao.xong", 5)
    assert len(x) == 1 and x[0].du_lieu["loi_ban_giao"] == ["Thiếu đối chiếu"] and x[0].du_lieu["ban_giao"] == BG
    assert len(sk.gan_day("hr-codex", "tho.tu_choi", 5)) == 1


def test_can_hoi_dat_dung_mem_va_estop_khong_chan_bao(ds):
    kho, p, _ = ds
    estop.bat("thử")
    nhan_bao(kho, "B", bao(p, "can_hoi", noi_dung="Xoá cột?", loai_hoi="thao_tac_nguy_hiem"), bay_gio=LUC, ch=CH)
    assert kho.lay(p.giao_id).dung_mem == "can-hoi"
    nhan_bao(kho, "B", bao(p, "bi", "r-bi000002", ly_do="can-hoi", ban_giao={**BG, "loai": "tam",
                                                                              "buoc_tiep": ["làm tiếp"]}),
             bay_gio=LUC, ch=CH)
    assert kho.lay(p.giao_id).ket_thuc == "bi"


def test_het_han_muc_ngat_cau_dao(ds):
    kho, p, _ = ds
    nhan_bao(kho, "B", bao(p, "het_han_muc"), bay_gio=LUC, ch=CH)
    assert kho.lay(p.giao_id).ket_thuc == "het_han_muc" and trang_thai_cau_dao(kho, "B/claude-1", LUC).ngat


def test_luot_cu_khe_khac_may_khac(ds):
    kho, p, sk = ds
    with pytest.raises(LuotCu):
        nhan_bao(kho, "B", bao(p, luot=2), bay_gio=LUC, ch=CH)
    with pytest.raises(LuotCu):
        nhan_bao(kho, "B", bao(p, khe_id="B/claude-2"), bay_gio=LUC, ch=CH)
    with pytest.raises(KhongThuocMay):
        nhan_bao(kho, "C", bao(p), bay_gio=LUC, ch=CH)                              # phiếu của máy B
    with pytest.raises(KhongThuocMay):
        nhan_bao(kho, "C", bao(p, khe_id="C/claude-1"), bay_gio=LUC, ch=CH)
    assert [s.du_lieu["luot_gui"] for s in sk.gan_day("hr-codex", "tho.tu_choi", 5)] == [1, 2]


@pytest.mark.parametrize("kw", [
    {"loai": "xong"}, {"loai": "bi"}, {"loai": "bi", "ly_do": "met"}, {"loai": "can_hoi"},
    {"loai": "moc", "ly_do": "agent"}, {"loai": "moc", "loi_ban_giao": ["x"]},
    {"loai": "xong", "ban_giao": {**BG, "loai": "tam"}}, {"loai": "xong", "ban_giao": {**BG, "luot": 9}},
    {"loai": "moc", "ban_giao": {**BG, "la": 1}}, {"loai": "moc", "commit": "HEAD"}, {"loai": "moc", "khac": 1},
])
def test_cau_truc_sai_422(ds, kw):
    _, p, _ = ds
    with pytest.raises(ValidationError):
        bao(p, **kw)


def test_lan_chay_trung_khong_nhan_request_id_moi(ds):
    from tram.phieu.lan_chay import LanChaySai
    kho, p, sk = ds
    bat = chay(p, "chay.bat_dau", {"lan": 1})
    nhan_su_kien_chay(kho, "B", bat, bay_gio=LUC, ch=CH)
    with pytest.raises(LanChaySai):
        nhan_su_kien_chay(kho, "B", bat.model_copy(update={"request_id": "r-bat-moi1"}), bay_gio=LUC, ch=CH)
    xong = chay(p, "chay.xong", {"lan": 1, "ket_thuc": "xong", "token_ra": 10}, "r-xonglan1")
    kq = nhan_su_kien_chay(kho, "B", xong, bay_gio=LUC, ch=CH)
    assert nhan_su_kien_chay(kho, "B", xong, bay_gio=LUC, ch=CH) == kq
    with pytest.raises(LanChaySai):
        nhan_su_kien_chay(kho, "B", xong.model_copy(update={"request_id": "r-xongmoi1"}), bay_gio=LUC, ch=CH)
    assert kho.db.execute("SELECT COUNT(*) FROM lan_chay").fetchone()[0] == 1
    assert len(sk.gan_day("hr-codex", "chay.xong", 20)) == 1


def test_xong_chua_bat_dau_khong_ghi_hay_xet_cau_dao(ds):
    from tram.phieu.lan_chay import LanChaySai
    kho, p, sk = ds
    with pytest.raises(LanChaySai):
        nhan_su_kien_chay(kho, "B", chay(p, "chay.xong", {"lan": 1, "ket_thuc": "het_han_muc"}),
                          bay_gio=LUC, ch=CH)
    assert sk.gan_day("hr-codex", "chay.xong", 20) == []
    assert not trang_thai_cau_dao(kho, p.khe_id, LUC).ngat


def test_lan_chay_khong_vuot_ngan_sach_phieu(ds):
    from tram.phieu.lan_chay import LanChaySai, kiem_lan_chay
    kho, p, sk = ds
    p = p.model_copy(update={"ngan_sach": p.ngan_sach.model_copy(update={"so_lan_chay": 1})})
    with kho.giao_dich(), pytest.raises(LanChaySai):
        kiem_lan_chay(kho, p, "chay.bat_dau", {"lan": 2})
    assert kho.db.execute("SELECT COUNT(*) FROM lan_chay").fetchone()[0] == 0


def test_su_kien_chay_dem_lan_va_cau_dao_va_loai_la(ds):
    kho, p, sk = ds
    nhan_su_kien_chay(kho, "B", chay(p, "chay.bat_dau", {"lan": 1}), bay_gio=LUC, ch=CH)
    nhan_su_kien_chay(kho, "B", chay(p, "chay.bat_dau", {"lan": 1}), bay_gio=LUC, ch=CH)      # gửi lại
    assert kho.db.execute("SELECT COUNT(*) FROM lan_chay").fetchone()[0] == 1
    xong = {"lan": 1, "ket_thuc": "het_han_muc", "ma_thoat": 1, "token_ra": 900, "mo_hinh": "claude-x",
            "reset_luc": "2026-10-13T05:00:00Z"}
    nhan_su_kien_chay(kho, "B", chay(p, "chay.xong", xong, "r-c0000002"), bay_gio=LUC, ch=CH)
    assert trang_thai_cau_dao(kho, "B/claude-1", LUC).toi_luc == "2026-10-13T05:00:00Z"
    e = sk.gan_day("hr-codex", "chay.xong", 1)[0]
    assert e.token_ra == 900 and e.mo_hinh == "claude-x" and e.du_lieu["request_id"] == "r-c0000002"
    nhan_su_kien_chay(kho, "B", chay(p, "chay.don_rac", {"nhanh_rac": "rac/hr-6xe1-20261013T030000Z"},
                                     "r-c0000003"), bay_gio=LUC, ch=CH)
    with pytest.raises(LoaiLa):
        nhan_su_kien_chay(kho, "B", chay(p, "bao.xong", {}, "r-c0000004"), bay_gio=LUC, ch=CH)
    with pytest.raises(ValidationError):
        nhan_su_kien_chay(kho, "B", chay(p, "chay.bat_dau", {"lan": 4}, "r-c0000005"), bay_gio=LUC, ch=CH)
    with pytest.raises(LuotCu):
        nhan_su_kien_chay(kho, "B", chay(p, "chay.bat_dau", {"lan": 2}, "r-c0000006", luot=7), bay_gio=LUC, ch=CH)
