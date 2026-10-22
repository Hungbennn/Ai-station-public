"""Luồng feature (spec 4 §5.1 "Bead feature", §6.6 "Với feature", §8 đợt sửa spec)."""
import pytest

from bead_gia import bead
from kho_phieu_gia import kho_tam
from su_kien_gia import ds, ket_thuc, nhan, sk
from test_phieu_yeu_cau import mo_ta
from tram.giao_viec.feature import buoc_feature, con_dot_spec, dem_tra_ve_dot, ly_do_khong_giao_spec
from tram.giao_viec.pipeline import TrangThaiBead

TT = TrangThaiBead(False, False, False, False, "sha256:d", False)
F = "hr-f"


@pytest.fixture
def kho(tmp_path):
    return kho_tam(tmp_path)


def spec_ket_thuc(kho, giao="g-1", luot=1, ket="xong", ly_do=None, commit="c1c1c1c"):
    nhan(kho, giao, luot, buoc="spec", bead_id=F)
    ket_thuc(kho, giao, luot, ket_thuc=ket, ly_do=ly_do, commit=commit if ket == "xong" else None, buoc="spec",
             bead_id=F)


@pytest.mark.parametrize("kw", [{"co_phieu": True}, {"bi_chan": True}, {"cong_viec_ton": True}])
def test_cho(kho, kw):
    spec_ket_thuc(kho)
    assert buoc_feature(ds(kho, F), TrangThaiBead(**{**TT.__dict__, **kw})) == "cho"


def test_chua_co_phieu_la_spec_xong_hop_le_la_chuyen_duyet(kho):
    assert buoc_feature(ds(kho, F), TT) == "spec"
    spec_ket_thuc(kho)
    assert buoc_feature(ds(kho, F), TT) == "chuyen_duyet"


@pytest.mark.parametrize("ket, ly_do", [("xong", "ke-hoach-loi"), ("xong", "spec-ngoai-docs"), ("bi", "agent"),
                                        ("thu_hoi", "mat-nhip"), ("het_han_muc", None)])
def test_luot_truoc_loi_hoac_dung_la_spec(kho, ket, ly_do):
    spec_ket_thuc(kho, ket=ket, ly_do=ly_do)
    assert buoc_feature(ds(kho, F), TT) == "spec"


def test_tra_ve_mo_vong_moi_khong_dung_spec_cu(kho):
    spec_ket_thuc(kho)
    sk(kho, "spec.tra_ve", {"gop_y": "Thiếu màn hình hoa hồng"}, bead_id=F)
    assert buoc_feature(ds(kho, F), TT) == "spec"
    spec_ket_thuc(kho, "g-2", 2, commit="c2c2c2c")
    assert buoc_feature(ds(kho, F), TT) == "chuyen_duyet"


def test_dot_sua_spec_dem_rieng_khong_bi_tra_ve_reset(kho):
    assert con_dot_spec(ds(kho, F))
    sk(kho, "spec.tra_ve", {"gop_y": "1"}, bead_id=F)
    sk(kho, "ngan_sach.chu_ky_moi", {"bead_id": F, "nguon_su_kien_id": 1}, bead_id=F)   # chu kỳ ngân sách khác đợt
    assert dem_tra_ve_dot(ds(kho, F)) == 1 and con_dot_spec(ds(kho, F))
    sk(kho, "spec.tra_ve", {"gop_y": "2"}, bead_id=F)
    assert dem_tra_ve_dot(ds(kho, F)) == 2 and not con_dot_spec(ds(kho, F))
    sk(kho, "ngan_sach.dot_spec_moi", {"bead_id": F, "nguon_su_kien_id": 9}, bead_id=F)
    assert dem_tra_ve_dot(ds(kho, F)) == 0 and con_dot_spec(ds(kho, F))


def f(**kw):
    kw.setdefault("labels", ["can-spec"])
    kw.setdefault("description", mo_ta())
    return bead(F, issue_type="feature", **kw)


def test_feature_du_dieu_kien():
    assert ly_do_khong_giao_spec(f(), {F}, "hr-codex") is None


@pytest.mark.parametrize("x, san, ly_do", [
    (bead(F, issue_type="task", labels=["can-spec"]), {F}, "loai-khong-giao"),
    (f(labels=["can-spec", "cot:ai-lam"]), {F}, "nhan-lech"), (f(labels=[]), {F}, "khong-can-spec"),
    (f(labels=["can-spec", "cho-duyet-spec"]), {F}, "khong-can-spec"),
    (f(labels=["can-spec", "theo-plan"]), {F}, "khong-can-spec"), (f(status="in_progress"), {F}, "trang-thai"),
    (f(), set(), "bi-chan"), (f(description="Không có phiếu"), {F}, "phieu-thieu"),
])
def test_feature_khong_du_dieu_kien(x, san, ly_do):
    assert ly_do_khong_giao_spec(x, san, "hr-codex") == ly_do


def test_phieu_cua_du_an_khac_la_phieu_thieu():
    assert ly_do_khong_giao_spec(f(), {F}, "khac") == "phieu-thieu"
