import pytest

from bead_gia import notes_ban_giao
from tram.ban_giao.doc import doc_khoi_ban_giao_co_loi, tom_tat_ban_giao
from tram.suy.chi_tiet import ban_giao_sach


def test_khong_co_khoi():
    assert doc_khoi_ban_giao_co_loi("chỉ là ghi chú") == (None, [])
    assert doc_khoi_ban_giao_co_loi(None) == (None, [])
    assert tom_tat_ban_giao("chỉ là ghi chú") is None


def test_khoi_hop_le_co_pr():
    bg, loi = doc_khoi_ban_giao_co_loi(notes_ban_giao())
    assert loi == [] and bg.pr == "https://github.com/o/r/pull/7"
    assert tom_tat_ban_giao(notes_ban_giao()) == {
        "pr": "https://github.com/o/r/pull/7", "nhanh": "fix/x", "commit": "abc1234",
        "file_ban_giao": "docs/handovers/x.md", "loi": []}


def test_khoi_sai_schema_co_loi():
    bg, loi = doc_khoi_ban_giao_co_loi(notes_ban_giao(luot="một"))
    assert bg is None and loi and any("luot" in x for x in loi)
    tt = tom_tat_ban_giao(notes_ban_giao(luot="một"))
    assert tt["pr"] is None and tt["loi"]


def test_thieu_dau_dong():
    bg, loi = doc_khoi_ban_giao_co_loi('<!-- ban-giao -->\n{"phien_ban": 1}')
    assert bg is None and loi == ["Khối bàn giao thiếu dấu đóng hoặc không phải một JSON object"]


def test_pr_http_khong_hien_link():
    tt = tom_tat_ban_giao(notes_ban_giao(pr="http://github.com/o/r/pull/7"))
    assert tt["pr"] is None and "pr không phải URL https — không hiện link" in tt["loi"]


def test_khoi_qua_64kb():
    bg, loi = doc_khoi_ban_giao_co_loi(notes_ban_giao(vuong_mac=["x" * 70_000]))
    assert bg is None and loi == ["Khối bàn giao vượt 64 KB"]


@pytest.mark.parametrize("ky_tu", ["‮", "​", "⁦"])
def test_pr_co_ky_tu_dieu_khien_khong_hien_link(ky_tu):
    tt = tom_tat_ban_giao(notes_ban_giao(pr=f"https://github.com/o/r/pull/7{ky_tu}exe.txt"))
    assert tt["pr"] is None and "pr có ký tự điều khiển" in tt["loi"]
    tho = {"pr": f"https://github.com/o/r/pull/7{ky_tu}exe.txt", "nhanh": "x", "commit": None,
           "file_ban_giao": None, "loi": []}
    assert ban_giao_sach(tho)["pr"] is None
