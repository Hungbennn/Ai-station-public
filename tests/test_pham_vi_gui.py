"""Review vòng 1 A01 (dot7-C01): kiểm rồi gửi KHÔNG nguyên tử, nên an toàn phải nằm Ở CHÍNH LỆNH GỬI. Nhóm gốc chưa gặt
(số không thể cấp lại) → mọi kênh; nhóm khác → CHỈ kênh chạy dưới UID dành riêng của principal `user` (nhân chỉ cho
trúng tiến trình của UID đó). `Nhan` là nhân GIẢ có UID: thay nhóm SAU lần kiểm cuối và GIỮA hai kênh gửi, rồi so toàn
bộ tín hiệu đã TRÚNG tiến trình. Không sudo/kill thật."""
import pytest

from test_vong_doi import PopenGia
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.gui_tin import gop_kill, kill_cuc_bo, kill_uid
from tram.kiem.han_tong import gop_kill as gop_kill_cu
from tram.kiem.vong_doi import Nhom
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.principal import Principal

QUAN_LY, KHE = 501, 502
SUDO = TienTrinh(4242, 1, 4242, 0, QUAN_LY, 1)                       # gốc: sudo root, uid thực = quản lý
LA = TienTrinh(7000, 1, 5001, QUAN_LY, QUAN_LY, 70)                  # tiến trình của quản lý mang số nhóm vừa cấp lại


class Nhan:
    """`kill(uid)(g, sig)` chỉ TRÚNG tiến trình nhóm g có uid thực = uid gửi (cansignal của macOS, không root)."""
    def __init__(self, *bang, sau_kiem=None):
        self.bang, self.sau_kiem, self.trung, self.goi = list(bang), sau_kiem, [], []

    def chup(self):
        return list(self.bang)

    def mot(self, pid):
        t = next((t for t in self.bang if t.pid == pid), None)
        if self.sau_kiem is not None:                                 # thay nhóm NGAY SAU lần kiểm cuối
            f, self.sau_kiem = self.sau_kiem, None
            f(self)
        return t

    def kill(self, uid):
        def gui(g, sig):
            self.goi.append((uid, g, sig))
            self.trung += [(t.pid, sig) for t in self.bang if t.pgid == g and t.ruid == uid]
        return gui


class PrGia:
    """Principal GIẢ: `kill_nhom` chạy dưới UID của nó (như `sudo -n -u … /bin/kill`)."""
    def __init__(self, nhan, uid, co_che="user", sau_gui=None):
        self.nhan, self.uid, self.co_che, self.sau_gui = nhan, uid, co_che, sau_gui

    def kill_nhom(self, g, sig):
        self.nhan.kill(self.uid)(g, sig)
        if self.sau_gui is not None:
            self.sau_gui(g)


def thu_hoi(nh, kill):
    n = Nhom(PopenGia(), kill=kill, chup=nh.chup, mot=nh.mot)
    n.cay()
    return n.thu_hoi(cho_term=0, cho_cuoi=0, han_gui=1)


def cap_lai(nh):
    nh.bang = [t for t in nh.bang if t.pid != 5001] + [LA]


def test_nhom_cap_lai_sau_lan_kiem_cuoi_khong_trung_ai_ngoai_uid_khe():
    nh = Nhan(SUDO, TienTrinh(5001, 4242, 5001, KHE, KHE, 11), sau_kiem=cap_lai)
    thu_hoi(nh, gop_kill(PrGia(nh, KHE).kill_nhom, nh.kill(QUAN_LY)))
    assert 7000 not in {pid for pid, _ in nh.trung}
    assert {g for uid, g, _ in nh.goi if uid == QUAN_LY} == {4242}             # cục bộ: chỉ nhóm gốc chưa gặt


def test_nhom_cap_lai_giua_hai_kenh_gui_khong_trung_ai_ngoai_uid_khe():
    nh = Nhan(SUDO, TienTrinh(5001, 4242, 5001, KHE, KHE, 11))
    pr = PrGia(nh, KHE, sau_gui=lambda g: cap_lai(nh) if g == 5001 else None)
    thu_hoi(nh, gop_kill(pr.kill_nhom, nh.kill(QUAN_LY)))
    assert (5001, 15) in nh.trung and 7000 not in {pid for pid, _ in nh.trung}
    assert {g for uid, g, _ in nh.goi if uid == QUAN_LY} == {4242}


@pytest.mark.parametrize("kenh", ["cuc-bo", "sandbox"])
def test_khong_co_kenh_theo_uid_rieng_thi_chi_gui_nhom_goc_va_khong_xac_nhan(kenh):
    nh = Nhan(SUDO, TienTrinh(5001, 4242, 5001, KHE, KHE, 11))
    kill = nh.kill(QUAN_LY) if kenh == "cuc-bo" else PrGia(nh, KHE, co_che="sandbox").kill_nhom
    assert thu_hoi(nh, kill) is False and {g for _, g, _ in nh.goi} == {4242}


def test_nhan_ra_kenh_theo_uid_rieng():
    u, s = Principal("user", "tram-k-1"), Principal("sandbox", "tram-exec")
    pk = PrincipalKiem("tram-kiem", ("/usr/bin/sudo",))
    assert kill_uid(u.kill_nhom) == u.kill_nhom and kill_uid(pk.kill_nhom) == pk.kill_nhom
    assert kill_uid(gop_kill(u.kill_nhom, kill_cuc_bo)) == u.kill_nhom and gop_kill_cu is gop_kill
    assert kill_uid(s.kill_nhom) is None and kill_uid(kill_cuc_bo) is None and kill_uid(u.boc) is None
    assert kill_uid(PrincipalKiem("tram-exec", (), "sandbox").kill_nhom) is None


def test_principal_user_phai_rieng_tung_khe(tmp_path):
    khe = ("  - {{ten: k{i}, cli: claude, principal: '{p}', thu_muc_cau_hinh: /x/{i}, ten_goi_nho: K{i}, "
           "vai_uu_tien: [coder]}}\n")
    yaml = "may_id: B\ntram_api: http://127.0.0.1:7700\nkhe:\n"
    (tmp_path / "a.yaml").write_text(yaml + khe.format(i=1, p="user:tram-k") + khe.format(i=2, p="user:tram-k"))
    with pytest.raises(ValueError, match="riêng"):
        nap_cau_hinh_tho(tmp_path / "a.yaml")
    sb = "sandbox:tram-exec"                                         # cơ chế sandbox: user dùng chung là thiết kế
    (tmp_path / "b.yaml").write_text(yaml + khe.format(i=1, p=sb) + khe.format(i=2, p=sb))
    assert len(nap_cau_hinh_tho(tmp_path / "b.yaml").khe) == 2
