"""Review vòng 1 A02: cây không quan sát được KHÔNG được coi là sạch ở tầng khe. Vòng `tram tho chay` THẬT (CLI giả,
trạm trong bộ nhớ, cùng user) chỉ sang lần chạy/phiếu sau khi dọn theo UID của khe xác nhận; còn tàn dư → khe dừng,
không spawn lần sau, giữ bản ghi pid + phiếu. Dọn UID là bản GIẢ (ghi lại; ném khi "còn tàn dư"), không kill -1
thật."""
import threading

from test_kich_ban_3a2 import su_kien
from tho_chay_gia import dung_may
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.vong_khe import VongKhe


def chay_khe(m, hong_tu: int):
    """Chạy vòng khe tới khi nó TỰ dừng; lần dọn thứ `hong_tu` báo còn tàn dư."""
    goi = []

    def don(pr):
        goi.append(pr)
        if len(goi) >= hong_tu:
            raise LoiThuHoi("còn 1 tiến trình của UID khe sau kill -1")
    m.nc.don_uid = don
    tat, vk = threading.Event(), VongKhe(m.nc, m.nc.ch.khe[0])
    th = threading.Thread(target=vk.chay, args=(tat,), daemon=True)
    th.start()
    th.join(40)
    tat.set()
    return vk, goi, not th.is_alive()


def test_tan_du_sau_lan_chay_thi_khong_sang_lan_sau_va_khe_dung(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, {"1": [{"thoat": 1}], "2": [{"thoat": 0}]})
    vk, goi, tu_dung = chay_khe(m, 3)                   # 1: khởi động khe, 2: đầu phiếu, 3: sau lần chạy 1
    wt = m.nc.goc_wt / "hr-codex" / "hr-1"
    assert tu_dung and vk.hong and len(goi) == 3 and [s["lan"] for s in su_kien(m, "chay.bat_dau")] == [1]
    assert not (wt / ".tram" / "stdin-2.md").exists() and su_kien(m, "chay.xong") == []
    assert vk.so.pid.exists() and vk.so.doc_phieu() is not None             # khởi động lại: dọn UID rồi `mo-coi`


def test_tan_du_luc_khoi_dong_thi_khe_dung_khong_nhan_phieu(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"thoat": 0}])
    vk, goi, tu_dung = chay_khe(m, 1)
    assert tu_dung and vk.hong and len(goi) == 1 and vk.so.doc_phieu() is None and su_kien(m, "chay.bat_dau") == []


def test_tan_du_dau_phieu_thi_khong_dung_worktree_khe_dung_giu_phieu(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"thoat": 0}])
    vk, goi, tu_dung = chay_khe(m, 2)
    assert tu_dung and vk.hong and len(goi) == 2 and su_kien(m, "chay.bat_dau") == []
    assert not (m.nc.goc_wt / "hr-codex" / "hr-1").exists() and vk.so.doc_phieu() is not None
