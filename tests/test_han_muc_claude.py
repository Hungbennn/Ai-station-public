"""Bộ đọc hạn mức Claude (spec 3 §8.1). Fixture dưới đây CHỈ DÙNG TRONG TEST — dựng theo spike 12/10 + tài liệu
Agent SDK, HÌNH DẠNG CHƯA XÁC MINH (chờ S1). Không đánh dấu adapter sẵn sàng bằng các fixture này."""
import json
import os
from datetime import datetime, timezone

import pytest

from tram.han_muc.claude import NguonHanMucClaude
from tram.han_muc.log_claude import doc_log_claude, gop_han_muc
from tram.han_muc.mo_hinh import CuaSo, HanMuc

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
RESET = 1760335200                                     # 2025-10-13T06:00:00Z


def su_kien(status="allowed", loai="five_hour", u=0.62, phang=False, **them):
    info = {"status": status, "resetsAt": RESET, "rateLimitType": loai, "utilization": u, **them}
    return {"type": "rate_limit_event", **info} if phang else {"type": "rate_limit_event", "rate_limit_info": info}


def doc(nguon, dong):
    return nguon.doc_dong(dong, khe_id="B/claude-1", bay_gio=LUC)


def test_chua_chot_thang_thi_khong_doc_utilization():
    cs = doc(NguonHanMucClaude(), su_kien()).cua_so[0]
    assert (cs.loai, cs.trang_thai, cs.phan_tram, cs.reset_luc) == ("5h", "chua_biet", None, "2025-10-13T06:00:00Z")
    assert doc(NguonHanMucClaude(), su_kien(status="rejected")).cua_so[0].phan_tram == 100.0
    assert doc(NguonHanMucClaude(), su_kien(status="allowed_warning")).cua_so[0].phan_tram == 90.0


@pytest.mark.parametrize("thang, u, ky_vong", [("ti_le", 0.62, 62.0), ("phan_tram", 62, 62.0),
                                               ("ti_le", 1.7, 100.0), ("phan_tram", -3, 0.0)])
def test_thang_da_chot(thang, u, ky_vong):
    hm = doc(NguonHanMucClaude(thang=thang), su_kien(u=u, loai="seven_day"))
    assert hm.nguon == "stream" and hm.cua_so[0].loai == "tuan" and hm.cua_so[0].phan_tram == ky_vong


def test_dang_phang_loai_la_va_dong_khong_lien_quan():
    n = NguonHanMucClaude(thang="ti_le")
    assert doc(n, su_kien(phang=True, u=0.5)).cua_so[0].phan_tram == 50.0
    assert doc(n, su_kien(loai="seven_day_opus")).cua_so[0].loai == "seven_day_opus"     # không thành "tuan"
    assert doc(n, su_kien(loai="")) is None and doc(n, {"type": "assistant"}) is None
    assert doc(n, su_kien(resetsAt="khong-phai-gio")).cua_so[0].reset_luc is None


def test_het_han_muc_chua_dang_nhap_va_reset():
    n = NguonHanMucClaude()
    assert n.het_han_muc(su_kien(status="rejected")) and not n.het_han_muc(su_kien())
    assert n.het_han_muc({"type": "assistant", "error": "rate_limit"})
    assert n.het_han_muc({"type": "result", "is_error": True, "result": "Claude AI usage limit reached|1760335200"})
    assert not n.het_han_muc({"type": "result", "is_error": False, "result": "rate limit nói trong bài"})
    assert n.chua_dang_nhap({"type": "result", "is_error": True, "result": "Invalid API key · Please run /login"})
    assert n.chua_dang_nhap({"type": "assistant", "error": "authentication_failed"})
    assert n.reset_luc(su_kien(status="rejected")) == "2025-10-13T06:00:00Z" and n.reset_luc(su_kien()) is None


def test_regex_gan_het_la_cua_so_regex_cham_nguong():
    hm = doc(NguonHanMucClaude(), {"type": "result", "result": "You are approaching your usage limit"})
    assert hm.nguon == "regex" and (hm.cua_so[0].loai, hm.cua_so[0].phan_tram) == ("regex", 90.0)


def test_gop_thay_cung_loai_giu_loai_khac():
    a = HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[
        CuaSo(loai="5h", trang_thai="biet", phan_tram=10, doc_luc="2026-10-13T02:00:00Z"),
        CuaSo(loai="tuan", trang_thai="biet", phan_tram=40, doc_luc="2026-10-13T02:00:00Z")])
    b = HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[
        CuaSo(loai="5h", trang_thai="biet", phan_tram=70, doc_luc="2026-10-13T03:00:00Z")])
    g = gop_han_muc(a, b)
    assert {c.loai: c.phan_tram for c in g.cua_so} == {"5h": 70, "tuan": 40}
    assert gop_han_muc(None, b) == b and gop_han_muc(a, None) == a


def test_nguon_lui_log_doc_file_moi_nhat(tmp_path):
    d = tmp_path / "projects" / "-Users-x-wt"
    d.mkdir(parents=True)
    (d / "cu.jsonl").write_text(json.dumps({"rate_limit_info": su_kien(status="rejected")["rate_limit_info"]}) + "\n")
    os.utime(d / "cu.jsonl", (1, 1))
    (d / "moi.jsonl").write_text("không json\n" + json.dumps(
        {"message": {"apiErrorParams": {"rate_limit_info": su_kien(loai="seven_day", status="rejected")[
            "rate_limit_info"]}}}) + "\n")
    hm = doc_log_claude(tmp_path, khe_id="B/claude-1", bay_gio=LUC, nguon=NguonHanMucClaude())
    assert hm.nguon == "log" and [(c.loai, c.phan_tram) for c in hm.cua_so] == [("tuan", 100.0)]
    assert doc_log_claude(tmp_path / "khong", khe_id="B/claude-1", bay_gio=LUC, nguon=NguonHanMucClaude()) is None
