"""Đọc stream-json (spec 3 §7.8). Dòng mẫu CHỈ DÙNG TRONG TEST — dạng theo tài liệu Agent SDK, chưa xác minh (S1/S4)."""
import json

from tho_gia import NguonHanMucGia
from tram.chay_cli.giao_dien import ket_thuc_tu
from tram.chay_cli.stream import DocStream
from tram.han_muc.claude import NguonHanMucClaude


def ast(mid, ra, **them):
    return json.dumps({"type": "assistant", "message": {"id": mid, "model": "claude-x", "usage": {
        "input_tokens": 10, "output_tokens": ra, "cache_read_input_tokens": 5}}, **them})


def doc(*dong, nguon=None, **kw):
    s = DocStream(nguon or NguonHanMucClaude(), khe_id="B/claude-1", **kw)
    for d in dong:
        s.an(d)
    return s


def test_dem_token_theo_message_id_khong_cong_dong_lap():
    s = doc(json.dumps({"type": "system", "subtype": "init", "model": "claude-mo-hinh"}),
            ast("m1", 50), ast("m1", 80), ast("m2", 20), "không phải json", "[1]")
    assert s.co_assistant and s.mo_hinh == "claude-mo-hinh"
    assert s.tokens() == {"token_vao": 20, "token_ra": 100, "token_cache_doc": 10, "token_cache_ghi": 0}
    s.an(json.dumps({"type": "result", "usage": {"input_tokens": 7, "output_tokens": 300}}))
    assert s.tokens()["token_ra"] == 300                                       # result: lấy usage tổng


def test_vuot_token_goi_mot_lan():
    goi = []
    s = doc(ast("m1", 60), ast("m2", 60), ast("m3", 60), tran_token_ra=100, khi_vuot=lambda: goi.append(1))
    assert s.vuot_token and goi == [1]


def test_het_han_muc_reset_va_loi_he():
    s = doc(json.dumps({"type": "rate_limit_event", "rate_limit_info": {"status": "rejected", "resetsAt": 1760335200,
                                                                         "rateLimitType": "five_hour"}}))
    kq = s.ket_qua(ma_thoat=1, bi_dung=False, thoi_gian_ms=5, digest_log="sha256:x")
    assert kq.het_han_muc and kq.reset_luc == "2025-10-13T06:00:00Z" and ket_thuc_tu(kq) == "het_han_muc"
    s = doc(json.dumps({"type": "result", "is_error": True, "result": "Invalid API key · Please run /login"}))
    assert ket_thuc_tu(s.ket_qua(ma_thoat=1, bi_dung=False, thoi_gian_ms=1, digest_log="")) == "loi_he"
    s = doc(json.dumps({"type": "assistant", "error": "rate_limit", "message": {"id": "e"}}))
    assert s.het_han_muc and not s.co_assistant                               # thông điệp lỗi không tính là agent


def test_han_muc_gop_va_bao_ra_ngoai():
    thay = []
    s = doc(json.dumps({"gia_han_muc": {"5h": 30.0}, "doc_luc": "2026-10-13T03:00:00Z"}),
            json.dumps({"gia_han_muc": {"tuan": 50.0}, "doc_luc": "2026-10-13T03:00:00Z"}),
            nguon=NguonHanMucGia(), khi_han_muc=thay.append)
    assert {c.loai for c in s.han_muc.cua_so} == {"5h", "tuan"} and len(thay) == 2
