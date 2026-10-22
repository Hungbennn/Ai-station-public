"""bs-2bd.1.1: một lời gọi Anthropic có HẠN TỔNG phía người gọi (luồng phụ + `cho` điều khiển được), SDK không tự thử
lại (không ngủ theo `retry-after`), số lời gọi còn sống có trần cưỡng chế. Không gọi mạng: client giả, transport giả của SDK; khoá giả."""
import threading
import time
from types import SimpleNamespace as NS

import anthropic
import httpx2
import pytest

from tram.llm import claude, han_goi
from tram.nho.llm import goi_json


@pytest.fixture(autouse=True)
def tha_luong_treo():
    tha = threading.Event()
    yield tha
    tha.set()                                                 # mọi bản giả đang treo chờ `tha` đều dứt
    for t in list(han_goi._song):
        t.join(5)
    assert not han_goi._song                                  # luồng dứt thì tự trả chỗ


def khong_cho(t, giay):
    """Đồng hồ điều khiển: hạn coi như đã trôi qua ngay, người gọi không chờ thật."""


def test_client_khong_tu_thu_lai_va_co_han_io(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-gia-khong-that")
    c = claude.tao_client()
    assert c.max_retries == 0 and c.timeout == han_goi.HAN_GOI_GIAY


def test_client_tu_keychain(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(claude, "doc_muc", lambda ten: "sk-gia-keychain" if ten == claude.KEYCHAIN_DICH_VU else None)
    c = claude.tao_client()
    assert c.api_key == "sk-gia-keychain" and c.max_retries == 0 and c.timeout == han_goi.HAN_GOI_GIAY


def test_thieu_khoa_bao_loi_khong_lo_gia_tri(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(claude, "doc_muc", lambda ten: None)
    with pytest.raises(claude.LoiChamLLM, match="Chưa có API key"):
        claude.tao_client()


def test_429_retry_after_mot_ngay_khong_ngu(monkeypatch):
    """SDK 1.13 ngủ đúng `retry-after` (không trần) rồi thử lại; tram tắt thử lại → lỗi ngay, không ngủ."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-gia-khong-that")
    goi = []

    def tra_429(req):
        goi.append(req.url.path)
        return httpx2.Response(429, headers={"retry-after": "86400"},
                               json={"type": "error", "error": {"type": "rate_limit_error", "message": "gia"}})
    monkeypatch.setattr(time, "sleep", lambda s: pytest.fail(f"SDK ngủ {s} giây"))
    c = claude.tao_client().with_options(http_client=httpx2.Client(transport=httpx2.MockTransport(tra_429)))
    with pytest.raises(anthropic.RateLimitError):
        c.messages.create(model="m", max_tokens=1, messages=[{"role": "user", "content": "x"}])
    assert goi == ["/v1/messages"]


def test_qua_han_tong_nem_timeout_khong_cho_luong_treo(tha_luong_treo):
    da_cho = []
    with pytest.raises(anthropic.APITimeoutError, match="quá 120 giây"):
        han_goi.goi_trong_han(lambda: tha_luong_treo.wait(10), cho=lambda t, giay: da_cho.append(giay))
    assert len(da_cho) == 1 and 0 < da_cho[0] <= han_goi.HAN_GOI_GIAY and len(han_goi._song) == 1


def test_het_cho_thi_cho_trong_han_roi_tu_choi_khong_mo_them(monkeypatch, tha_luong_treo):
    monkeypatch.setattr(han_goi, "HAN_GOI_GIAY", 0.2)
    vao = []

    def treo():
        vao.append(1)
        tha_luong_treo.wait(10)
    for _ in range(han_goi.TOI_DA_LUONG):
        with pytest.raises(anthropic.APITimeoutError):
            han_goi.goi_trong_han(treo, cho=khong_cho)
    bat_dau = time.monotonic()
    with pytest.raises(anthropic.APITimeoutError, match="chưa dứt"):
        han_goi.goi_trong_han(treo, cho=khong_cho)
    assert time.monotonic() - bat_dau < 2                      # chờ chỗ trong hạn tổng của chính lời gọi
    het = time.monotonic() + 5
    while len(vao) < han_goi.TOI_DA_LUONG and time.monotonic() < het:
        time.sleep(0.01)
    assert len(vao) == han_goi.TOI_DA_LUONG                      # lời gọi thứ ba không mở luồng
    tha_luong_treo.set()
    for t in list(han_goi._song):
        t.join(5)
    assert han_goi.goi_trong_han(lambda: 7) == 7                 # luồng treo đã dứt: gọi lại được


def test_nhieu_nguoi_goi_dong_thoi_khong_vuot_tran(tha_luong_treo):
    """Năm người gọi cùng lúc (memory: vòng nạp + MCP trong threadpool): cùng lúc chỉ TOI_DA_LUONG lời gọi chạy, người
    đến sau chờ chỗ trong hạn của mình; nhả ra thì tất cả xong."""
    khoa, dem, ket_qua = threading.Lock(), {"dang": 0, "dinh": 0}, []
    rao = threading.Barrier(5)

    def mang():
        with khoa:
            dem["dang"] += 1
            dem["dinh"] = max(dem["dinh"], dem["dang"])
        tha_luong_treo.wait(10)
        with khoa:
            dem["dang"] -= 1
        return 1

    def nguoi_goi():
        rao.wait(5)
        ket_qua.append(han_goi.goi_trong_han(mang))
    ds = [threading.Thread(target=nguoi_goi) for _ in range(5)]
    for t in ds:
        t.start()
    het = time.monotonic() + 5
    while dem["dang"] < han_goi.TOI_DA_LUONG and time.monotonic() < het:
        time.sleep(0.01)
    time.sleep(0.3)                                              # người đến sau đã kịp thử
    assert dem["dinh"] == han_goi.TOI_DA_LUONG == len(han_goi._song)
    tha_luong_treo.set()
    for t in ds:
        t.join(10)
    assert ket_qua == [1] * 5 and dem["dinh"] == han_goi.TOI_DA_LUONG


def test_nguoi_goi_bi_ngat_khi_cho_van_giu_cho(monkeypatch, tha_luong_treo):
    """Người gọi bị ngắt lúc chờ: luồng còn sống vẫn được đếm tới khi lời gọi thật dứt — lần gọi sau không vượt trần."""
    monkeypatch.setattr(han_goi, "TOI_DA_LUONG", 1)
    monkeypatch.setattr(han_goi, "HAN_GOI_GIAY", 0.2)
    vao = []

    def ngat(t, giay):
        raise KeyboardInterrupt

    def treo():
        vao.append(1)
        tha_luong_treo.wait(10)
    with pytest.raises(KeyboardInterrupt):
        han_goi.goi_trong_han(treo, cho=ngat)
    assert len(han_goi._song) == 1
    with pytest.raises(anthropic.APITimeoutError, match="chưa dứt"):
        han_goi.goi_trong_han(treo, cho=khong_cho)
    time.sleep(0.1)
    assert len(vao) == 1
    tha_luong_treo.set()
    for t in list(han_goi._song):
        t.join(5)
    assert han_goi.goi_trong_han(lambda: 7) == 7


def test_ngat_start_truoc_khi_ident_hien_ra_khong_tra_cho(monkeypatch):
    class DangKhoiDong:
        ident = None

        def start(self):
            raise KeyboardInterrupt()       # luồng OS có thể đã tạo nhưng chưa chạy _bootstrap

    t = DangKhoiDong()
    monkeypatch.setattr(han_goi, "TOI_DA_LUONG", 1)
    try:
        with pytest.raises(KeyboardInterrupt):
            han_goi._dat_cho(t, time.monotonic() + 1)
        assert t in han_goi._song
        with pytest.raises(anthropic.APITimeoutError, match="chưa dứt"):
            han_goi._dat_cho(DangKhoiDong(), time.monotonic() - 1)
    finally:
        han_goi._song.discard(t)              # chỉ bản giả không có luồng; không áp cách này vào mã thật


def test_het_han_du_co_cho_trong_cung_khong_mo_luong():
    class ChuaChay:
        def start(self):
            pytest.fail("không được mở lời gọi mới sau hạn")
    with pytest.raises(anthropic.APITimeoutError, match="hết hạn"):
        han_goi._dat_cho(ChuaChay(), time.monotonic() - 1)
    assert not han_goi._song


def test_tra_ket_qua_va_loi_nguyen_ven():
    assert han_goi.goi_trong_han(lambda: {"a": 1}) == {"a": 1}

    def hong():
        raise ValueError("lỗi gốc")
    with pytest.raises(ValueError, match="lỗi gốc"):
        han_goi.goi_trong_han(hong)
    assert han_goi._song == set()


def test_dong_ho_that_cho_dung_han(monkeypatch, tha_luong_treo):
    monkeypatch.setattr(han_goi, "HAN_GOI_GIAY", 0.2)
    bat_dau = time.monotonic()
    with pytest.raises(anthropic.APITimeoutError):
        han_goi.goi_trong_han(lambda: tha_luong_treo.wait(10))
    assert time.monotonic() - bat_dau < 2


def test_cham_cot_va_memory_deu_di_qua_han(monkeypatch, tha_luong_treo):
    monkeypatch.setattr(han_goi, "HAN_GOI_GIAY", 0.1)
    treo = NS(create=lambda **kw: tha_luong_treo.wait(3))         # trần 3 giây: bản đỏ không treo
    with pytest.raises(anthropic.APITimeoutError):
        claude.cham_bang_llm(NS(beta=NS(messages=treo)), "HỆ", "NỘI DUNG")
    with pytest.raises(anthropic.APITimeoutError):
        goi_json(NS(messages=treo), he_thong="HỆ", noi_dung="x", schema={}, kiem=lambda d: [])
