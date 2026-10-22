"""1b-3: bước soạn của thăng cấp — LLM chỉ thấy nội dung, đầu ra qua guardrail, rỗng = bỏ cặp."""
import json

import pytest

from nho_gia import ClientGia, tra_loi
from tram.cham_cot.prompt import THE, nap_vai
from tram.nho.llm import LoiLLMNho
from tram.nho.soan_thang_cap import BanSoan, loi_soan, soan

VAI = nap_vai("nho-thang-cap")
TOT = {"noi_dung": "Chạy toàn bộ test trước khi bàn giao.", "nhan": ["test"], "co_ten_rieng": False}


def test_vai_thang_cap_co_phien_ban_va_nguyen_tac():
    assert VAI[0] == "1" and "du_lieu_khong_tin_cay" in VAI[1] and "chuỗi rỗng" in VAI[1]


def test_soan_boc_the_chi_dua_noi_dung():
    c = ClientGia(tra_loi(TOT))
    kq = soan(c, VAI, "hr-codex: chạy `php artisan test` trước khi bàn giao", "ke-toan: chạy pytest trước bàn giao")
    assert kq == BanSoan("Chạy toàn bộ test trước khi bàn giao.", ("test",), False)
    noi_dung = c.goi[0]["messages"][0]["content"]
    assert noi_dung.startswith(f"<{THE}>") and noi_dung.endswith(f"</{THE}>")
    tho = json.loads(noi_dung.removeprefix(f"<{THE}>\n").removesuffix(f"\n</{THE}>"))
    assert tho == {"ky_uc": ["hr-codex: chạy `php artisan test` trước khi bàn giao",
                             "ke-toan: chạy pytest trước bàn giao"]}
    assert c.goi[0]["system"][0]["text"] == VAI[1]


def test_noi_dung_rong_la_khong_thang_cap():
    kq = soan(ClientGia(tra_loi({"noi_dung": "  ", "nhan": [], "co_ten_rieng": False})), VAI, "a", "b")
    assert kq.noi_dung == ""


@pytest.mark.parametrize("d", [
    {"noi_dung": "x" * 601, "nhan": [], "co_ten_rieng": False},
    {"noi_dung": 3, "nhan": [], "co_ten_rieng": False},
    {"noi_dung": "x", "nhan": ["a"] * 6, "co_ten_rieng": False},
    {"noi_dung": "x", "nhan": [""], "co_ten_rieng": False},
    {"noi_dung": "x", "nhan": [], "co_ten_rieng": "khong"}])
def test_guardrail_bat_dau_ra_sai(d):
    assert loi_soan(d)


def test_sai_ba_lan_thi_loi_llm_nho():
    xau = tra_loi({"noi_dung": "x", "nhan": "test", "co_ten_rieng": False})
    with pytest.raises(LoiLLMNho):
        soan(ClientGia(xau, xau, xau), VAI, "a", "b")


def test_sai_mot_lan_thi_thu_lai():
    xau = tra_loi({"noi_dung": "x" * 700, "nhan": [], "co_ten_rieng": False})
    c = ClientGia(xau, tra_loi(TOT))
    assert soan(c, VAI, "a", "b").noi_dung == TOT["noi_dung"] and len(c.goi) == 2
