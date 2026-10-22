"""Phiếu yêu cầu (spec 4 §7.1) — dữ liệu không tin cậy, kiểm chặt."""
import json

import pytest

from tram.giao_viec.phieu_yeu_cau import doc_phieu, tieu_chi_spec

MAU = {"phien_ban": 1, "muc_tieu": "Sale xem được hoa hồng tạm tính ngay trên booking",
       "nghiep_vu_da_chot": ["Hoa hồng tính trên giá sau giảm giá (ADR-0083)"],
       "pham_vi": "Màn chi tiết booking (Book) + API đọc hoa hồng (Comp)", "khong_lam": ["Không sửa công thức"],
       "nghiem_thu_so_bo": ["Booking có giảm giá  hiện đúng số tạm tính"], "cau_hoi_mo": [], "du_an": "hr-codex",
       "module": ["Book", "Comp"], "bien_ban": "docs/discussions/2026-10-13-hoa-hong-tam-tinh.md"}


def mo_ta(phieu=None, *, tho=None) -> str:
    noi_dung = tho if tho is not None else json.dumps(phieu if phieu is not None else MAU, ensure_ascii=False)
    return f"Ý tưởng hoa hồng.\n<!-- phieu-yeu-cau -->\n{noi_dung}\n<!-- phieu-yeu-cau -->\nghi chú"


def test_hop_le_va_tieu_chi_spec():
    p, loi = doc_phieu(mo_ta(), "hr-codex")
    assert loi == [] and p.muc_tieu.startswith("Sale") and p.module == ["Book", "Comp"]
    assert tieu_chi_spec(p) == ["Booking có giảm giá hiện đúng số tạm tính"]


def test_toi_thieu_va_cau_hoi_mo_van_hop_le():
    p, _ = doc_phieu(mo_ta({"phien_ban": 1, "muc_tieu": "x", "pham_vi": "y", "nghiem_thu_so_bo": ["z"],
                            "du_an": "hr-codex", "cau_hoi_mo": ["Làm tròn lên hay xuống?"]}), "hr-codex")
    assert p is not None and p.cau_hoi_mo == ["Làm tròn lên hay xuống?"] and p.bien_ban is None


@pytest.mark.parametrize("sua, chu", [
    ({"muc_tieu": None}, "muc_tieu"), ({"pham_vi": None}, "pham_vi"), ({"muc_tieu": "   "}, "muc_tieu"),
    ({"nghiem_thu_so_bo": []}, "nghiem_thu_so_bo"), ({"nghiem_thu_so_bo": [" "]}, "nghiem_thu_so_bo"),
    ({"phien_ban": 2}, "phien_ban"), ({"la": 1}, "la"), ({"bien_ban": "../bi-mat.md"}, "bien_ban"),
    ({"bien_ban": "/etc/passwd"}, "bien_ban"), ({"du_an": "HR"}, "du_an"), ({"module": "Book"}, "module"),
])
def test_sai_schema(sua, chu):
    phieu = {k: v for k, v in {**MAU, **sua}.items() if v is not None}
    p, loi = doc_phieu(mo_ta(phieu), "hr-codex")
    assert p is None and any(chu in l for l in loi)


@pytest.mark.parametrize("van_ban, chu", [
    ("Không có khối", "không có khối"), (mo_ta() + mo_ta(), "đúng một khối"),
    (mo_ta(tho="{hỏng"), "khối"), (mo_ta(tho='{"phien_ban": 1, ' + '"x": "' + "a" * 40000 + '"}'), "32 KB"),
])
def test_khoi_loi(van_ban, chu):
    p, loi = doc_phieu(van_ban, "hr-codex")
    assert p is None and chu in loi[0]


def test_du_an_khac_du_an_cua_bead():
    p, loi = doc_phieu(mo_ta(), "khac")
    assert p is None and "khác dự án" in loi[0]
