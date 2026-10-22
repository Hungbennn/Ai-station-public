"""`buoc_ke_tiep` — từng dòng của bảng spec 4 §6.6."""
import pytest

from kho_phieu_gia import kho_tam
from su_kien_gia import cong_bo, ds, ket_thuc, kiem, nhan, qc, sk
from tram.giao_viec.pipeline import TrangThaiBead, buoc_ke_tiep

TT = TrangThaiBead(False, False, False, False, "sha256:d", False)
C1, C2, Q1 = "c1c1c1c", "c2c2c2c", "d1d1d1d"


def tt(**kw):
    return TrangThaiBead(**{**TT.__dict__, **kw})


@pytest.fixture
def kho(tmp_path):
    return kho_tam(tmp_path)


def code_xong(kho, giao="g-1", luot=1, commit=C1, ly_do=None):
    nhan(kho, giao, luot)
    cong_bo(kho, luot, commit)
    ket_thuc(kho, giao, luot, ly_do=ly_do, commit=commit)


@pytest.mark.parametrize("kw", [{"co_phieu": True}, {"bi_chan": True}, {"cong_viec_ton": True},
                                {"cho_review": True}])
def test_dong_1_2_cho(kho, kw):
    code_xong(kho)
    assert buoc_ke_tiep(ds(kho), tt(**kw)) == "cho"


def test_chua_co_phieu_nao_la_code(kho):
    assert buoc_ke_tiep(ds(kho), TT) == "code"


def test_dong_5_xong_hop_le_chua_kiem_lai(kho):
    code_xong(kho)
    assert buoc_ke_tiep(ds(kho), TT) == "kiem_lai"


@pytest.mark.parametrize("ly_do", ["ban-giao-loi", "dong-file-cau-hinh", "commit-khong-cong-bo"])
def test_bao_xong_khong_hop_le_la_code(kho, ly_do):
    code_xong(kho, ly_do=ly_do)
    assert buoc_ke_tiep(ds(kho), TT) == "code"


@pytest.mark.parametrize("ket", ["bi", "thu_hoi", "het_han_muc"])
def test_phieu_cuoi_khong_xong_la_code(kho, ket):
    nhan(kho, "g-1", 1)
    ket_thuc(kho, "g-1", 1, ket_thuc=ket, ly_do="agent" if ket == "bi" else None)
    assert buoc_ke_tiep(ds(kho), TT) == "code"


def test_dong_4_kiem_dat_thi_qc_spike_thi_cot_3(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    assert buoc_ke_tiep(ds(kho), TT) == "qc" and buoc_ke_tiep(ds(kho), tt(la_spike=True)) == "cot_3"


def test_kiem_lai_khong_dat_la_code(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1, dat=False)
    assert buoc_ke_tiep(ds(kho), TT) == "code"


def test_dong_3_qc_dat_va_ref_bang_commit_qc(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    nhan(kho, "g-2", 2, buoc="qc")
    cong_bo(kho, 2, Q1)
    qc(kho, "g-2", C1, Q1)
    assert buoc_ke_tiep(ds(kho), TT) == "cot_3"


def test_qc_tra_ve_la_code_roi_vong_moi(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    qc(kho, "g-2", C1, Q1, ket_luan="tra_ve")
    assert buoc_ke_tiep(ds(kho), TT) == "code"
    code_xong(kho, "g-3", 3, C2)
    assert buoc_ke_tiep(ds(kho), TT) == "kiem_lai"
    kiem(kho, "g-3", C2, luot=3)
    assert buoc_ke_tiep(ds(kho), TT) == "qc"


def test_qc_khong_cong_nhan_la_code(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    qc(kho, "g-2", C1, Q1, ket_luan="khong_cong_nhan")
    assert buoc_ke_tiep(ds(kho), TT) == "code"


def test_push_moi_sau_qc_dat_bang_chung_het_hieu_luc(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    qc(kho, "g-2", C1, Q1)
    cong_bo(kho, 2, "eeeeeee")                     # ref công bố đổi sau QC
    assert buoc_ke_tiep(ds(kho), TT) == "code"


def test_tieu_chi_doi_sau_kiem_thi_het_hieu_luc(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    assert buoc_ke_tiep(ds(kho), tt(digest_tieu_chi="sha256:moi")) == "code"
    qc(kho, "g-2", C1, Q1)
    cong_bo(kho, 2, Q1)
    assert buoc_ke_tiep(ds(kho), tt(digest_tieu_chi="sha256:moi")) == "code"


def test_tra_ve_khong_tai_dung_kiem_lai_va_qc_cu(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    nhan(kho, "g-2", 2, buoc="qc")
    cong_bo(kho, 2, Q1)
    qc(kho, "g-2", C1, Q1)
    sk(kho, "cot.tra_ve", {"gop_y": "Thiếu ca 'ỷ'"})
    assert buoc_ke_tiep(ds(kho), TT) == "code"


def test_qc_bi_thu_hoi_thi_qc_lai(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    nhan(kho, "g-2", 2, buoc="qc")
    ket_thuc(kho, "g-2", 2, ket_thuc="thu_hoi", buoc="qc")
    assert buoc_ke_tiep(ds(kho), TT) == "qc"


def test_code_luot_moi_cung_sha_phai_kiem_lai(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    code_xong(kho, "g-3", 3, C1)
    assert buoc_ke_tiep(ds(kho), TT) == "kiem_lai"


def test_luot_code_loi_khong_dung_qc_cu(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    qc(kho, "g-2", C1, Q1)
    cong_bo(kho, 2, Q1)
    nhan(kho, "g-3", 3)
    ket_thuc(kho, "g-3", 3, ly_do="ban-giao-loi", commit=Q1)
    assert buoc_ke_tiep(ds(kho), TT) == "code"


def test_qc_vong_cu_khong_chan_qc_vong_moi_cung_sha(kho):
    code_xong(kho)
    kiem(kho, "g-1", C1)
    qc(kho, "g-2", C1, Q1, ket_luan="tra_ve")
    code_xong(kho, "g-3", 3, C1)
    kiem(kho, "g-3", C1, luot=3)
    assert buoc_ke_tiep(ds(kho), TT) == "qc"
