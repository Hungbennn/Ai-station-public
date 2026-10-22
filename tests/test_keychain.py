"""bs-2bd.1.2: mọi lệnh `security find-generic-password` có hạn; kiểm tồn tại lỗi → không biết, phải dừng.
Chỉ dùng bộ chạy GIẢ — không bao giờ gọi `security` thật."""
import subprocess

import pytest

from tram.keychain import HAN_GIAY, LoiKeychain, co_muc, doc_muc

BI_MAT = "BI-MAT-KHONG-DUOC-LO"


def _chay(ma=0, ra="", loi=None):
    goi = []

    def chay(argv, **kw):
        goi.append((argv, kw))
        if loi is not None:
            raise loi
        return subprocess.CompletedProcess(argv, ma, ra, "")
    return chay, goi


def test_doc_muc_co_han_va_khong_doc_stdin():
    chay, goi = _chay(ra=BI_MAT + "\n")
    assert doc_muc("tram-x", chay=chay) == BI_MAT
    ((argv, kw),) = goi
    assert argv == ["security", "find-generic-password", "-s", "tram-x", "-w"]
    assert kw["timeout"] == HAN_GIAY and 0 < HAN_GIAY <= 15
    assert kw["stdin"] is subprocess.DEVNULL and kw["capture_output"] is True


@pytest.mark.parametrize("loi", [subprocess.TimeoutExpired(["security"], HAN_GIAY), OSError("không có security")])
def test_doc_muc_qua_han_hay_khong_chay_duoc_la_none(loi):
    chay, _ = _chay(loi=loi)
    assert doc_muc("tram-x", chay=chay) is None


@pytest.mark.parametrize("ma, ra", [(44, ""), (0, "  \n"), (51, BI_MAT)])
def test_doc_muc_ma_loi_hay_rong_la_none(ma, ra):
    chay, _ = _chay(ma=ma, ra=ra)
    assert doc_muc("tram-x", chay=chay) is None


def test_co_muc_khong_doc_gia_tri_va_co_han():
    chay, goi = _chay(ma=0)
    assert co_muc("tram-x", chay=chay) is True
    ((argv, kw),) = goi
    assert "-w" not in argv and kw["timeout"] == HAN_GIAY
    assert co_muc("tram-x", chay=_chay(ma=44)[0]) is False


@pytest.mark.parametrize("loi", [subprocess.TimeoutExpired(["security"], HAN_GIAY), OSError("x")])
def test_co_muc_qua_han_thi_bao_khong_biet(loi):
    with pytest.raises(LoiKeychain, match="Keychain") as e:
        co_muc("tram-x", chay=_chay(loi=loi)[0])
    assert "security" not in str(e.value)


@pytest.mark.parametrize("ma", [36, 51, 1, 127, -9])
def test_co_muc_loi_khong_duoc_coi_la_chua_co(ma):
    chay, _ = _chay(ma=ma, ra=BI_MAT)
    with pytest.raises(LoiKeychain, match="Keychain") as e:
        co_muc("tram-x", chay=chay)
    assert BI_MAT not in str(e.value)


def test_khong_con_loi_goi_security_khong_han_ngoai_keychain():
    """Chỗ được gọi thẳng: `tram/keychain.py`; `suy/he_thong.py` (hạn 3 giây, không `-w`); `tho/kiem_am.py` (thăm
    dò ÂM dưới principal, chạy qua bộ chạy có hạn của lát P1 — V2 sở hữu)."""
    from pathlib import Path
    goc = Path(__file__).resolve().parents[1] / "tram"
    duoc = {"keychain.py", "suy/he_thong.py", "tho/kiem_am.py"}
    sai = [str(p.relative_to(goc)) for p in goc.rglob("*.py")
           if "find-generic-password" in p.read_text(encoding="utf-8") and str(p.relative_to(goc)) not in duoc]
    assert sai == []


@pytest.mark.parametrize("ma", [None, 36, 51, 1, 127, -9])
def test_cai_dat_khong_tao_token_khi_chua_biet_da_co_hay_chua(monkeypatch, ma):
    from tram.chu import cai_dat
    from tram.chu.cai_dat_nho import tao_token_nho

    def treo(argv, **kw):
        if ma is None:
            raise subprocess.TimeoutExpired(argv, HAN_GIAY)
        return subprocess.CompletedProcess(argv, ma, BI_MAT, BI_MAT)
    monkeypatch.setattr(subprocess, "run", treo)          # `chay` mặc định đọc lúc gọi → lời gọi thật bị chặn ở đây
    assert cai_dat._thieu_keychain("tram-x") is True
    tao = []
    with pytest.raises(LoiKeychain):
        tao_token_nho(chay=lambda *a, **k: tao.append(a))
    assert tao == []
