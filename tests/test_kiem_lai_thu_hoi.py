"""Hợp đồng P1 H6 (lát 3c): kiểm lại từ chối khi dấu hạn tổng `kiem-lai.dong` còn (harness S6 chưa xác nhận dọn), và
KHÔNG công nhận kết quả lệnh kiểm khi P1 báo chưa thu hồi được cây (`da_thu_hoi=False`) — ném, cổng lượt đóng, lượt sau
bị chặn. git/tar/rm thật trong `tmp_path` (boc đồng nhất), quan sát giả, không sudo."""
import pytest

from test_kiem_lai_cong import chay, cong
from test_kiem_lai_principal import ban_chep, m  # noqa: F401 — fixture `m` dùng chung
from tram.giao_viec import kiem_lai as kl
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong
from tram.kiem.chay_lenh import KetQuaLenh


def test_dau_han_tong_con_thi_khong_vao_cong_khong_chep(m, tram_home_tam):
    c = cong(m[2])
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "kiem-lai.dong").touch()                      # harness S6 quá hạn, dọn chưa xác nhận
    with pytest.raises(LoiBanChep, match="kiem-lai.dong"):
        chay(m, c)
    assert c.trang_thai() == {"trang_thai": "mo"} and ban_chep(m) == []


def test_lenh_chua_thu_hoi_thi_khong_cong_nhan_dong_cong_chan_luot_sau(m, monkeypatch):
    c = cong(m[2])
    monkeypatch.setattr(kl, "chay_mot_lenh", lambda lenh, argv, **kw: KetQuaLenh(lenh, "pass", "", "sha256:0", 0,
                                                                                 da_thu_hoi=False))
    with pytest.raises(LoiBanChep, match="chưa thu hồi"):
        chay(m, c)
    assert c.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1: LoiBanChep"} and ban_chep(m) == []
    with pytest.raises(CongDong):
        chay(m, c)
