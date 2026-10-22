"""Trạng thái bền phía thợ: sổ khe, hộp thư đi, CLI mồ côi, khoá worktree (spec 3 §6.6, §7.2, §8.3, H1)."""
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

from tram.han_muc.mo_hinh import HanMuc
from tram.tho.cau_hinh_chay import CauHinhChay
from tram.tho.hop_thu import HopThu
from tram.tho.khach import LoiKhachTram
from tram.tho.mo_coi import con_song, dat_khoa, go_khoa
from tram.tho.so_khe import SoKhe, TrangThaiPhieu

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


class KhachGia:
    def __init__(self, *ma):
        self.ma, self.da = list(ma), []

    def goi(self, method, duong, than=None, *, xac_thuc=True):
        m = self.ma.pop(0)
        if m is None:
            raise LoiKhachTram("mất mạng")
        self.da.append((duong, than))
        return m, {"ma": m}


def test_so_khe_quyen_va_trang_thai_phieu(tmp_path):
    s = SoKhe("B", "claude-1", tmp_path)
    assert s.goc == tmp_path / "tho" / "B" / "claude-1" and oct(s.goc.stat().st_mode)[-3:] == "700"
    assert s.hang_doi == tmp_path / "hang-doi" / "B" / "claude-1" and s.doc_phieu() is None
    s.luu_phieu(TrangThaiPhieu(phieu={"giao_id": "g-1", "ma_giao": "bi-mat"}, nhan_luc="2026-10-13T03:00:00Z", lan=2))
    assert oct((s.goc / "phieu.json").stat().st_mode)[-3:] == "600"
    assert SoKhe("B", "claude-1", tmp_path).doc_phieu().lan == 2
    s.xoa_phieu()
    assert s.doc_phieu() is None


def test_tran_cuc_bo_cau_dao_va_han_muc(tmp_path):
    s, ch = SoKhe("B", "claude-1", tmp_path), CauHinhChay(lan_chay_moi_gio=2, lan_chay_moi_ngay=3)
    for phut in (200, 50, 10):
        s.ghi_lan_chay(LUC - timedelta(minutes=phut))
    assert not s.con_cho_chay(LUC, ch)                                       # 3 trong 24 giờ
    assert SoKhe("B", "claude-2", tmp_path).con_cho_chay(LUC, ch)
    s.ngat_cau_dao(LUC + timedelta(minutes=60), "het-han-muc")
    assert s.cau_dao_ngat(LUC) and not s.cau_dao_ngat(LUC + timedelta(minutes=61))
    hm = HanMuc(khe_id="B/claude-1", nguon="stream")
    s.luu_han_muc(hm)
    assert s.doc_han_muc() == hm


def test_hop_thu_ghi_truoc_gui_dung_thu_tu_va_gui_lai_sau_restart(tmp_path):
    h = HopThu(tmp_path)
    h.them("/api/tho/su-kien", {"request_id": "r-1", "loai": "chay.bat_dau"})
    kq = h.gui_mot(KhachGia(503), "/api/tho/su-kien", {"request_id": "r-2", "loai": "chay.xong"})
    assert kq is None and [d["than"]["request_id"] for d in h.cho_gui()] == ["r-1", "r-2"]
    lai = HopThu(tmp_path)                                                    # tiến trình khởi động lại
    k = KhachGia(None)
    assert lai.gui(k) == [] and len(lai.cho_gui()) == 2
    k = KhachGia(200, 409)
    ra = lai.gui(k)
    assert [x.than["request_id"] for x in ra] == ["r-1", "r-2"] and ra[1].ma == 409
    assert [d[1]["request_id"] for d in k.da] == ["r-1", "r-2"] and lai.cho_gui() == []
    assert lai.co(lambda duong, than: than.get("loai") == "chay.xong") and lai.don()
    assert not (tmp_path / "hop-thu.jsonl").exists()


def test_hop_thu_401_dung_va_don_giu_dong_cho(tmp_path):
    h = HopThu(tmp_path)
    assert h.gui_mot(KhachGia(401), "/api/tho/bao", {"request_id": "r-1"}) is None and not h.don()


def test_khoa_worktree_h1(tmp_path):
    song = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        assert dat_khoa(tmp_path, pid=song.pid, giao_id="g-1")
        assert not dat_khoa(tmp_path, pid=os.getpid(), giao_id="g-2")        # pid khác còn sống giữ khoá
    finally:
        song.kill()
        song.wait()
    assert not con_song(song.pid) and dat_khoa(tmp_path, pid=os.getpid(), giao_id="g-2")
    go_khoa(tmp_path)
    assert not (tmp_path / ".tram" / "khoa").exists()

