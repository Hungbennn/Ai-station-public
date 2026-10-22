import io
import json
import urllib.error
from types import SimpleNamespace as NS

import pytest

from tram.nho import tra_phieu
from tram.nho.tra_phieu import URL_API, LoiTraPhieu, TraPhieu, doc_token_noi_bo

GID = "g-20261013-0042"
PHIEU = {"du_an": "hr-codex", "vai": "coder", "ma_giao": "Abc_def-123456789012ab", "con_hieu_luc": True}
THU_HOI = {**PHIEU, "ma_giao": None, "con_hieu_luc": False}


class MoGia:
    """urlopen giả (CHỈ DÙNG TRONG TEST): trả lần lượt; phần tử Exception thì ném."""

    def __init__(self, *tra):
        self.tra, self.goi = list(tra), []

    def __call__(self, yc, timeout):
        self.goi.append((yc.full_url, yc.get_header("Authorization"), yc.get_method(), timeout))
        x = self.tra.pop(0)
        if isinstance(x, Exception):
            raise x
        return io.BytesIO(json.dumps(x).encode())


def loi_http(ma: int):
    return urllib.error.HTTPError("u", ma, "x", {}, None)


def test_hoi_dung_url_token_noi_bo_va_timeout():
    mo = MoGia({**PHIEU, "thua": 1})
    assert TraPhieu(lambda: "tok-noi-bo", mo=mo)(GID) == PHIEU
    assert mo.goi == [(f"http://127.0.0.1:7700/api/noi-bo/phieu/{GID}", "Bearer tok-noi-bo", "GET", 2.0)]


def test_404_la_khong_co_phieu():
    assert TraPhieu(lambda: "t", mo=MoGia(loi_http(404)))(GID) is None


@pytest.mark.parametrize("tra", [loi_http(401), loi_http(500), urllib.error.URLError("tắt"), ConnectionRefusedError(),
                                 [1], {"du_an": 1}, {k: v for k, v in PHIEU.items() if k != "con_hieu_luc"},
                                  {k: v for k, v in PHIEU.items() if k != "ma_giao"}])
def test_loi_hay_sai_dang_la_tu_choi(tra):
    with pytest.raises(LoiTraPhieu):
        TraPhieu(lambda: "t", mo=MoGia(tra))(GID)


def test_chua_co_token_noi_bo_thi_tu_choi_khong_goi_mang():
    mo = MoGia()
    with pytest.raises(LoiTraPhieu, match="tram-noi-bo-token"):
        TraPhieu(lambda: None, mo=mo)(GID)
    assert mo.goi == []


@pytest.mark.parametrize("gid", ["", "g-1", "../x", f"{GID}/../../api/chu", None])
def test_giao_id_sai_dang_khong_goi_mang(gid):
    mo = MoGia()
    with pytest.raises(ValueError):
        TraPhieu(lambda: "t", mo=mo)(gid)
    assert mo.goi == []


def test_cache_30_giay_roi_hoi_lai_thay_thu_hoi():
    gio, mo = [100.0], MoGia(PHIEU, THU_HOI)
    t = TraPhieu(lambda: "t", mo=mo, dong_ho=lambda: gio[0])
    assert t(GID) == PHIEU
    gio[0] = 129.9
    assert t(GID) == PHIEU and len(mo.goi) == 1                 # trong cửa sổ 30 giây: không hỏi lại
    gio[0] = 130.0
    assert t(GID) == THU_HOI and len(mo.goi) == 2


def test_loi_khong_cache_va_cache_co_gioi_han(monkeypatch):
    mo = MoGia(urllib.error.URLError("tắt"), PHIEU, PHIEU, PHIEU)
    t = TraPhieu(lambda: "t", mo=mo, dong_ho=lambda: 0.0)
    with pytest.raises(LoiTraPhieu):
        t(GID)
    assert t(GID) == PHIEU and len(mo.goi) == 2
    monkeypatch.setattr(tra_phieu, "TOI_DA_CACHE", 1)
    t("g-20261013-0043")                                         # đẩy GID ra khỏi cache
    assert t(GID) == PHIEU and len(mo.goi) == 4


def test_doc_token_noi_bo_qua_ham_tiem():
    goi = []
    assert doc_token_noi_bo(chay=lambda c, **k: goi.append(c) or NS(returncode=0, stdout="tok\n")) == "tok"
    assert goi == [["security", "find-generic-password", "-s", "tram-noi-bo-token", "-w"]]
    assert doc_token_noi_bo(chay=lambda c, **k: NS(returncode=44, stdout="")) is None


def test_hang_so_khop_tram_api():
    from tram.api.noi_bo import KEYCHAIN_NOI_BO
    from tram.cli_dich_vu import CONG_MAC_DINH
    assert KEYCHAIN_NOI_BO == tra_phieu.KEYCHAIN_NOI_BO and URL_API == f"http://127.0.0.1:{CONG_MAC_DINH}"
