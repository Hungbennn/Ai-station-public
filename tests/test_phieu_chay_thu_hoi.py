"""P1 ở tầng phiếu: `LoiThuHoi` ở lần chạy thứ hai không dọn worktree/phiếu (tiến trình có thể còn sống) và nổi lên
cho vòng khe dừng; lỗi khác của CLI (đã thu hồi) không giữ pid cũ. Toàn bộ bằng bản giả — không spawn gì."""
import threading
from types import SimpleNamespace

import pytest

import tram.tho.phieu_chay as pcm
from tram.kiem.vong_doi import LoiThuHoi


def test_loi_thu_hoi_lan_sau_khong_don_phieu(monkeypatch):
    lan, don, khoa = [], [], []

    def mot_vong(pc, nc, vk):
        lan.append(1)
        if len(lan) == 1:
            return None
        raise LoiThuHoi("x")
    monkeypatch.setattr(pcm, "_mot_vong", mot_vong)
    monkeypatch.setattr(pcm, "chuan_bi", lambda *a: SimpleNamespace(wt="/khong-dung", p=SimpleNamespace(giao_id="g")))
    monkeypatch.setattr(pcm, "dat_khoa", lambda *a, **k: True)
    monkeypatch.setattr(pcm, "go_khoa", khoa.append)
    monkeypatch.setattr(pcm, "don_phieu", lambda *a: don.append(1))
    with pytest.raises(LoiThuHoi):
        nc = SimpleNamespace(don_khe=lambda k: None, ch=SimpleNamespace(tren_may_b=False))
        pcm.chay_phieu(nc, SimpleNamespace(k=None, so=None, hop=None), None)
    assert lan == [1, 1] and don == [] and khoa == ["/khong-dung"]


def test_cli_loi_khac_sau_khi_thu_hoi_thi_xoa_pid(tmp_path, monkeypatch):
    from tho_chay_gia import dung_may, lay_phieu
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.mot_lan import chay_mot_lan
    m = dung_may(tmp_path / "worker", monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)

    def tao(boc, **kw):
        def chay(argv, **k2):
            kw["khi_bat_dau"](999999)
            raise OSError("đọc log hỏng")
        return SimpleNamespace(chay=chay)
    m.nc.tao_cli = tao
    with pytest.raises(OSError):
        chay_mot_lan(pc, m.nc, threading.Event())
    assert not so.pid.exists()
