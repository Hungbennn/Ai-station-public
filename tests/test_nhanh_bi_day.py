"""Hợp đồng `bao.bi {ly_do: "nhanh-bi-day-ngoai-luong"}` (spec 4 §9; 4a-1 G20): thợ báo được (3a-1 `LY_DO_BI`),
trạm nhận qua `nhan_bao` thật và vòng tick tạo escalation `nhanh-bi-day`, không giao lại."""
from giao_viec_gia import bug, dung
from test_kich_ban_4a1 import bao, xin
from tram.giao_viec.tick import mot_vong_tick
from tram.phieu.bao import LY_DO_BI, ThanBao


def test_ly_do_bi_nhan_nhanh_bi_day():
    assert "nhanh-bi-day-ngoai-luong" in LY_DO_BI
    assert ThanBao(khe_id="B/claude-1", giao_id="g-20261013-0001", luot=1, loai="bi", request_id="r-12345678",
                   ly_do="nhanh-bi-day-ngoai-luong").ly_do == "nhanh-bi-day-ngoai-luong"


def test_bao_bi_nhanh_bi_day_thanh_escalation(tmp_path):
    t = dung(tmp_path, bug())
    mot_vong_tick(t.bo)
    p = xin(t, "claude-1")
    bao(t, p, "bi", ly_do="nhanh-bi-day-ngoai-luong", noi_dung="CAS ref công bố thất bại")
    mot_vong_tick(t.bo)
    esc = [b for b in t.g.beads.values() if b.issue_type == "decision"]
    assert len(esc) == 1 and "ly_do: nhanh-bi-day" in esc[0].description and "CAS" in esc[0].description
    assert xin(t, "claude-1") is None and xin(t, "claude-2") is None                 # bead bị chặn, không giao lại
