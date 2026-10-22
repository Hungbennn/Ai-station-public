import json

import pytest
from pydantic import ValidationError

from tram.ban_giao.schema import BanGiao, doc_khoi_ban_giao, kiem_ban_giao


def mau(**ghi_de):
    d = {
        "phien_ban": 1, "loai": "chinh-thuc", "luot": 1,
        "file_ban_giao": "docs/handovers/bg.md", "nhanh": "tram/hr-1", "commit": None,
        "doi_chieu_nghiem_thu": [{"tieu_chi": "A", "dat": True, "bang_chung": "t::a"}],
        "lenh_kiem": [{"lenh": "pytest", "ket_qua": "pass", "tom_tat": "1 passed",
                       "digest_log": "sha256:ab"}],
        "quyet_dinh": [], "huong_da_bo": [], "vuong_mac": [], "buoc_tiep": [],
        "cau_hoi_mo": [], "thay_doi_vung_nhay_cam": [],
    }
    d.update(ghi_de)
    return BanGiao.model_validate(d)


BB = {"lenh_bat_buoc": ["pytest"], "can_lenh_kiem": True}   # luật chặt 13/10: tham số bắt buộc


def repo(tmp_path):
    (tmp_path / "docs/handovers").mkdir(parents=True)
    (tmp_path / "docs/handovers/bg.md").write_text("x")
    return tmp_path


def test_hop_le(tmp_path):
    assert kiem_ban_giao(mau(), ["A"], repo(tmp_path), **BB) == []


def test_thieu_doi_chieu_tieu_chi(tmp_path):
    assert any("B" in l for l in kiem_ban_giao(mau(), ["A", "B"], repo(tmp_path), **BB))


def test_dat_ma_khong_bang_chung(tmp_path):
    bg = mau(doi_chieu_nghiem_thu=[{"tieu_chi": "A", "dat": True, "bang_chung": ""}])
    assert kiem_ban_giao(bg, ["A"], repo(tmp_path), **BB)


def test_khong_lenh_pass(tmp_path):
    bg = mau(lenh_kiem=[{"lenh": "pytest", "ket_qua": "fail", "tom_tat": "", "digest_log": ""}])
    assert kiem_ban_giao(bg, ["A"], repo(tmp_path), **BB)


def test_file_ban_giao_khong_ton_tai(tmp_path):
    assert kiem_ban_giao(mau(), ["A"], tmp_path, **BB)


def test_ban_giao_tam_can_nhanh_va_buoc_tiep(tmp_path):
    assert kiem_ban_giao(mau(loai="tam", buoc_tiep=[]), [], tmp_path, **BB)
    assert kiem_ban_giao(mau(loai="tam", buoc_tiep=["chạy lại test"]), [], tmp_path, **BB) == []


def test_qua_64kb(tmp_path):
    bg = mau(vuong_mac=["x" * 70_000])
    assert any("64" in l for l in kiem_ban_giao(bg, ["A"], repo(tmp_path), **BB))


def test_doc_khoi_tu_notes():
    notes = "abc\n<!-- ban-giao -->\n" + mau().model_dump_json() + "\n<!-- ban-giao -->\nxyz"
    assert doc_khoi_ban_giao(notes).nhanh == "tram/hr-1"
    assert doc_khoi_ban_giao("không có khối") is None


# --- Lát 2a: trường pr (spec 0+1a §4.3) ---

def test_ban_giao_cu_khong_co_pr_van_hop_le(tmp_path):
    bg = mau()
    assert bg.pr is None and kiem_ban_giao(bg, ["A"], repo(tmp_path), **BB) == []


def test_pr_url_va_null_hop_le():
    assert mau(pr="https://github.com/hung/hr-codex/pull/12").pr.endswith("/pull/12")
    assert mau(pr=None).pr is None


@pytest.mark.parametrize("sai", ["", "pull/12", "javascript:alert(1)", "https://", "https://github.com", "https://github.com/",
                                 "https://github.com/a b", "ftp://github.com/a/pull/1"])
def test_pr_khong_phai_url_bi_tu_choi(sai):
    with pytest.raises(ValidationError):
        mau(pr=sai)


def test_doc_khoi_co_pr_tu_notes():
    notes = "<!-- ban-giao -->\n" + mau(pr="https://github.com/h/r/pull/3").model_dump_json() + "\n<!-- ban-giao -->"
    assert doc_khoi_ban_giao(notes).pr == "https://github.com/h/r/pull/3"


def test_doc_khoi_cu_khong_co_truong_pr():
    d = json.loads(mau().model_dump_json())
    d.pop("pr", None)
    notes = "<!-- ban-giao -->\n" + json.dumps(d, ensure_ascii=False) + "\n<!-- ban-giao -->"
    bg = doc_khoi_ban_giao(notes)
    assert bg is not None and bg.pr is None
