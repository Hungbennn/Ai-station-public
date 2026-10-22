"""3C-D5 (C01, hợp đồng P1/3C-B): thu hồi theo UID — mở `CongLich` (UID thực đã chứng minh) rồi `kill -KILL -1` dưới
`tram-kiem` qua primitive có hạn, rồi TRẠM xác minh bằng ảnh chụp `ps`; `cron_at` mặc định cũng chạy qua `CongLich`.
Sai danh tính → không lệnh nào chạy. Không sudo/ps thật: `mo_cong`, `chup`, `chay` giả."""
import subprocess

import pytest

from tram.giao_viec import quan_sat_kiem
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import GIET, cho_het_uid, thu_hoi_theo_uid
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import HAN, cron_at
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.ngoai_le_uid import con_uid
from tram.kiem.cong_lich import CongLich
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi


def mo_gia(pk, goi, uid=777):
    def mo(ten, boc, kill):
        goi.append(("mo", ten, boc, kill))
        return CongLich(tuple(boc([])), uid, lambda a, **kw: goi.append((a, kw)) or subprocess.CompletedProcess(a, 0))
    return mo


@pytest.mark.parametrize("co_che", ["user", "sandbox"])
def test_xac_minh_uid_roi_kill_moi_tien_trinh_co_han_roi_chup_cay(co_che):
    goi, pk = [], tu_cach_ly(f"{co_che}:tram-kiem")
    thu_hoi_theo_uid(pk, mo_cong=mo_gia(pk, goi), cho_het=lambda uid: goi.append(("cho_het", uid)),
                     don_he=lambda p, chay: goi.append(("don_he", p, chay.uid)))
    assert goi == [("mo", "tram-kiem", pk.boc_lenh, pk.kill_nhom),
                   (pk.boc_lenh(GIET), {"capture_output": True, "timeout": HAN}), ("cho_het", 777), ("don_he", pk, 777)]


@pytest.mark.parametrize("loi", [LoiDanhTinh("UID 501 trùng người vận hành"), LoiThuHoi("cây dò chưa thu hồi")])
def test_sai_danh_tinh_khong_kill_khong_chup(loi):
    goi = []

    def mo(ten, boc, kill):
        raise loi
    with pytest.raises(LoiBanChep, match="không xác minh được UID"):
        thu_hoi_theo_uid(tu_cach_ly("user:tram-kiem"), mo_cong=mo, cho_het=goi.append)
    assert goi == []


def test_cho_het_uid_doi_xac_song_duoc_gat_roi_moi_dat():
    anh, ngu = [[TienTrinh(10, 1, 10, 777, 777), TienTrinh(11, 1, 11, 0, 777)], [TienTrinh(12, 1, 12, 501, 501)]], []
    cho_het_uid(777, chup=lambda: anh.pop(0), han=5, ngu=ngu.append,
                loc=lambda uid, chup, **kw: con_uid(uid, chup, ban="24G90", **kw))
    assert ngu == [0.2] and anh == []


@pytest.mark.parametrize("chup, khop", [
    (lambda: [TienTrinh(10, 1, 10, 0, 777)], "còn 1 tiến trình uid 777"),      # setuid: ruid tram-kiem, euid root
    (lambda: (_ for _ in ()).throw(OSError("ps mã 1")), "không chụp được"),
    (lambda: (_ for _ in ()).throw(ValueError("dòng ps sai dạng")), "không chụp được")])
def test_cho_het_uid_con_hoac_ps_loi_thi_nem(chup, khop):
    with pytest.raises(LoiBanChep, match=khop):
        cho_het_uid(777, chup=chup, han=0, ngu=lambda s: None,
                    loc=lambda uid, chup, **kw: con_uid(uid, chup, ban="24G90", **kw))


def test_cron_at_mac_dinh_qua_cong_lich_da_xac_minh(monkeypatch):
    goi, pk = [], tu_cach_ly("user:tram-kiem")
    kq = [(1, "", "crontab: no crontab for tram-kiem\n"), (0, "", ""), (0, "", "")]

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, *kq.pop(0))
    monkeypatch.setattr(quan_sat_kiem, "mo_cong_lich", lambda ten, boc, kill: CongLich(tuple(boc([])), 777, chay))
    cron_at(pk)
    assert goi == [pk.boc_lenh(["/usr/bin/crontab", "-l"]), pk.boc_lenh(["/usr/bin/atq"]),
                   ["/usr/bin/find", "/usr/lib/cron/jobs", "-user", "tram-kiem"]]

    def sai(ten, boc, kill):
        raise LoiDanhTinh("principal trùng root hoặc người vận hành")
    monkeypatch.setattr(quan_sat_kiem, "mo_cong_lich", sai)
    with pytest.raises(LoiBanChep, match="không xác minh được UID"):
        cron_at(pk)
    assert len(goi) == 3                                           # sai danh tính: không thêm lệnh lịch nào


@pytest.mark.parametrize("loi", [LoiThuHoi("['kill'] quá hạn"), subprocess.TimeoutExpired(["sudo"], 120),
                                 LoiDanhTinh("lệnh không chạy dưới principal đã xác minh")])
def test_kill_loi_thanh_loi_ban_chep_co_dinh_khong_chup(loi):
    goi, pk = [], tu_cach_ly("user:tram-kiem")

    def chay(a, **kw):
        raise loi
    with pytest.raises(LoiBanChep, match=r"kill -1 không xác nhận được \((LoiThuHoi|TimeoutExpired|LoiDanhTinh)\)$"):
        thu_hoi_theo_uid(pk, mo_cong=lambda t, b, k: CongLich(tuple(b([])), 777, chay), cho_het=goi.append)
    assert goi == []                                               # don_ban bắt OSError → vẫn rm bản chép


def test_cron_at_co_che_sandbox_dong_cong_khong_chay_gi(monkeypatch):
    monkeypatch.setattr(quan_sat_kiem, "mo_cong_lich", lambda *a: pytest.fail("không được mở cổng lịch"))
    with pytest.raises(LoiBanChep, match="sandbox"):
        cron_at(tu_cach_ly("sandbox:tram-kiem"))


def test_cron_at_loi_khi_chay_thanh_loi_ban_chep_co_dinh():
    def treo(argv, **kw):
        raise LoiThuHoi("['crontab'] quá hạn")
    with pytest.raises(LoiBanChep, match=r"quan sát lịch không xác nhận được \(LoiThuHoi\)$"):
        cron_at(tu_cach_ly("user:tram-kiem"), chay=treo)
