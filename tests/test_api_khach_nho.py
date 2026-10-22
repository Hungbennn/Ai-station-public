"""1b-3: tram-api gọi memory service — token đọc lười, quên khi 401; lỗi giữ mã HTTP + thân `{loi, ly_do}`."""
import io
import urllib.error

import pytest
from pydantic import ValidationError

from tram.api.khach_nho import CHO_DOC, KhachNho
from tram.api.than import ThanNhoGhi, ThanNhoXoa
from tram.nho.khach import LoiNhoKhach, goi_nho


def _http_loi(ma, than: bytes | None):
    def mo(yc, timeout):
        raise urllib.error.HTTPError(yc.full_url, ma, "x", {}, None if than is None else io.BytesIO(than))
    return mo


def test_loi_http_giu_ma_va_than_loi():
    with pytest.raises(LoiNhoKhach) as e:
        goi_nho("/ghi", {}, token="bi-mat", mo=_http_loi(422, '{"loi": "chạm luật", "ly_do": ["số tiền (10k)"]}'
                                                       .encode()))
    assert e.value.ma == 422 and e.value.than == {"loi": "chạm luật", "ly_do": ["số tiền (10k)"]}
    assert "bi-mat" not in str(e.value) and str(e.value) == "memory service trả 422"
    for than in (None, b"khong-phai-json", b"[1]"):
        with pytest.raises(LoiNhoKhach) as e:
            goi_nho("/ghi", {}, token="t", mo=_http_loi(503, than))
        assert e.value.ma == 503 and e.value.than == {}


def test_khong_goi_duoc_thi_ma_none():
    def mo(yc, timeout):
        raise urllib.error.URLError("refused")
    with pytest.raises(LoiNhoKhach) as e:
        goi_nho("/x", {}, token="t", mo=mo)
    assert e.value.ma is None


def test_khach_nho_doc_token_luoi_mot_lan():
    doc, goi = [], []
    k = KhachNho(doc=lambda: doc.append(1) or "tk", goi=lambda d, t, **kw: goi.append((d, t, kw)) or {"ok": 1})
    assert doc == []                                    # dựng tram-api không đọc Keychain
    assert k.goi("/danh-sach", {"a": 1}) == {"ok": 1} and k.goi("/xoa", {}, thoi_gian_cho=60.0) == {"ok": 1}
    assert doc == [1] and goi == [("/danh-sach", {"a": 1}, {"token": "tk", "thoi_gian_cho": CHO_DOC}),
                                  ("/xoa", {}, {"token": "tk", "thoi_gian_cho": 60.0})]


def test_chua_cai_thi_bao_loi_va_lan_sau_doc_lai():
    token = [None, "tk"]
    k = KhachNho(doc=lambda: token.pop(0), goi=lambda d, t, **kw: {"ok": 1})
    with pytest.raises(LoiNhoKhach) as e:
        k.goi("/danh-sach", {})
    assert e.value.ma is None and "chưa cài" in str(e.value)
    assert k.goi("/danh-sach", {}) == {"ok": 1}


def test_401_thi_quen_token():
    doc = []

    def goi(d, t, **kw):
        raise LoiNhoKhach("memory service trả 401", ma=401)
    k = KhachNho(doc=lambda: doc.append(1) or "cu", goi=goi)
    for _ in range(2):
        with pytest.raises(LoiNhoKhach):
            k.goi("/x", {})
    assert doc == [1, 1]


def test_than_nho_tu_choi_truong_la_va_qua_dai():
    g = {"ma_thao_tac": "ma-nho-0001", "expected_version": ""}
    assert ThanNhoGhi(**g, noi_dung="Chạy test", pham_vi="/chung").nhan == []
    for xau in ({"noi_dung": "x" * 601, "pham_vi": "/chung"}, {"noi_dung": "x", "pham_vi": "/chung", "nhan": ["a"] * 6},
                {"noi_dung": "x", "pham_vi": "/chung", "la": 1}, {"noi_dung": "", "pham_vi": "/chung"}):
        with pytest.raises(ValidationError):
            ThanNhoGhi(**g, **xau)
    with pytest.raises(ValidationError):
        ThanNhoXoa(**g, id="m-1; rm")
    assert ThanNhoXoa(**g, id="m-abc").id == "m-abc"
