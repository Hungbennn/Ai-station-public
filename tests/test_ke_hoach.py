"""`*.beads.json` (spec 4 §7.2) — kiểm dữ liệu không tin cậy; digest đúng bản (G11)."""
import json

import pytest

from feature_gia import bead_de_xuat, ke_hoach, ke_hoach_json
from tram.giao_viec.ke_hoach import digest_ke_hoach, doc_ke_hoach, duong_ke_hoach


def test_hop_le():
    kh, loi = doc_ke_hoach(ke_hoach_json(), "hr-f")
    assert loi == [] and [b.khoa for b in kh.bead] == ["t1", "t2"] and kh.bead[1].phu_thuoc == ["t1"]
    assert duong_ke_hoach("hr-f") == "docs/plans/hr-f.beads.json"


def test_digest_theo_noi_dung_khong_theo_dinh_dang():
    a = digest_ke_hoach(ke_hoach_json())
    assert a.startswith("sha256:") and a == digest_ke_hoach(json.dumps(ke_hoach(), ensure_ascii=True))
    sua = ke_hoach()
    sua["bead"][0]["uu_tien"] = 3
    assert digest_ke_hoach(json.dumps(sua)) != a


def b(**sua):
    return {"bead": [{**bead_de_xuat("t1"), **sua}]}


@pytest.mark.parametrize("sua", [
    {"feature": "hr-khac"}, {"bead": []}, {"bead": [bead_de_xuat(f"t{i}") for i in range(31)]},
    {"bead": [bead_de_xuat("t1"), bead_de_xuat("t1")]}, b(khoa="T1"), b(khoa="x" * 21), b(loai="feature"),
    b(loai="decision"), b(uu_tien=5), b(uu_tien="2"), b(uu_tien=True), b(tieu_de="x" * 201), b(tieu_de="--actor=x"),
    b(tieu_de="a\nb"), b(mo_ta="x" * 8001), b(nghiem_thu=""), b(nghiem_thu="  "), b(nghiem_thu="x" * 4001),
    b(nhan=["cot:ai-lam"]), b(nhan=["theo-plan"]), b(nhan=["tram:escalation"]), b(nhan=["co-do"]), b(nhan=["a,b"]),
    b(nhan=["cot-khoa"]), b(phu_thuoc=["t9"]), b(phu_thuoc=["t1"]), b(la=1),
    {"bead": [bead_de_xuat("t1", phu_thuoc=["t2"]), bead_de_xuat("t2", phu_thuoc=["t1"])]},
    {"spec_file": "../x.md"}, {"spec_file": "docs/../x.md"}, {"spec_file": "/docs/x.md"}, {"plan_file": "src/x.md"},
    {"plan_file": "docs/plans/x.txt"}, {"phien_ban": 2}, {"la": 1},
])
def test_sai_bi_tu_choi(sua):
    kh, loi = doc_ke_hoach(json.dumps(ke_hoach(**sua)), "hr-f")
    assert kh is None and loi


@pytest.mark.parametrize("van_ban", [None, "{hỏng", "[]", json.dumps(ke_hoach(ghi_chu="x" * 300_000))])
def test_khong_co_file_hoac_hong(van_ban):
    kh, loi = doc_ke_hoach(van_ban, "hr-f")
    assert kh is None and loi
