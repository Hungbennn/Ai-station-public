"""Thợ đưa commit lên ref tạm + báo da-push, thử lại kết quả tạm (spec 3 §6.4) — remote bare cục bộ, trạm giả."""
import time

from cong_bo_gia import dung_ba_kho
from git_gia import git
from phieu_gia import de_xuat
from tram.cong_bo.git import sha_remote
from tram.phieu.mo_hinh import Phieu, sinh_ma_giao
from tram.tho.day import day_va_cong_bo, luu_wip, than_da_push, xoa_ref_tam


def phieu(cha):
    return Phieu(**de_xuat("hr-1", cha=cha).model_dump(), giao_id="g-20261013-0001", luot=2, khe_id="B/claude-1",
                 han_giu="2026-10-13T03:10:00Z", ma_giao=sinh_ma_giao())


class Khach:
    def __init__(self, *tl):
        self.tl, self.da = list(tl), []

    def goi(self, method, duong, than=None, *, xac_thuc=True):
        self.da.append(than)
        return self.tl.pop(0)


def test_luu_wip_va_kho_tho_chi_dat_nhanh_cuc_bo(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    (b.tho / "moi.txt").write_text("x")
    c = luu_wip(b.tho, "wip: dừng mềm")
    assert git(b.tho, "log", "-1", "--format=%s") == "wip: dừng mềm" and luu_wip(b.tho, "khong doi") == c
    p, k = phieu(b.cha), Khach((200, {"cong_bo": True, "commit": c}))
    assert day_va_cong_bo(b.tho, p, c, khach=k, phuong_an="kho-tho", han=time.monotonic() + 30) == "cong_bo"
    assert git(b.tho, "rev-parse", "tram/luot/hr-1/2") == c and sha_remote(b.tho, "tram/luot/hr-1/2", timeout=30) is None
    assert k.da == [than_da_push(p, c)] and k.da[0]["request_id"] == than_da_push(p, c)["request_id"]
    xoa_ref_tam(b.tho, p)
    assert git(b.tho, "branch", "--list", "tram/luot/hr-1/2") == ""


def test_ref_tam_push_len_origin_va_thu_lai_ket_qua_tam(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    (b.tho / "moi.txt").write_text("x")
    c, ngu = luu_wip(b.tho, "moc"), []
    k = Khach((503, {"ly_do": "chua-chot-phuong-an"}), (200, {"cong_bo": False, "ly_do": "khong-ro"}),
              (200, {"cong_bo": True}))
    kq = day_va_cong_bo(b.tho, phieu(b.cha), c, khach=k, phuong_an="ref-tam", han=time.monotonic() + 30,
                        cho=0.01, ngu=ngu.append)
    assert kq == "cong_bo" and len(k.da) == 3 and len(ngu) == 2
    assert sha_remote(b.tho, "tram/luot/hr-1/2", timeout=30) == c


def test_ket_qua_dut_khoat_va_het_han(tmp_path, monkeypatch):
    b = dung_ba_kho(tmp_path, monkeypatch)
    p, h = phieu(b.cha), time.monotonic() + 30
    assert day_va_cong_bo(b.tho, p, b.cha, khach=Khach((200, {"ly_do": "nhanh-bi-day-ngoai-luong"})),
                          phuong_an="kho-tho", han=h) == "ngoai-luong"
    assert day_va_cong_bo(b.tho, p, b.cha, khach=Khach((409, {"ly_do": "luot-cu"})), phuong_an="kho-tho",
                          han=h) == "luot-cu"
    assert day_va_cong_bo(b.tho, p, b.cha, khach=Khach(*[(200, {"ly_do": "dang-cong-bo"})] * 50),
                          phuong_an="kho-tho", han=time.monotonic() + 0.2, cho=0.05) == "chua-cong-bo"
