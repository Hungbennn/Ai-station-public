"""Tạo bead con từ plan đã duyệt (spec 4 §7.3) — G7: đúng cha, nhãn, phụ thuộc; không trùng khi làm lại hay crash."""
import json

import pytest

from bd_gia import BdGia
from bead_gia import bead
from feature_gia import ke_hoach
from tram.beads.bd import LoiBd
from tram.giao_viec.ke_hoach import KeHoachBead
from tram.thao_tac.tao_con import con_theo_khoa, noi_phu_thuoc, tao_con

KH = KeHoachBead.model_validate_json(json.dumps(ke_hoach()))


def g(*them, **kw):
    return BdGia([bead("hr-f", issue_type="feature", labels=["cho-duyet-spec"]), *them], **kw)


def test_tao_du_va_dung():
    bd = g()
    ids = tao_con(bd, "hr-f", KH)
    assert ids == {"t1": "hr-f.1", "t2": "hr-f.2"}
    t1, t2 = bd.beads["hr-f.1"], bd.beads["hr-f.2"]
    assert t1.description == "<!-- khoa: t1 -->\nLàm Task t1 của plan" and t1.labels == ("b2b",)
    assert (t2.parent, t2.priority, t2.acceptance_criteria, t2.issue_type) == ("hr-f", 1, "- Tiêu chí của t2", "task")
    assert noi_phu_thuoc(bd, KH, ids) == [["hr-f.2", "hr-f.1"]]
    assert [(p.depends_on_id, p.loai) for p in bd.beads["hr-f.2"].phu_thuoc][-1] == ("hr-f.1", "blocks")


def test_lam_lai_khong_tao_trung():
    bd = g()
    ids = tao_con(bd, "hr-f", KH)
    noi_phu_thuoc(bd, KH, ids)
    assert tao_con(bd, "hr-f", KH) == ids and noi_phu_thuoc(bd, KH, ids) == []
    assert bd.so_lan("tao") == 2 and bd.so_lan("them_phu_thuoc") == 1


def test_crash_sau_bd_create_doi_soat_theo_dong_khoa():
    bd = g(ra_loi_sau={"tao": 2})
    assert tao_con(bd, "hr-f", KH) == {"t1": "hr-f.1", "t2": "hr-f.2"} and bd.so_lan("tao") == 2


def test_loi_truoc_bd_create_thi_bao_loi_roi_lam_tiep():
    bd = g(ra_loi_truoc={"tao": 2})
    with pytest.raises(LoiBd):
        tao_con(bd, "hr-f", KH)
    assert tao_con(bd, "hr-f", KH) == {"t1": "hr-f.1", "t2": "hr-f.2"} and bd.so_lan("tao") == 2


def test_chi_nhan_dong_khoa_dau_mo_ta_cua_con_dung_cha():
    bd = g(bead("hr-x", parent="hr-khac", description="<!-- khoa: t1 -->\nx"),
           bead("hr-y", parent="hr-f", description="Ghi chú <!-- khoa: t1 -->"),
           bead("hr-f.9", parent="hr-f", description="<!-- khoa: t2 -->\ntạo tay từ trước"))
    assert set(con_theo_khoa(list(bd.beads.values()), "hr-f")) == {"t2"}
    ids = tao_con(bd, "hr-f", KH)
    assert ids["t2"] == "hr-f.9" and ids["t1"] not in ("hr-x", "hr-y") and bd.so_lan("tao") == 1
